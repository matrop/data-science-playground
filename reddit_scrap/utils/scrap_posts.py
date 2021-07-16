import requests
import pandas as pd
import numpy as np
import os

from typing import Dict, Any


def get_authentication() -> Dict[str, Any]:
    """Authenticate with reddit in order to use API
    """
    auth = requests.auth.HTTPBasicAuth(
        '_mh0lD9wwQfuSr_JiUfKPQ',
        'dItOUj_QzYhLWlZVhEv6a-feaudvIQ')

    data = {
        "grant_type": "password",
        "username": "<username>",
        "password": "<password>",
    }

    headers = {"User-Agent": "DataEngBot/0.0.1 by <username>"}

    res = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=auth,
        data=data,
        headers=headers)

    if "error" in res.json():
        raise RuntimeError(f"Error in request: {res.json()['error']}")

    # Get access token from response
    token = res.json()["access_token"]

    # add authorization to headers dictionary
    return {**headers, **{'Authorization': f"bearer {token}"}}


def extract_posts(headers: Dict[str, Any], section: str, limit: int) -> Dict[str, Any]:
    """Query the reddit API to receive posts in json format
    """
    res = requests.get(
        f"https://oauth.reddit.com/r/popular/{section}",
        headers=headers,
        params={"limit": limit})

    return res.json()


def transform_posts(posts_json: Dict[str, Any], section: str) -> pd.DataFrame:
    """Transform the loaded posts into a pd.DataFrame, matching the schema of the Postgres table
    """
    columns = [
        "subreddit", "author", "upvote_ratio", "ups", "total_awards_received", "num_comments",
        "created",
    ]

    df_raw = {k: [] for k in columns}

    for post in posts_json["data"]["children"]:
        for col in columns:
            # Small hack to convert seconds (reddit API timestamp) to np timestamp
            if col == "created":
                post["data"][col] = np.datetime64(int(post["data"][col]), "s")

            df_raw[col].append(post["data"][col])

    posts_df = pd.DataFrame(df_raw)
    posts_df["section"] = section
    posts_df["added"] = np.datetime64("now", "s")

    return posts_df


def load_posts(posts_df: pd.DataFrame, section: str, base_path: str):
    """Extract the posts DataFrame into csv files
    """
    posts_df.to_csv(
        os.path.join(base_path, f"data/scrap_data_{section}.csv"),
        index=False
    )


def scrap_posts(**kwargs):
    """Scrap data from the reddit API, transform it and load it into csv files
    """
    headers = get_authentication()

    posts_json = extract_posts(headers, kwargs["section"], kwargs["limit"])
    posts_df = transform_posts(posts_json, kwargs["section"])
    load_posts(posts_df, kwargs["section"], kwargs["base_path"])