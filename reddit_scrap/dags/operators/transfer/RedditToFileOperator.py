import requests
import pandas as pd
import numpy as np

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from typing import Dict, Any, List


class RedditToFileOperator(BaseOperator):
    """This operator fetches Reddit posts via the Reddit API and saves them to a local file.

    Args:
        username (str): The username with which to authenticate in Reddit API
        password (str): The password with which to authenticate in Reddit API
        target_file (str): The local file in which to save the fetched reddit posts
        subreddit (str): From which subreddit to fetch the posts
        section (str): Posts from which section of the subreddit should be fetched - hot / trending / new
        limit (int): The number of posts to fetch per DAG run
        columns (List): List of properties to fetch about the posts. See Reddit API doc for details
    """

    template_fields = ["target_file"]
    ui_color = "#cc0000"

    @apply_defaults
    def __init__(
        self,
        username: str,
        password: str,
        target_file: str,
        subreddit: str,
        section: str,
        limit: int,
        columns: List,
        *args,
        **kwargs,
    ) -> None:
        super(RedditToFileOperator, self).__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.target_file = target_file
        self.subreddit = subreddit
        self.section = section
        self.limit = limit
        self.columns = columns

    def get_authentication(self) -> Dict[str, Any]:
        """Authenticate with reddit in order to use API

        Raises:
            RuntimeError: The API connection was not successful

        Returns:
            Dict[str, Any]: Authentication headers for POST request to Reddit API
        """
        auth = requests.auth.HTTPBasicAuth(
            "_mh0lD9wwQfuSr_JiUfKPQ", "dItOUj_QzYhLWlZVhEv6a-feaudvIQ"
        )

        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        headers = {"User-Agent": f"DataEngBot/0.0.1 by {self.username}"}

        res = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers,
        )

        if "error" in res.json():
            raise RuntimeError(f"Error in request: {res.json()['error']}")

        # Get access token from response
        token = res.json()["access_token"]

        # add authorization to headers dictionary
        return {**headers, **{"Authorization": f"bearer {token}"}}

    def extract_posts(
        self, headers: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Query the reddit API to receive posts in json format

        Args:
            headers (Dict[str, Any]): Authentication headers for POST request to Reddit API

        Returns:
            Dict[str, Any]: Extracted Reddit posts in JSON format
        """
        res = requests.get(
            f"https://oauth.reddit.com/r/{self.subreddit}/{self.section}",
            headers=headers,
            params={"limit": self.limit},
        )

        return res.json()

    def transform_posts(self, posts_json: Dict[str, Any]) -> pd.DataFrame:
        """Transform the loaded posts into a pd.DataFrame. Adds section and fetching timestamp automatically.

        Args:
            posts_json (Dict[str, Any]): Extracted Reddit posts in JSON format

        Returns:
            pd.DataFrame: Reddit posts in DataFrame format
        """
        # Fetch all columns if not stated otherwise
        df_raw = {k: [] for k in self.columns}

        for post in posts_json["data"]["children"]:
            for col in self.columns:
                df_raw[col].append(post["data"].get(col, "NULL"))

        posts_df = pd.DataFrame(df_raw)
        posts_df["section"] = self.section
        posts_df["added"] = np.datetime64("now", "s")

        return posts_df

    def execute(self, **kwargs) -> None:
        """Execute the operator
        """
        self.log.info("Starting...")
        header = self.get_authentication()

        self.log.info("Extracting posts...")
        posts_json = self.extract_posts(header)

        self.log.info("Transforming posts...")
        posts_df = self.transform_posts(posts_json)

        self.log.info("Saving posts to local filesystem...")
        posts_df.to_csv(
            self.target_file, sep="\t", index=False, header=False,
        )  # Tab separated since we upload files via pg_hook.bulk_insert
        self.log.info(f"Saved results to {self.target_file}")
