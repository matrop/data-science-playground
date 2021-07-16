DROP TABLE IF EXISTS reddit_posts;
CREATE TABLE reddit_posts (
    subreddit VARCHAR(30),
    author VARCHAR(30),
    upvote_ratio FLOAT,
    ups INT,
    total_awards_received INT,
    num_comments INT,
    created TIMESTAMP,
    added TIMESTAMP,
    section VARCHAR(3),
    id SERIAL PRIMARY KEY
);
