from airflow import DAG

# Airflow operators
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Airflow utils
from airflow.utils.dates import days_ago

# Python scripts for tasks
from reddit_scrap.utils.scrap_posts import scrap_posts
from reddit_scrap.utils.load_scrap_data import load_scrap_data
from reddit_scrap.utils.create_dashboard_images import create_dashboard_images

# Misc
from datetime import timedelta

template_searchpath = "/home/maurice/Dokumente/data-science-playground/reddit_scrap"

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email': ['email@emailprovider.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    "reddit_scrap",
    default_args=default_args,
    description="Scraps reddit hot page data once an hour",
    schedule_interval=timedelta(hours=1),
    template_searchpath=template_searchpath,
    start_date=days_ago(2),
    tags=["reddit_scrap"],
    catchup=False,
) as dag:

    py_section_scraps = [
        PythonOperator(
            task_id=f"scrap_posts_{section}",
            python_callable=scrap_posts,
            op_kwargs={"section": section, "limit": 50, "base_path": template_searchpath}
        )
        for section in ["hot", "top", "new"]
    ]

    create_reddit_posts_table = PostgresOperator(
        task_id="create_reddit_posts_table",
        postgres_conn_id="postgres_default",
        sql="sql/create_reddit_posts_table.sql"
    )

    py_load_scrap_data = PythonOperator(
        task_id="load_scrap_data",
        python_callable=load_scrap_data
    )

    create_agg_metrics_table = PostgresOperator(
        task_id="create_agg_metrics_table",
        postgres_conn_id="postgres_default",
        sql="sql/create_agg_metrics_table.sql"
    )

    compute_agg_metrics = PostgresOperator(
        task_id="compute_agg_metrics",
        postgres_conn_id="postgres_default",
        sql="sql/compute_agg_metrics.sql"
    )

    py_create_dashboard_images = PythonOperator(
        task_id="create_dashboard_images",
        python_callable=create_dashboard_images,
    )


    py_section_scraps >> create_reddit_posts_table >> py_load_scrap_data

    py_load_scrap_data >> create_agg_metrics_table >> compute_agg_metrics

    compute_agg_metrics >> py_create_dashboard_images