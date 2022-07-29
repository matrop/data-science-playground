from statistics import mean
from bs4 import BeautifulSoup
from typing import Dict, Any

import json
import re
import requests
import pandas as pd
import time
import os
import sqlalchemy


class R6Scrapper:
    def __init__(self):
        self.config = self.get_config()

    def get_config(self) -> Dict[str, Any]:
        with open(os.path.join("..", "config", "config.json"), "rb") as file:
            return json.load(file)

    def request_data(self, url: str, data: Dict[str, Any]) -> requests.Response:
        r = requests.get(url)

        if not r.ok:
            raise Exception(
                f"Failed to fetch html text (error {r.status_code}) | url = {url}, data = {data}, text = {r.text}")

        return r

    def scrap_stats(self, response: requests.Response) -> Dict[str, str]:
        bs = BeautifulSoup(response.text, "html.parser")

        overall_stats = {}
        divs = bs.find_all("div", {"class": "trn-card"})

        for div in divs:
            season_title = div.find(
                "h2", {"class": "trn-card__header-title"}).text

            if season_title in self.config["exclude_seasons"]:
                # Stats are not complete for these seasons
                continue

            season_div = [
                season_div
                for season_div in div.find_all("div", {"class": "r6-season"})
                if season_div.findChild("span").text in ["Ranked", "[EU] Ranked"]
            ][0]  # There can be more than one ranked stat per year

            player_name = re.findall(
                "(?<=- )(.*)(?= -)",
                bs.find("title").text)[0]

            try:
                stats = self.scrap_season_stats(
                    season_div, season_title, player_name)
            except RuntimeError as e:
                print(e)
                continue

            # Add to season data to multi-season table
            for key in stats:
                overall_stats[key] = overall_stats.get(key, []) + [stats[key]]

        return overall_stats

    def scrap_season_stats(self, season_div, season_title: str, player_name: str) -> Dict[str, Any]:
        stat_names = [entry.text for entry in season_div.find_all(
            "div", {"class": "trn-defstat__name"})]
        stat_values = [entry.text.strip(
            "/n").replace(",", "") for entry in season_div.find_all("div", {"class": "trn-defstat__value"})]
        stats = {k: v for k, v in list(zip(stat_names, stat_values))}

        # TODO: Define default values in JSON?
        for stat_name in ["K/D", "Kills/Match", "Kills", "Deaths"]:
            if stat_name not in stats:
                stats[stat_name] = -1

        # Number of matches
        n_matches = sum([int(stats[key])
                        for key in ["Wins", "Losses", "Abandons"]])
        if n_matches == "0":
            raise RuntimeError(
                f"Player did not play any matches in this season | season_title = {season_title}, player_name = {player_name}")

        stats["n_matches"] = n_matches
        stats["season_title"] = season_title
        stats["player"] = player_name

        return stats

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        for col_name, new_col_name, dtype in self.config["schema"]:
            df[new_col_name] = df[col_name].astype(dtype)
            df.drop(col_name, axis=1, inplace=True)

        df["timestamp"] = pd.Timestamp.now().isoformat()        
        df["deaths_per_match"] = round(df["deaths"] / df["matches_played"], 2)

        df = self.clean_kills_per_match(df)
        print("Cleaned data")

        return df

    def clean_kills_per_match(self, df: pd.DataFrame):
        mean_kpm = df["kills_per_match"].mean()
        std_kpm = df["kills_per_match"].std()

        upper_bound = mean_kpm + 3 * std_kpm
        lower_bound = 0

        dirty_indices = df[(df["kills_per_match"] > upper_bound) | (df["kills_per_match"] < lower_bound)].index
        return df.drop(dirty_indices, inplace=False)

    def run(self):
        overall_stats = {}

        for player in self.config["players"]:
            url = f"https://r6.tracker.network/profile/psn/{player}/seasons"

            response = self.request_data(url, self.config["request_data"])
            try:
                stats = self.scrap_stats(response)
            except RuntimeError as e:
                print(f"Exception occured | {e}")
                continue

            for key in stats:
                overall_stats[key] = overall_stats.get(key, []) + stats[key]

            print(f"Fetched {player}")

            # To avoid being blocked b/c too many requests
            time.sleep(self.config["request_delay_sec"])

        raw_df = pd.DataFrame(overall_stats)
        cleaned_df = self.clean_data(raw_df)

        engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}")

        with engine.connect() as con:
            cleaned_df.to_sql("data", con=con, schema="core", if_exists="replace", index=False)
        
        print("Saved data to database")
