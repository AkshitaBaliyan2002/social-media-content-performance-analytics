# Social Media Content Performance Analytics

Power BI analytics project for evaluating social media content performance, posting-time effectiveness, follower growth, campaign ROI, and A/B test outcomes across major platforms.

## Project Overview

The project analyzes multi-platform social media performance using a Kaggle-backed dataset enriched with campaign and business metrics for dashboard analysis.

Key questions answered:

- Which platforms and content categories drive the strongest engagement?
- What posting days and hours perform best?
- How are followers growing by platform?
- Which campaigns deliver the highest ROI and ROAS?
- Which A/B test variants perform best?

## Tools Used

- Python for data preparation and validation
- Kaggle public dataset via `kagglehub`
- Power BI Desktop for dashboarding
- CSV files as the reporting data layer

## Data Source

Primary dataset:

- [Social Media Engagement Dataset](https://www.kaggle.com/datasets/aviral342/social-media-engagement-dataset)

The dataset provides post-level fields such as timestamp, platform, content type, category, likes, comments, shares, views, saves, follower count, posting hour, sentiment, influencer tier, media flag, and verified status.

The preparation script filters the data to:

- Instagram
- YouTube
- TikTok
- LinkedIn
- X/Twitter

Additional dashboard fields are modeled for analysis completeness, including reach, clicks, campaign assignment, spend, revenue, ROI, ROAS, daily follower movement, and A/B test outcomes.

## Dashboard Pages

The Power BI dashboard is designed around six report pages:

- Executive Overview
- Content Performance
- Posting Time Analysis
- Follower Growth
- Campaign ROI
- A/B Testing

## Key Metrics

- Impressions
- Reach
- Likes, comments, shares, and saves
- Engagement rate
- Click-through rate
- Follower growth rate
- Campaign spend and revenue
- ROI and ROAS
- Conversion rate
- A/B test winner

## Repository Structure

```text
.
├── data/
│   └── processed/
│       ├── ab_tests.csv
│       ├── campaigns.csv
│       ├── date_table.csv
│       ├── followers_daily.csv
│       ├── platforms.csv
│       ├── posts.csv
│       └── source_manifest.csv
├── scripts/
│   ├── prepare_kaggle_social_media_data.py
│   └── validate_data.py
├── requirements.txt
└── README.md
```

## Reproduce the Dataset

```bash
python3 -m pip install -r requirements.txt
python3 scripts/prepare_kaggle_social_media_data.py
python3 scripts/validate_data.py
```

## Validation

The validation script checks:

- Expected CSV files are present
- Required columns exist
- IDs are unique where required
- No blank platform, category, or date fields
- Engagement rate, CTR, ROI, ROAS, and conversion rate calculations are valid
- Each A/B test has exactly one winner

Current processed dataset:

- `posts.csv`: 4,016 rows
- `campaigns.csv`: 55 rows
- `followers_daily.csv`: 3,655 rows
- `ab_tests.csv`: 36 rows
- `date_table.csv`: 731 rows
- `platforms.csv`: 5 rows

