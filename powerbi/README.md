# Power BI Dashboard Build Kit

This folder contains the copy-ready assets for building the Power BI report from the processed CSV files in `data/processed`.

## Recommended Build Flow

1. Open Power BI Desktop.
2. Select `Get data > Text/CSV` and import these files:
   - `posts.csv`
   - `campaigns.csv`
   - `followers_daily.csv`
   - `ab_tests.csv`
   - `date_table.csv`
   - `platforms.csv`
3. Keep the default table names from the file names: `posts`, `campaigns`, `followers_daily`, `ab_tests`, `date_table`, and `platforms`.
4. Set the data types listed below, or paste the M query bodies from `power_query_template.pq` into Power Query Advanced Editor.
5. Create the model relationships from the relationship table below.
6. Paste the measures from `measures.dax` into Power BI.
7. Import `social_media_theme.json` from `View > Themes > Browse for themes`.
8. Build the six report pages using `dashboard_pages.md`.

## Data Types

Use these core data types if importing manually:

| Table | Date fields | Whole numbers | Decimal/currency/rate fields | Logical fields |
| --- | --- | --- | --- | --- |
| `posts` | `post_datetime`, `post_date` | `post_hour`, `hashtag_count`, `content_length`, `impressions`, `reach`, `likes`, `comments`, `shares`, `saves`, `clicks` | `engagement_rate`, `ctr` | `has_media`, `is_verified` |
| `campaigns` | `start_date`, `end_date` | `impressions`, `clicks`, `conversions` | `spend`, `revenue`, `roi`, `roas` | none |
| `followers_daily` | `date` | `followers`, `new_followers`, `lost_followers`, `net_growth` | `follower_growth_rate` | none |
| `ab_tests` | `start_date`, `end_date` | `impressions`, `clicks`, `conversions`, `engagements` | `engagement_rate`, `ctr`, `conversion_rate` | `is_winner` |
| `date_table` | `date`, `month_start` | `year`, `month_number`, `weekday_number` | none | `is_weekend` |
| `platforms` | none | `starting_followers`, `kaggle_post_rows` | none | none |

Format rate fields as percentages in the report view. Format `spend` and `revenue` as currency.

## Relationships

Create a clean star-style model with dimensions filtering facts. Keep cross filter direction as `Single`.

| From table | From column | To table | To column | Cardinality | Active |
| --- | --- | --- | --- | --- | --- |
| `date_table` | `date` | `posts` | `post_date` | One-to-many | Yes |
| `date_table` | `date` | `followers_daily` | `date` | One-to-many | Yes |
| `date_table` | `date` | `campaigns` | `start_date` | One-to-many | Yes |
| `date_table` | `date` | `ab_tests` | `start_date` | One-to-many | Yes |
| `platforms` | `platform` | `posts` | `platform` | One-to-many | Yes |
| `platforms` | `platform` | `followers_daily` | `platform` | One-to-many | Yes |
| `platforms` | `platform` | `campaigns` | `platform` | One-to-many | Yes |
| `platforms` | `platform` | `ab_tests` | `platform` | One-to-many | Yes |

Do not create active relationships between fact tables such as `campaigns` to `posts`. The common `date_table` and `platforms` dimensions keep filtering predictable.

## Dashboard Scope

The report answers:

- Which platforms and content categories drive the strongest engagement?
- What posting days and hours perform best?
- How are followers growing by platform?
- Which campaigns deliver the highest ROI and ROAS?
- Which A/B test variants win on conversion rate, CTR, and engagement?

Validated data profile:

- Date range: 2024-01-01 to 2025-12-31
- Posts: 4,016
- Total impressions: 514,925,953
- Total reach: 385,622,153
- Total engagements: 42,170,185
- Total clicks: 8,083,542
- Overall engagement rate: 8.19%
- Overall CTR: 1.57%
- Paid campaign spend: 1,423,084.41
- Paid campaign revenue: 3,309,632.61
- Paid ROAS: 2.33
- A/B tests: 18 tests, 36 variants

## Free Hosting and Sharing Options

As of 2026-06-19, the practical free paths are:

1. **Build locally with Power BI Desktop.** Power BI Desktop is free and is the best no-cost authoring option.
2. **Use Power BI service My Workspace for personal viewing.** A free license can create content in My Workspace, but cannot share privately with other users in a normal workspace.
3. **Use Publish to web only if public data is acceptable.** Viewers do not need Power BI accounts, but the report and underlying detail-level data become public on the internet. Your tenant admin also has to allow the feature.
4. **For private sharing, expect Pro/PPU or Premium/Fabric capacity.** Free viewers can consume shared content only when the report and semantic model are hosted in eligible Premium/Fabric capacity.
5. **For a portfolio submission with no paid license, share the `.pbix`, screenshots, PDF export, or a short screen recording.** That is usually the safest free option for student/project review.

Microsoft references:

- Power BI Desktop: https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop
- Publish to web: https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-publish-to-web
- License capabilities: https://learn.microsoft.com/en-us/power-bi/fundamentals/end-user-license
