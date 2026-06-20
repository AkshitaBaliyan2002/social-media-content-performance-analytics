# Dashboard Pages

Build the report in 16:9 canvas format. Use slicers for `platforms[platform]`, `date_table[year]`, `date_table[quarter]`, `posts[content_category]`, and `posts[content_type]` where relevant.

## 1. Executive Overview

Purpose: show whether the social program is growing efficiently.

Top KPI cards:

- `[Total Impressions]`
- `[Total Reach]`
- `[Total Engagements]`
- `[Engagement Rate]`
- `[Overall CTR]`
- `[Latest Followers]`
- `[Paid Revenue]`
- `[Campaign ROI]`
- `[ROAS]`

Main visuals:

- Line chart: `date_table[month_start]` by `[Total Impressions]` and `[Total Engagements]`
- Clustered column chart: `platforms[platform]` by `[Engagement Rate]`, `[Overall CTR]`
- Donut chart: `platforms[platform]` by `[Total Impressions]`
- Table: `platforms[platform]`, `[Total Posts]`, `[Total Impressions]`, `[Engagement Rate]`, `[Overall CTR]`, `[Latest Followers]`, `[ROAS]`

Design notes:

- Put platform and year slicers in the header.
- Use green conditional formatting for ROI and ROAS values above target.
- Add a small text box: `Social Media Content Performance Analytics | 2024-2025`.

## 2. Content Performance

Purpose: compare what content themes and formats perform best.

Main visuals:

- Bar chart: `posts[content_category]` by `[Engagement Rate]`
- Bar chart: `posts[content_type]` by `[Total Engagements]`
- Matrix: rows `posts[content_category]`, columns `platforms[platform]`, values `[Engagement Rate]`, `[Overall CTR]`, `[Total Impressions]`
- Scatter chart: x `[Total Impressions]`, y `[Engagement Rate]`, size `[Total Clicks]`, legend `posts[content_type]`
- Table: `posts[post_id]`, `posts[platform]`, `posts[content_category]`, `posts[content_type]`, `[Total Impressions]`, `[Total Engagements]`, `[Engagement Rate]`, `[Overall CTR]`

Suggested filters:

- Top N table filter: top 25 posts by `[Total Engagements]`
- Page slicers: content category, content type, sentiment, influencer tier

## 3. Posting Time Analysis

Purpose: find the best days and hours for publishing.

Main visuals:

- Matrix heatmap: rows `date_table[weekday_name]`, columns `posts[post_hour]`, values `[Engagement Rate]`
- Line chart: `posts[post_hour]` by `[Engagement Rate]`, `[Overall CTR]`
- Bar chart: `posts[posting_time_bucket]` by `[Total Engagements]`
- Card: `[Best Posting Hour]`
- Card: `[Best Posting Bucket]`
- Card: `[Best Weekday]`

Sorting:

- Sort `date_table[weekday_name]` by `date_table[weekday_number]`.
- Sort `date_table[month_name]` by `date_table[month_number]`.

Conditional formatting:

- For the heatmap, apply background color to `[Engagement Rate]`.
- Keep a neutral low color and strong green high color.

## 4. Follower Growth

Purpose: show community growth and churn by platform.

Top KPI cards:

- `[Latest Followers]`
- `[Followers Start]`
- `[Followers End]`
- `[Follower Net Growth]`
- `[Follower Growth %]`
- `[Average Daily Net Growth]`

Main visuals:

- Line chart: `date_table[date]` by `[Latest Followers]`, legend `platforms[platform]`
- Stacked column chart: `date_table[month_start]` by `[New Followers]` and `[Lost Followers]`
- Column chart: `platforms[platform]` by `[Follower Net Growth]`
- Table: `platforms[platform]`, `[Followers Start]`, `[Followers End]`, `[Follower Net Growth]`, `[Follower Growth %]`

## 5. Campaign ROI

Purpose: evaluate paid campaign efficiency and revenue return.

Page filter:

- `campaigns[campaign_type] = Paid`

Top KPI cards:

- `[Paid Spend]`
- `[Paid Revenue]`
- `[Campaign ROI]`
- `[ROAS]`
- `[Campaign Conversions]`
- `[Cost per Conversion]`

Main visuals:

- Clustered bar chart: `campaigns[campaign_name]` by `[ROAS]`
- Scatter chart: x `[Paid Spend]`, y `[Paid Revenue]`, size `[Campaign Conversions]`, legend `platforms[platform]`
- Matrix: rows `platforms[platform]`, columns `campaigns[objective]`, values `[Paid Spend]`, `[Paid Revenue]`, `[ROAS]`, `[Campaign ROI]`
- Table: `campaigns[campaign_name]`, `campaigns[platform]`, `campaigns[objective]`, `[Paid Spend]`, `[Paid Revenue]`, `[Campaign ROI]`, `[ROAS]`, `[Cost per Conversion]`

Suggested conditional formatting:

- ROAS under 1.0: red
- ROAS from 1.0 to 2.0: amber
- ROAS above 2.0: green

## 6. A/B Testing

Purpose: compare variants and identify winners.

Top KPI cards:

- `[A/B Tests]`
- `[A/B Variants]`
- `[A/B Winner Rows]`
- `[A/B Conversion Rate]`
- `[A/B CTR]`
- `[A/B Engagement Rate]`

Main visuals:

- Clustered column chart: `ab_tests[variant]` by `[A/B Conversion Rate]`, small multiples by `ab_tests[test_name]`
- Clustered bar chart: `ab_tests[variant]` by `[A/B CTR]`
- Matrix: rows `ab_tests[test_name]`, `ab_tests[variant]`; values `[A/B Impressions]`, `[A/B Clicks]`, `[A/B Conversions]`, `[A/B Conversion Rate]`, `[A/B Variant Lift vs A]`
- Donut chart: `ab_tests[variant]` by `[A/B Winner Rows]`
- Table: `ab_tests[test_name]`, `ab_tests[platform]`, `ab_tests[variant]`, `ab_tests[winner]`, `[A/B Conversion Rate]`, `[A/B Variant Lift vs A]`

Suggested filters:

- `ab_tests[winner]`
- `ab_tests[content_category]`
- `platforms[platform]`
