-- SQLite views for the Social Media Content Performance Analytics project.
-- Run through scripts/build_sqlite_db.py after loading CSV files.

DROP VIEW IF EXISTS v_post_performance;
DROP VIEW IF EXISTS v_posting_time_performance;
DROP VIEW IF EXISTS v_campaign_roi;
DROP VIEW IF EXISTS v_follower_growth_monthly;
DROP VIEW IF EXISTS v_ab_test_results;

CREATE VIEW v_post_performance AS
SELECT
    platform,
    content_category,
    content_type,
    COUNT(*) AS posts,
    SUM(impressions) AS impressions,
    SUM(reach) AS reach,
    SUM(likes + comments + shares + saves) AS engagements,
    SUM(clicks) AS clicks,
    ROUND(1.0 * SUM(likes + comments + shares + saves) / NULLIF(SUM(impressions), 0), 6) AS engagement_rate,
    ROUND(1.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 6) AS ctr
FROM posts
GROUP BY platform, content_category, content_type;

CREATE VIEW v_posting_time_performance AS
SELECT
    weekday_name,
    post_hour,
    posting_time_bucket,
    COUNT(*) AS posts,
    SUM(impressions) AS impressions,
    SUM(likes + comments + shares + saves) AS engagements,
    SUM(clicks) AS clicks,
    ROUND(1.0 * SUM(likes + comments + shares + saves) / NULLIF(SUM(impressions), 0), 6) AS engagement_rate,
    ROUND(1.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 6) AS ctr
FROM posts
GROUP BY weekday_name, post_hour, posting_time_bucket;

CREATE VIEW v_campaign_roi AS
SELECT
    campaign_id,
    campaign_name,
    campaign_type,
    platform,
    objective,
    content_category_focus,
    start_date,
    end_date,
    spend,
    revenue,
    conversions,
    impressions,
    clicks,
    ROUND((revenue - spend) / NULLIF(spend, 0), 6) AS calculated_roi,
    ROUND(revenue / NULLIF(spend, 0), 6) AS calculated_roas,
    ROUND(1.0 * conversions / NULLIF(clicks, 0), 6) AS conversion_rate,
    ROUND(spend / NULLIF(conversions, 0), 2) AS cost_per_conversion
FROM campaigns
WHERE campaign_type = 'Paid';

CREATE VIEW v_follower_growth_monthly AS
SELECT
    substr(date, 1, 7) AS year_month,
    platform,
    MIN(followers) AS starting_followers,
    MAX(followers) AS ending_followers,
    SUM(new_followers) AS new_followers,
    SUM(lost_followers) AS lost_followers,
    SUM(net_growth) AS net_growth,
    ROUND(1.0 * (MAX(followers) - MIN(followers)) / NULLIF(MIN(followers), 0), 6) AS follower_growth_rate
FROM followers_daily
GROUP BY substr(date, 1, 7), platform;

CREATE VIEW v_ab_test_results AS
SELECT
    test_id,
    test_name,
    campaign_id,
    campaign_name,
    platform,
    content_category,
    variant,
    variant_description,
    impressions,
    clicks,
    conversions,
    engagements,
    ROUND(1.0 * engagements / NULLIF(impressions, 0), 6) AS engagement_rate,
    ROUND(1.0 * clicks / NULLIF(impressions, 0), 6) AS ctr,
    ROUND(1.0 * conversions / NULLIF(clicks, 0), 6) AS conversion_rate,
    is_winner,
    winner
FROM ab_tests;
