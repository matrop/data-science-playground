SELECT
    subreddit :: VARCHAR AS "subreddit",
    upvote_ratio :: REAL AS "upvote_ratio",
    ups :: INTEGER AS "upvotes",
    -- to_timestamp(created) :: TIMESTAMP AS "creation_ts",
    id :: VARCHAR AS "post_id",
    is_video :: BOOLEAN AS "is_video",
    added :: TIMESTAMP AS "elt_ts"
FROM
    {{ source('reddit_raw', 'popular_hot_posts') }}