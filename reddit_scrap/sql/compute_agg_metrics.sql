INSERT INTO agg_metrics
SELECT section, added, COUNT(DISTINCT subreddit), SUM(ups), AVG(upvote_ratio),SUM(total_awards_received), SUM(num_comments)
FROM reddit_posts
GROUP BY section, added;

