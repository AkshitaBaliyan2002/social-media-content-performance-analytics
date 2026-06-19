#!/usr/bin/env python3
"""Prepare Kaggle-backed social media analytics data for Power BI."""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median


DEFAULT_SEED = 20250619
SOURCE_HANDLE = "aviral342/social-media-engagement-dataset"
SOURCE_FILE = "social_media_engagement_dataset.csv"
SOURCE_URL = "https://www.kaggle.com/datasets/aviral342/social-media-engagement-dataset"

PLATFORM_MAP = {
    "Instagram": "Instagram",
    "YouTube": "YouTube",
    "TikTok": "TikTok",
    "LinkedIn": "LinkedIn",
    "Twitter": "X/Twitter",
}

PLATFORM_CONFIG = {
    "Instagram": {
        "slug": "instagram",
        "base_ctr": 0.013,
        "daily_growth_rate": 0.0014,
        "daily_churn_rate": 0.00045,
        "cpm": 8.5,
        "conversion_rate": 0.030,
        "primary_goal": "Visual community growth and lifestyle engagement",
    },
    "YouTube": {
        "slug": "youtube",
        "base_ctr": 0.018,
        "daily_growth_rate": 0.0011,
        "daily_churn_rate": 0.00025,
        "cpm": 10.0,
        "conversion_rate": 0.025,
        "primary_goal": "Video discovery and subscriber growth",
    },
    "TikTok": {
        "slug": "tiktok",
        "base_ctr": 0.011,
        "daily_growth_rate": 0.0018,
        "daily_churn_rate": 0.00050,
        "cpm": 7.5,
        "conversion_rate": 0.022,
        "primary_goal": "Short-form reach and viral growth",
    },
    "LinkedIn": {
        "slug": "linkedin",
        "base_ctr": 0.022,
        "daily_growth_rate": 0.0009,
        "daily_churn_rate": 0.00018,
        "cpm": 18.0,
        "conversion_rate": 0.045,
        "primary_goal": "B2B awareness and lead quality",
    },
    "X/Twitter": {
        "slug": "x-twitter",
        "base_ctr": 0.015,
        "daily_growth_rate": 0.0007,
        "daily_churn_rate": 0.00035,
        "cpm": 6.5,
        "conversion_rate": 0.020,
        "primary_goal": "Conversation, news, and community response",
    },
}

CAMPAIGN_TEMPLATES = [
    ("Q1 Awareness Sprint", "Awareness", "Education", 1, 10, 2, 28, (0.9, 1.8)),
    ("Spring Product Launch", "Product Launch", "Technology", 3, 5, 4, 30, (1.5, 3.2)),
    ("Summer Creator Push", "Engagement", "Entertainment", 6, 1, 7, 31, (1.1, 2.6)),
    ("Back to School Offer", "Conversion", "Business", 8, 10, 9, 25, (1.8, 4.0)),
    ("Holiday Revenue Campaign", "Revenue", "Fashion", 11, 1, 12, 20, (2.2, 5.0)),
]

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def daterange(start_date: date, end_date: date) -> list[date]:
    days = []
    current = start_date
    while current <= end_date:
        days.append(current)
        current += timedelta(days=1)
    return days


def money(value: float) -> str:
    return f"{value:.2f}"


def rate(value: float) -> str:
    return f"{value:.6f}"


def platform_id(platform: str) -> str:
    return PLATFORM_CONFIG[platform]["slug"].upper().replace("-", "_")


def clean_int(value: str) -> int:
    return int(float(value.replace(",", "").strip()))


def clean_bool(value: str) -> str:
    return "TRUE" if value.strip().lower() == "true" else "FALSE"


def posting_time_bucket(hour: int) -> str:
    if 5 <= hour < 12:
        return "Morning"
    if 12 <= hour < 17:
        return "Afternoon"
    if 17 <= hour < 22:
        return "Evening"
    return "Late Night"


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def resolve_source_csv(source_csv: str | None) -> Path:
    if source_csv:
        path = Path(source_csv)
        if not path.exists():
            raise FileNotFoundError(f"Source CSV does not exist: {path}")
        return path

    try:
        import kagglehub
    except ImportError as exc:
        raise SystemExit(
            "kagglehub is required to download the Kaggle dataset. "
            "Run: python3 -m pip install -r requirements.txt"
        ) from exc

    dataset_dir = Path(kagglehub.dataset_download(SOURCE_HANDLE))
    source_path = dataset_dir / SOURCE_FILE
    if not source_path.exists():
        matches = list(dataset_dir.glob("*.csv"))
        raise FileNotFoundError(f"Expected {SOURCE_FILE} in {dataset_dir}. Found: {matches}")
    return source_path


def read_kaggle_rows(source_csv: Path) -> list[dict[str, str]]:
    rows = []
    with source_csv.open(newline="", encoding="utf-8-sig") as csv_file:
        for row in csv.DictReader(csv_file):
            source_platform = row["Platform"]
            if source_platform not in PLATFORM_MAP:
                continue
            row["normalized_platform"] = PLATFORM_MAP[source_platform]
            rows.append(row)
    rows.sort(key=lambda row: (row["Timestamp"], row["Post_ID"]))
    return rows


def build_campaign_shells(years: list[int]) -> tuple[list[dict[str, object]], dict[str, list[dict[str, object]]]]:
    campaigns = []
    campaigns_by_platform: dict[str, list[dict[str, object]]] = {platform: [] for platform in PLATFORM_CONFIG}

    for platform in PLATFORM_CONFIG:
        organic = {
            "campaign_id": f"ORG-{platform_id(platform)}",
            "campaign_name": "Organic / Always On",
            "campaign_type": "Organic",
            "platform": platform,
            "objective": "Organic Content",
            "content_category_focus": "Mixed",
            "start_date": date(min(years), 1, 1).isoformat(),
            "end_date": date(max(years), 12, 31).isoformat(),
            "roas_target_low": 0.0,
            "roas_target_high": 0.0,
        }
        campaigns.append(organic)
        campaigns_by_platform[platform].append(organic)

        counter = 1
        for year in years:
            for name, objective, category, start_month, start_day, end_month, end_day, roas_range in CAMPAIGN_TEMPLATES:
                campaign = {
                    "campaign_id": f"CMP-{year}-{platform_id(platform)}-{counter:02d}",
                    "campaign_name": f"{year} {name}",
                    "campaign_type": "Paid",
                    "platform": platform,
                    "objective": objective,
                    "content_category_focus": category,
                    "start_date": date(year, start_month, start_day).isoformat(),
                    "end_date": date(year, end_month, end_day).isoformat(),
                    "roas_target_low": roas_range[0],
                    "roas_target_high": roas_range[1],
                }
                campaigns.append(campaign)
                campaigns_by_platform[platform].append(campaign)
                counter += 1

    return campaigns, campaigns_by_platform


def active_paid_campaigns(platform_campaigns: list[dict[str, object]], post_date: date) -> list[dict[str, object]]:
    active = []
    for campaign in platform_campaigns:
        if campaign["campaign_type"] != "Paid":
            continue
        start = datetime.strptime(str(campaign["start_date"]), "%Y-%m-%d").date()
        end = datetime.strptime(str(campaign["end_date"]), "%Y-%m-%d").date()
        if start <= post_date <= end:
            active.append(campaign)
    return active


def choose_campaign(platform: str, category: str, post_date: date, campaigns_by_platform: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    platform_campaigns = campaigns_by_platform[platform]
    active = active_paid_campaigns(platform_campaigns, post_date)
    focused = [campaign for campaign in active if campaign["content_category_focus"] == category]
    if focused and random.random() < 0.72:
        return random.choice(focused)
    if active and random.random() < 0.38:
        return random.choice(active)
    return platform_campaigns[0]


def estimate_reach(impressions: int) -> int:
    return max(1, int(impressions * random.uniform(0.58, 0.92)))


def estimate_clicks(platform: str, impressions: int, category: str, sentiment: str, is_verified: str) -> int:
    ctr = PLATFORM_CONFIG[platform]["base_ctr"]
    category_boost = {
        "Business": 1.18,
        "Technology": 1.15,
        "Education": 1.12,
        "Fitness": 1.04,
        "Fashion": 1.03,
        "Entertainment": 1.02,
        "Food": 0.98,
        "Health": 0.98,
        "Lifestyle": 0.96,
        "Gaming": 0.95,
        "Sports": 0.94,
        "Travel": 0.92,
    }.get(category, 1.0)
    sentiment_boost = {"Positive": 1.08, "Neutral": 1.0, "Negative": 0.86}.get(sentiment, 1.0)
    verified_boost = 1.05 if is_verified == "TRUE" else 1.0
    ctr *= category_boost * sentiment_boost * verified_boost * random.uniform(0.72, 1.26)
    ctr = max(0.0015, min(0.08, ctr))
    return min(impressions, max(0, int(impressions * ctr)))


def build_posts(source_rows: list[dict[str, str]], campaigns_by_platform: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows = []
    seen_ids: set[str] = set()

    for source_row in source_rows:
        platform = source_row["normalized_platform"]
        post_dt = datetime.strptime(source_row["Timestamp"], "%Y-%m-%d %H:%M:%S")
        post_date = post_dt.date()
        campaign = choose_campaign(platform, source_row["Category"], post_date, campaigns_by_platform)
        original_post_id = source_row["Post_ID"]
        post_id = f"KG-{original_post_id}"
        if post_id in seen_ids:
            post_id = f"{post_id}-{len(seen_ids) + 1}"
        seen_ids.add(post_id)

        impressions = max(1, clean_int(source_row["Views"]))
        likes = max(0, clean_int(source_row["Likes"]))
        comments = max(0, clean_int(source_row["Comments"]))
        shares = max(0, clean_int(source_row["Shares"]))
        saves = max(0, clean_int(source_row["Saves"]))
        is_verified = clean_bool(source_row["Is_Verified"])
        clicks = estimate_clicks(platform, impressions, source_row["Category"], source_row["Sentiment"], is_verified)
        reach = estimate_reach(impressions)

        rows.append(
            {
                "post_id": post_id,
                "source_dataset": SOURCE_HANDLE,
                "original_post_id": original_post_id,
                "platform": platform,
                "post_datetime": post_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "post_date": post_date.isoformat(),
                "post_hour": int(source_row["Hour_of_Day"]),
                "weekday_name": source_row["Day_of_Week"],
                "posting_time_bucket": posting_time_bucket(int(source_row["Hour_of_Day"])),
                "campaign_id": campaign["campaign_id"],
                "campaign_name": campaign["campaign_name"],
                "campaign_type": campaign["campaign_type"],
                "content_type": source_row["Content_Type"],
                "content_category": source_row["Category"],
                "sentiment": source_row["Sentiment"],
                "influencer_tier": source_row["Influencer_Tier"],
                "hashtag_count": clean_int(source_row["Hashtag_Count"]),
                "content_length": clean_int(source_row["Content_Length"]),
                "has_media": clean_bool(source_row["Has_Media"]),
                "is_verified": is_verified,
                "impressions": impressions,
                "reach": reach,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "saves": saves,
                "clicks": clicks,
                "engagement_rate": rate((likes + comments + shares + saves) / impressions),
                "ctr": rate(clicks / impressions),
            }
        )

    return rows


def build_campaign_rows(campaign_shells: list[dict[str, object]], posts: list[dict[str, object]]) -> list[dict[str, object]]:
    metrics: dict[str, dict[str, int]] = defaultdict(lambda: {"impressions": 0, "clicks": 0, "conversions": 0})
    for post in posts:
        campaign_id = str(post["campaign_id"])
        platform = str(post["platform"])
        clicks = int(post["clicks"])
        conversion_rate = PLATFORM_CONFIG[platform]["conversion_rate"]
        metrics[campaign_id]["impressions"] += int(post["impressions"])
        metrics[campaign_id]["clicks"] += clicks
        metrics[campaign_id]["conversions"] += int(clicks * conversion_rate * random.uniform(0.72, 1.34))

    rows = []
    for campaign in campaign_shells:
        campaign_id = str(campaign["campaign_id"])
        platform = str(campaign["platform"])
        campaign_metrics = metrics[campaign_id]
        impressions = campaign_metrics["impressions"]
        clicks = campaign_metrics["clicks"]
        conversions = campaign_metrics["conversions"]

        if campaign["campaign_type"] == "Paid" and impressions > 0:
            spend_value = (impressions / 1000) * PLATFORM_CONFIG[platform]["cpm"] * random.uniform(0.82, 1.22)
            roas_target = random.uniform(float(campaign["roas_target_low"]), float(campaign["roas_target_high"]))
            revenue_value = spend_value * roas_target
            spend_rounded = round(spend_value, 2)
            revenue_rounded = round(revenue_value, 2)
            roi_value = (revenue_rounded - spend_rounded) / spend_rounded if spend_rounded else 0.0
            roas_value = revenue_rounded / spend_rounded if spend_rounded else 0.0
        else:
            spend_rounded = 0.0
            revenue_rounded = 0.0
            roi_value = 0.0
            roas_value = 0.0

        rows.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign["campaign_name"],
                "campaign_type": campaign["campaign_type"],
                "platform": platform,
                "objective": campaign["objective"],
                "content_category_focus": campaign["content_category_focus"],
                "start_date": campaign["start_date"],
                "end_date": campaign["end_date"],
                "spend": money(spend_rounded),
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "revenue": money(revenue_rounded),
                "roi": rate(roi_value),
                "roas": rate(roas_value),
                "source_type": "Kaggle posts + modeled campaign economics",
            }
        )

    return rows


def build_followers(source_rows: list[dict[str, str]], posts: list[dict[str, object]], start_date: date, end_date: date) -> list[dict[str, object]]:
    follower_values: dict[str, list[int]] = defaultdict(list)
    for source_row in source_rows:
        follower_values[source_row["normalized_platform"]].append(clean_int(source_row["Follower_Count"]))

    posts_by_platform_date: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for post in posts:
        posts_by_platform_date[(str(post["platform"]), str(post["post_date"]))].append(post)

    rows = []
    for platform in PLATFORM_CONFIG:
        source_median = int(median(follower_values[platform]))
        followers = max(2500, int(source_median * random.uniform(0.74, 0.96)))
        for current in daterange(start_date, end_date):
            daily_posts = posts_by_platform_date.get((platform, current.isoformat()), [])
            post_boost = 0
            if daily_posts:
                avg_engagements = sum(
                    int(post["likes"]) + int(post["comments"]) + int(post["shares"]) + int(post["saves"])
                    for post in daily_posts
                ) / len(daily_posts)
                post_boost = int(avg_engagements * random.uniform(0.010, 0.035))

            seasonal_multiplier = 1.0
            if current.month in {3, 4, 8, 9, 11, 12}:
                seasonal_multiplier = random.uniform(1.06, 1.20)

            previous_followers = followers
            base_new = followers * PLATFORM_CONFIG[platform]["daily_growth_rate"] * seasonal_multiplier
            new_followers = max(0, int(random.gauss(base_new, max(5, base_new * 0.24))) + post_boost)
            lost_followers = max(0, int(random.gauss(followers * PLATFORM_CONFIG[platform]["daily_churn_rate"], 4)))
            net_growth = new_followers - lost_followers
            followers = max(0, followers + net_growth)

            rows.append(
                {
                    "date": current.isoformat(),
                    "platform": platform,
                    "followers": followers,
                    "new_followers": new_followers,
                    "lost_followers": lost_followers,
                    "net_growth": net_growth,
                    "follower_growth_rate": rate(net_growth / previous_followers if previous_followers else 0),
                    "source_type": "Modeled from Kaggle follower count and post engagement",
                }
            )

    return rows


def build_ab_tests(campaign_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    eligible = [
        campaign
        for campaign in campaign_rows
        if campaign["campaign_type"] == "Paid" and int(campaign["impressions"]) > 0 and int(campaign["clicks"]) > 0
    ]
    selected = random.sample(eligible, k=min(18, len(eligible)))
    rows = []

    for index, campaign in enumerate(selected, start=1):
        start = datetime.strptime(str(campaign["start_date"]), "%Y-%m-%d").date()
        end = datetime.strptime(str(campaign["end_date"]), "%Y-%m-%d").date()
        test_start = start + timedelta(days=random.randint(0, 8))
        test_end = min(end, test_start + timedelta(days=random.randint(10, 21)))
        test_id = f"AB-{index:03d}"
        base_impressions = max(2000, int(int(campaign["impressions"]) * random.uniform(0.24, 0.46)))
        baseline_ctr = int(campaign["clicks"]) / int(campaign["impressions"])
        baseline_conversion = PLATFORM_CONFIG[str(campaign["platform"])]["conversion_rate"]

        variants = []
        for variant in ["A", "B"]:
            variant_multiplier = 1.0 if variant == "A" else random.uniform(0.88, 1.28)
            impressions = int(base_impressions * random.uniform(0.90, 1.10))
            clicks = max(1, int(impressions * baseline_ctr * variant_multiplier))
            conversions = max(1, int(clicks * baseline_conversion * variant_multiplier * random.uniform(0.86, 1.18)))
            engagements = max(1, int(impressions * random.uniform(0.045, 0.145) * variant_multiplier))
            variants.append(
                {
                    "test_id": test_id,
                    "test_name": f"{campaign['campaign_name']} {campaign['platform']} Creative Test",
                    "campaign_id": campaign["campaign_id"],
                    "campaign_name": campaign["campaign_name"],
                    "platform": campaign["platform"],
                    "content_category": campaign["content_category_focus"],
                    "variant": variant,
                    "variant_description": "Control creative" if variant == "A" else "New hook and CTA",
                    "start_date": test_start.isoformat(),
                    "end_date": test_end.isoformat(),
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "engagements": engagements,
                    "engagement_rate": rate(engagements / impressions),
                    "ctr": rate(clicks / impressions),
                    "conversion_rate": rate(conversions / clicks),
                    "source_type": "Modeled A/B test from Kaggle-backed campaign",
                }
            )

        winner_rate = max(float(row["conversion_rate"]) for row in variants)
        for row in variants:
            row["is_winner"] = "TRUE" if float(row["conversion_rate"]) == winner_rate else "FALSE"
            row["winner"] = "Winner" if row["is_winner"] == "TRUE" else "Challenger"
            rows.append(row)

    rows.sort(key=lambda row: (row["test_id"], row["variant"]))
    return rows


def build_date_table(start_date: date, end_date: date) -> list[dict[str, object]]:
    rows = []
    for current in daterange(start_date, end_date):
        rows.append(
            {
                "date": current.isoformat(),
                "year": current.year,
                "quarter": f"Q{((current.month - 1) // 3) + 1}",
                "month_number": current.month,
                "month_name": MONTH_NAMES[current.month - 1],
                "month_start": date(current.year, current.month, 1).isoformat(),
                "weekday_number": current.weekday() + 1,
                "weekday_name": WEEKDAY_NAMES[current.weekday()],
                "is_weekend": "TRUE" if current.weekday() >= 5 else "FALSE",
            }
        )
    return rows


def build_platforms(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    counts: dict[str, int] = defaultdict(int)
    follower_values: dict[str, list[int]] = defaultdict(list)
    for row in source_rows:
        platform = row["normalized_platform"]
        counts[platform] += 1
        follower_values[platform].append(clean_int(row["Follower_Count"]))

    rows = []
    for platform, config in PLATFORM_CONFIG.items():
        rows.append(
            {
                "platform": platform,
                "platform_slug": config["slug"],
                "starting_followers": int(median(follower_values[platform])),
                "primary_goal": config["primary_goal"],
                "kaggle_post_rows": counts[platform],
            }
        )
    return rows


def build_source_manifest(source_csv: Path, source_rows: list[dict[str, str]], posts: list[dict[str, object]]) -> list[dict[str, object]]:
    platform_counts: dict[str, int] = defaultdict(int)
    for post in posts:
        platform_counts[str(post["platform"])] += 1
    imported_counts = "; ".join(f"{platform}: {platform_counts[platform]}" for platform in sorted(platform_counts))
    return [
        {
            "source_name": "Social Media Engagement Dataset",
            "source_type": "Kaggle dataset",
            "kaggle_handle": SOURCE_HANDLE,
            "source_url": SOURCE_URL,
            "local_source_file": source_csv.name,
            "raw_rows_read": len(source_rows),
            "processed_post_rows": len(posts),
            "platform_rows": imported_counts,
            "fields_used": "Timestamp, Platform, Content_Type, Category, Likes, Comments, Shares, Views, Saves, Follower_Count, Hour_of_Day, Day_of_Week, Sentiment, Influencer_Tier, Has_Media, Is_Verified",
            "enrichment_note": "Campaign assignments, clicks, reach, ROI, follower daily history, and A/B tests are modeled for dashboard completeness.",
        }
    ]


def generate(output_dir: Path, source_csv: Path, seed: int) -> None:
    random.seed(seed)
    source_rows = read_kaggle_rows(source_csv)
    if not source_rows:
        raise SystemExit("No supported platform rows found in the Kaggle source file.")

    parsed_dates = [datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S").date() for row in source_rows]
    start_date = min(parsed_dates)
    end_date = max(parsed_dates)
    years = list(range(start_date.year, end_date.year + 1))

    campaign_shells, campaigns_by_platform = build_campaign_shells(years)
    posts = build_posts(source_rows, campaigns_by_platform)
    campaigns = build_campaign_rows(campaign_shells, posts)
    followers = build_followers(source_rows, posts, start_date, end_date)
    ab_tests = build_ab_tests(campaigns)
    date_table = build_date_table(start_date, end_date)
    platforms = build_platforms(source_rows)
    source_manifest = build_source_manifest(source_csv, source_rows, posts)

    write_csv(
        output_dir / "posts.csv",
        posts,
        [
            "post_id",
            "source_dataset",
            "original_post_id",
            "platform",
            "post_datetime",
            "post_date",
            "post_hour",
            "weekday_name",
            "posting_time_bucket",
            "campaign_id",
            "campaign_name",
            "campaign_type",
            "content_type",
            "content_category",
            "sentiment",
            "influencer_tier",
            "hashtag_count",
            "content_length",
            "has_media",
            "is_verified",
            "impressions",
            "reach",
            "likes",
            "comments",
            "shares",
            "saves",
            "clicks",
            "engagement_rate",
            "ctr",
        ],
    )
    write_csv(
        output_dir / "campaigns.csv",
        campaigns,
        [
            "campaign_id",
            "campaign_name",
            "campaign_type",
            "platform",
            "objective",
            "content_category_focus",
            "start_date",
            "end_date",
            "spend",
            "impressions",
            "clicks",
            "conversions",
            "revenue",
            "roi",
            "roas",
            "source_type",
        ],
    )
    write_csv(
        output_dir / "followers_daily.csv",
        followers,
        [
            "date",
            "platform",
            "followers",
            "new_followers",
            "lost_followers",
            "net_growth",
            "follower_growth_rate",
            "source_type",
        ],
    )
    write_csv(
        output_dir / "ab_tests.csv",
        ab_tests,
        [
            "test_id",
            "test_name",
            "campaign_id",
            "campaign_name",
            "platform",
            "content_category",
            "variant",
            "variant_description",
            "start_date",
            "end_date",
            "impressions",
            "clicks",
            "conversions",
            "engagements",
            "engagement_rate",
            "ctr",
            "conversion_rate",
            "source_type",
            "is_winner",
            "winner",
        ],
    )
    write_csv(
        output_dir / "date_table.csv",
        date_table,
        ["date", "year", "quarter", "month_number", "month_name", "month_start", "weekday_number", "weekday_name", "is_weekend"],
    )
    write_csv(
        output_dir / "platforms.csv",
        platforms,
        ["platform", "platform_slug", "starting_followers", "primary_goal", "kaggle_post_rows"],
    )
    write_csv(
        output_dir / "source_manifest.csv",
        source_manifest,
        [
            "source_name",
            "source_type",
            "kaggle_handle",
            "source_url",
            "local_source_file",
            "raw_rows_read",
            "processed_post_rows",
            "platform_rows",
            "fields_used",
            "enrichment_note",
        ],
    )

    print(f"Prepared Kaggle-backed CSV files in {output_dir}")
    print(f"Kaggle source: {SOURCE_HANDLE}")
    print(f"Source CSV: {source_csv.name}")
    print(f"Posts: {len(posts):,}")
    print(f"Campaign rows: {len(campaigns):,}")
    print(f"Follower rows: {len(followers):,}")
    print(f"A/B test rows: {len(ab_tests):,}")
    print(f"Date rows: {len(date_table):,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Kaggle-backed social media analytics data.")
    parser.add_argument("--source-csv", help="Optional local Kaggle CSV path. If omitted, kagglehub downloads it.")
    parser.add_argument("--output-dir", default="data/processed", help="Directory for processed CSV outputs.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for enrichment fields.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(Path(args.output_dir), resolve_source_csv(args.source_csv), args.seed)
