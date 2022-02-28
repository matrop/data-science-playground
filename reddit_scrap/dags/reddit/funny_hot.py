import os
import json
import numpy as np
import logging

from airflow import DAG
from airflow.models import Variable

# Airflow operators
from airflow.providers.postgres.operators.postgres import PostgresOperator
from dags.operators.transfer.FileToPostgresOperator import FileToPostgresOperator
from operators.transfer.RedditToFileOperator import RedditToFileOperator

# Misc
from datetime import datetime, timedelta

filename_wo_ext = os.path.basename(__file__)[:-3]
with open(f"/opt/airflow/dags/reddit/config/{filename_wo_ext}.json", "r") as conf_file:
    dag_config = json.load(conf_file)

default_args = {
    "owner": "admin",
    "depends_on_past": False,
    "email": ["email@emailprovider.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    f"reddit_fetch__{dag_config['subreddit']}_{dag_config['section']}",
    default_args=default_args,
    description=dag_config["description"],
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2022, 2, 28),
    tags=[""],
    catchup=False,
) as dag:
    dag.doc_md=f"""Fetch posts from the '{dag_config['section']}' section of the '{dag_config['subreddit']}' subreddit 
    and load it into the table '{dag_config['schema']}.{dag_config['table']}' in Postgres"""

    reddit_to_file = RedditToFileOperator(
        task_id="reddit_to_file",
        username=Variable.get("reddit_username"),
        password=Variable.get("reddit_password_secret"),
        subreddit=dag_config["subreddit"],
        section=dag_config["section"],
        limit=dag_config["limit"],
        columns=dag_config["columns"],
        target_file=os.path.join(
            "/opt",
            "airflow",
            "tmp",
            f"{dag_config['subreddit']}_{dag_config['section']}_" + "{{ts_nodash}}.csv",
        ),
    )

    create_table_if_nexists = PostgresOperator(
        task_id="create_table_if_nexists",
        postgres_conn_id="pg_database",
        sql=f"""
            CREATE TABLE IF NOT EXISTS {dag_config["schema"]}.{dag_config["table"]} (
                {",".join([
                    f'"{key}" {dag_config["columns"][key]["sql"]}' for key in dag_config['columns']
                ])}
            )
        """,
    )

    file_to_postgres = FileToPostgresOperator(
        task_id="file_to_postgres",
        source_file=os.path.join(
            "/opt",
            "airflow",
            "tmp",
            f"{dag_config['subreddit']}_{dag_config['section']}_" + "{{ts_nodash}}.csv",
        ),
        target_table=f"{dag_config['schema']}.{dag_config['table']}",
        postgres_conn_id="pg_database",
    )

    reddit_to_file >> create_table_if_nexists >> file_to_postgres
