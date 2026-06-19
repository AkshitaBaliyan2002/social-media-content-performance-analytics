#!/usr/bin/env python3
"""Validate generated social media analytics CSV files."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_FILES = {
    "posts.csv",
    "campaigns.csv",
    "followers_daily.csv",
    "ab_tests.csv",
    "date_table.csv",
    "platforms.csv",
}


REQUIRED_COLUMNS = {
    "posts.csv": {
        "post_id",
        "platform",
        "post_date",
        "post_hour",
        "content_type",
        "content_category",
        "impressions",
        "likes",
        "comments",
        "shares",
        "saves",
        "clicks",
        "engagement_rate",
        "ctr",
    },
    "campaigns.csv": {
        "campaign_id",
        "campaign_name",
        "campaign_type",
        "platform",
        "objective",
        "spend",
        "impressions",
        "clicks",
        "conversions",
        "revenue",
        "roi",
        "roas",
    },
    "followers_daily.csv": {
        "date",
        "platform",
        "followers",
        "new_followers",
        "lost_followers",
        "net_growth",
        "follower_growth_rate",
    },
    "ab_tests.csv": {
        "test_id",
        "platform",
        "variant",
        "impressions",
        "clicks",
        "conversions",
        "engagements",
        "engagement_rate",
        "ctr",
        "conversion_rate",
        "is_winner",
    },
    "date_table.csv": {"date", "year", "quarter", "month_number", "weekday_name"},
    "platforms.csv": {"platform", "platform_slug", "starting_followers", "primary_goal"},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def close_enough(left: float, right: float, tolerance: float = 0.00001) -> bool:
    return abs(left - right) <= tolerance


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_files(data_dir: Path, errors: list[str]) -> dict[str, list[dict[str, str]]]:
    available = {path.name for path in data_dir.glob("*.csv")}
    missing = EXPECTED_FILES - available
    require(not missing, f"Missing expected files: {sorted(missing)}", errors)

    tables: dict[str, list[dict[str, str]]] = {}
    for file_name in EXPECTED_FILES & available:
        rows = read_csv(data_dir / file_name)
        tables[file_name] = rows
        require(rows, f"{file_name} has no data rows", errors)
        if rows:
            actual_columns = set(rows[0].keys())
            missing_columns = REQUIRED_COLUMNS[file_name] - actual_columns
            require(not missing_columns, f"{file_name} missing columns: {sorted(missing_columns)}", errors)
    return tables


def validate_posts(rows: list[dict[str, str]], errors: list[str]) -> None:
    post_ids = Counter(row["post_id"] for row in rows)
    duplicates = [post_id for post_id, count in post_ids.items() if count > 1]
    require(not duplicates, f"Duplicate post IDs found: {duplicates[:5]}", errors)

    for index, row in enumerate(rows, start=2):
        require(bool(row["platform"]), f"posts.csv row {index}: platform is blank", errors)
        require(bool(row["content_category"]), f"posts.csv row {index}: content_category is blank", errors)
        require(bool(row["post_date"]), f"posts.csv row {index}: post_date is blank", errors)

        impressions = int(row["impressions"])
        likes = int(row["likes"])
        comments = int(row["comments"])
        shares = int(row["shares"])
        saves = int(row["saves"])
        clicks = int(row["clicks"])
        require(impressions > 0, f"posts.csv row {index}: impressions must be positive", errors)
        require(all(value >= 0 for value in [likes, comments, shares, saves, clicks]), f"posts.csv row {index}: negative metric", errors)

        expected_engagement = (likes + comments + shares + saves) / impressions
        expected_ctr = clicks / impressions
        require(close_enough(float(row["engagement_rate"]), expected_engagement), f"posts.csv row {index}: engagement_rate mismatch", errors)
        require(close_enough(float(row["ctr"]), expected_ctr), f"posts.csv row {index}: ctr mismatch", errors)


def validate_campaigns(rows: list[dict[str, str]], errors: list[str]) -> None:
    campaign_ids = Counter(row["campaign_id"] for row in rows)
    duplicates = [campaign_id for campaign_id, count in campaign_ids.items() if count > 1]
    require(not duplicates, f"Duplicate campaign IDs found: {duplicates[:5]}", errors)

    for index, row in enumerate(rows, start=2):
        spend = float(row["spend"])
        revenue = float(row["revenue"])
        impressions = int(row["impressions"])
        clicks = int(row["clicks"])
        conversions = int(row["conversions"])
        require(spend >= 0, f"campaigns.csv row {index}: spend is negative", errors)
        require(revenue >= 0, f"campaigns.csv row {index}: revenue is negative", errors)
        require(all(value >= 0 for value in [impressions, clicks, conversions]), f"campaigns.csv row {index}: negative metric", errors)

        if spend > 0:
            require(close_enough(float(row["roi"]), (revenue - spend) / spend), f"campaigns.csv row {index}: roi mismatch", errors)
            require(close_enough(float(row["roas"]), revenue / spend), f"campaigns.csv row {index}: roas mismatch", errors)


def validate_followers(rows: list[dict[str, str]], errors: list[str]) -> None:
    for index, row in enumerate(rows, start=2):
        require(bool(row["date"]), f"followers_daily.csv row {index}: date is blank", errors)
        require(bool(row["platform"]), f"followers_daily.csv row {index}: platform is blank", errors)
        followers = int(row["followers"])
        new_followers = int(row["new_followers"])
        lost_followers = int(row["lost_followers"])
        require(followers >= 0, f"followers_daily.csv row {index}: followers is negative", errors)
        require(new_followers >= 0, f"followers_daily.csv row {index}: new_followers is negative", errors)
        require(lost_followers >= 0, f"followers_daily.csv row {index}: lost_followers is negative", errors)


def validate_ab_tests(rows: list[dict[str, str]], errors: list[str]) -> None:
    winners_by_test: defaultdict[str, int] = defaultdict(int)
    variants_by_test: defaultdict[str, set[str]] = defaultdict(set)

    for index, row in enumerate(rows, start=2):
        impressions = int(row["impressions"])
        clicks = int(row["clicks"])
        conversions = int(row["conversions"])
        engagements = int(row["engagements"])
        require(impressions > 0, f"ab_tests.csv row {index}: impressions must be positive", errors)
        require(all(value >= 0 for value in [clicks, conversions, engagements]), f"ab_tests.csv row {index}: negative metric", errors)
        require(close_enough(float(row["engagement_rate"]), engagements / impressions), f"ab_tests.csv row {index}: engagement_rate mismatch", errors)
        require(close_enough(float(row["ctr"]), clicks / impressions), f"ab_tests.csv row {index}: ctr mismatch", errors)
        require(close_enough(float(row["conversion_rate"]), conversions / clicks), f"ab_tests.csv row {index}: conversion_rate mismatch", errors)

        variants_by_test[row["test_id"]].add(row["variant"])
        if row["is_winner"] == "TRUE":
            winners_by_test[row["test_id"]] += 1

    for test_id, variants in variants_by_test.items():
        require(variants == {"A", "B"}, f"{test_id}: expected variants A and B, found {sorted(variants)}", errors)
        require(winners_by_test[test_id] == 1, f"{test_id}: expected exactly one winner", errors)


def validate(data_dir: Path) -> None:
    errors: list[str] = []
    tables = validate_files(data_dir, errors)

    if "posts.csv" in tables:
        validate_posts(tables["posts.csv"], errors)
    if "campaigns.csv" in tables:
        validate_campaigns(tables["campaigns.csv"], errors)
    if "followers_daily.csv" in tables:
        validate_followers(tables["followers_daily.csv"], errors)
    if "ab_tests.csv" in tables:
        validate_ab_tests(tables["ab_tests.csv"], errors)

    if errors:
        print("Validation failed:")
        for error in errors[:50]:
            print(f"- {error}")
        if len(errors) > 50:
            print(f"- ...and {len(errors) - 50} more")
        raise SystemExit(1)

    print("Validation passed.")
    for file_name in sorted(tables):
        print(f"{file_name}: {len(tables[file_name]):,} rows")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated social media analytics CSV files.")
    parser.add_argument("--data-dir", default="data/processed", help="Directory containing generated CSV files.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    validate(Path(args.data_dir))

