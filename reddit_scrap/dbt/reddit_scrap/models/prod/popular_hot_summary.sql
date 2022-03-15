SELECT
    subreddit,
    COUNT(*) AS non_unique_post_count,
    COUNT(DISTINCT post_id) AS unique_post_count,
    AVG(upvote_ratio) AS mean_upvote_ratio,
    ROUND(AVG(upvotes), 2) AS mean_upvotes
FROM
    {{ ref('base_popular_hot_posts') }}
GROUP BY
    subreddit
ORDER BY
    COUNT(*) DESC