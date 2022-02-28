import os

from dotenv import load_dotenv, find_dotenv

from airflow import DAG
from airflow.models import Variable, Connection
from airflow import settings

# Airflow operators
from airflow.operators.python import PythonOperator

from datetime import timedelta, datetime

# Load environment variables
load_dotenv(os.path.join("/opt", "airflow", "dags", "config", ".env"))

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
    "setup_env",
    default_args=default_args,
    description="Scraps reddit hot page data",
    schedule_interval="@once",
    start_date=datetime(2022, 2, 28),
    tags=[""],
    catchup=False,
) as dag:
    def set_reddit_variables():
        Variable.set(
            key="reddit_username",
            value=os.environ.get("REDDIT_USERNAME")
        )

        Variable.set(
            key="reddit_password_secret",
            value=os.environ.get("REDDIT_PASSWORD")
        )

    setup_reddit_variables = PythonOperator(
        task_id="setup_reddit_variables",
        python_callable=set_reddit_variables,
    )

    def set_pg_conn():
        conn = Connection(
                conn_id="pg_database",
                conn_type="postgres",
                host="postgres",
                login="airflow",
                password="airflow",
                port=5432
        ) #create a connection object

        session = settings.Session() 
        session.add(conn)
        session.commit()

    setup_pg_conn = PythonOperator(
        task_id="setup_pg_conn",
        python_callable=set_pg_conn,
    )

    setup_reddit_variables >> setup_pg_conn

    # RedditToFile operator that uses utils file to load reddit data to local storage

    # FileToPostgres operator to load files into Postgres

    # dbt usage in postgres to transform data?
