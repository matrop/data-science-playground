For reddit_scrap I created a ETL pipeline using Apache Airflow and PostgreSQL. The pipeline works like this:

1. Fetch posts from the reddit popular page. Fetch posts from each "top", "hot" and "new" sections

2. Save the fetched posts locally into csv files

3. Load the data from the csv files into a newly create database table

4. Compute some aggregations on the data and write these into a new table

5. Fetch the aggregations and produce plots out of them

![DAG overview](./dag.png?raw=true "DAG Overview")

Of course the pipeline could be upgrade quite extensively. One of the main points would be a central config file (JSON, YAML, etc.) to manage parameters (e.g. number of posts, subreddit, ...) and paths. Another point would be to perform data quality checks, either when the csv files are imported to the database or when they are still files. Ultimately, this would have to be built up into a stage-check-exchange pattern.
