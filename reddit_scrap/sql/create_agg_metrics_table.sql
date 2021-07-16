DROP TABLE IF EXISTS agg_metrics;
CREATE TABLE agg_metrics (
    section VARCHAR(3) PRIMARY KEY,
    added TIMESTAMP,
    n_subreddits INT,
    sum_ups INT,
    avg_upvote_ratio FLOAT,
    sum_awards INT,
    sum_num_comments INT
);
