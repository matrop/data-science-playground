import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import reddit_scrap.utils.db_utils as db_utils


sns.set(rc={"figure.figsize": (13, 6)})


def create_dashboard_images():
    """Query data from agg_metrics Postgres table and build barplots from it. Saves the plots to png
    files.
    """
    with db_utils.get_con() as con:
        df = pd.read_sql("agg_metrics", con=con)

    added = df.added.max()  # Latest date of the scraps will be in the plot titles

    for col in df.columns[2:]:  # Exclude "section", "added" column
        plt.title(f"Comparisson of {col} between reddit popular sections at {added}", fontsize=16)
        g = sns.barplot(data=df, x="section", y=col)

        # Annotate bars
        for index, row in df.iterrows():
            g.text(row.name, row[col]+0.01, round(row[col], 2), color='black', ha="center")

        plt.savefig(f"/home/maurice/Dokumente/data-science-playground/reddit_scrap/imgs/{col}.png")
        plt.close()
