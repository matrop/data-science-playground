import pandas as pd
import reddit_scrap.utils.db_utils as db_utils


def load_scrap_data():
    """Loads exported post data from csv files into the database
    """
    with db_utils.get_con() as con:
        for section in ["hot", "top", "new"]:
            df = pd.read_csv(f"/home/maurice/Dokumente/data-science-playground/reddit_scrap/data/scrap_data_{section}.csv")
            df.to_sql("reddit_posts", if_exists="append", index=False, con=con)