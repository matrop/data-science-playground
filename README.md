# data-science-playground
A series of data-related projects aimed at gaining new skills and having fun. If you have advice on how to improve things, feel free to open an issue. I cannot promise to implement it but it's nice to know what can be improved. 

## Project List

1. Reddit Scrap

A take on data engineering with the Reddit API, mainly using Apache Airflow and PostgreSQL. The goal of this project was to get familiar with ELT pipelines and using APIs to fetch data from the web.
To run it, use `docker-compose`. You will get DAG import errors until you've run the `setup_environment` DAG.
