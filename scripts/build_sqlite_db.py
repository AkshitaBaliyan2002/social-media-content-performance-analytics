#!/usr/bin/env python3
"""Load processed CSV files into a local SQLite database for SQL analysis."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path


TABLE_SCHEMAS = {
    "posts": """
        CREATE TABLE posts (
            post_id TEXT PRIMARY KEY,
            source_dataset TEXT,
            original_post_id TEXT,
            platform TEXT NOT NULL,
            post_datetime TEXT NOT NULL,
            post_date TEXT NOT NULL,
            post_hour INTEGER NOT NULL,
            weekday_name TEXT NOT NULL,
            posting_time_bucket TEXT NOT NULL,
            campaign_id TEXT NOT NULL,
            campaign_name TEXT NOT NULL,
            campaign_type TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content_category TEXT NOT NULL,
            sentiment TEXT,
            influencer_tier TEXT,
            hashtag_count INTEGER,
            content_length INTEGER,
            has_media TEXT,
            is_verified TEXT,
            impressions INTEGER NOT NULL,
            reach INTEGER NOT NULL,
            likes INTEGER NOT NULL,
            comments INTEGER NOT NULL,
            shares INTEGER NOT NULL,
            saves INTEGER NOT NULL,
            clicks INTEGER NOT NULL,
            engagement_rate REAL NOT NULL,
            ctr REAL NOT NULL
        )
    """,
    "campaigns": """
        CREATE TABLE campaigns (
            campaign_id TEXT PRIMARY KEY,
            campaign_name TEXT NOT NULL,
            campaign_type TEXT NOT NULL,
            platform TEXT NOT NULL,
            objective TEXT NOT NULL,
            content_category_focus TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            spend REAL NOT NULL,
            impressions INTEGER NOT NULL,
            clicks INTEGER NOT NULL,
            conversions INTEGER NOT NULL,
            revenue REAL NOT NULL,
            roi REAL NOT NULL,
            roas REAL NOT NULL,
            source_type TEXT
        )
    """,
    "followers_daily": """
        CREATE TABLE followers_daily (
            date TEXT NOT NULL,
            platform TEXT NOT NULL,
            followers INTEGER NOT NULL,
            new_followers INTEGER NOT NULL,
            lost_followers INTEGER NOT NULL,
            net_growth INTEGER NOT NULL,
            follower_growth_rate REAL NOT NULL,
            source_type TEXT,
            PRIMARY KEY (date, platform)
        )
    """,
    "ab_tests": """
        CREATE TABLE ab_tests (
            test_id TEXT NOT NULL,
            test_name TEXT NOT NULL,
            campaign_id TEXT NOT NULL,
            campaign_name TEXT NOT NULL,
            platform TEXT NOT NULL,
            content_category TEXT NOT NULL,
            variant TEXT NOT NULL,
            variant_description TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            impressions INTEGER NOT NULL,
            clicks INTEGER NOT NULL,
            conversions INTEGER NOT NULL,
            engagements INTEGER NOT NULL,
            engagement_rate REAL NOT NULL,
            ctr REAL NOT NULL,
            conversion_rate REAL NOT NULL,
            source_type TEXT,
            is_winner TEXT NOT NULL,
            winner TEXT NOT NULL,
            PRIMARY KEY (test_id, variant)
        )
    """,
    "date_table": """
        CREATE TABLE date_table (
            date TEXT PRIMARY KEY,
            year INTEGER NOT NULL,
            quarter TEXT NOT NULL,
            month_number INTEGER NOT NULL,
            month_name TEXT NOT NULL,
            month_start TEXT NOT NULL,
            weekday_number INTEGER NOT NULL,
            weekday_name TEXT NOT NULL,
            is_weekend TEXT NOT NULL
        )
    """,
    "platforms": """
        CREATE TABLE platforms (
            platform TEXT PRIMARY KEY,
            platform_slug TEXT NOT NULL,
            starting_followers INTEGER NOT NULL,
            primary_goal TEXT NOT NULL,
            kaggle_post_rows INTEGER NOT NULL
        )
    """,
    "source_manifest": """
        CREATE TABLE source_manifest (
            source_name TEXT,
            source_type TEXT,
            kaggle_handle TEXT,
            source_url TEXT,
            local_source_file TEXT,
            raw_rows_read INTEGER,
            processed_post_rows INTEGER,
            platform_rows TEXT,
            fields_used TEXT,
            enrichment_note TEXT
        )
    """,
}


LOAD_ORDER = [
    "platforms",
    "date_table",
    "campaigns",
    "posts",
    "followers_daily",
    "ab_tests",
    "source_manifest",
]


def load_csv(connection: sqlite3.Connection, table_name: str, csv_path: Path) -> int:
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    if not rows:
        return 0

    columns = reader.fieldnames or []
    placeholders = ", ".join("?" for _ in columns)
    column_list = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
    connection.executemany(sql, ([row[column] for column in columns] for row in rows))
    return len(rows)


def build_database(data_dir: Path, db_path: Path, sql_path: Path) -> None:
    missing = [table for table in LOAD_ORDER if not (data_dir / f"{table}.csv").exists()]
    if missing:
        raise FileNotFoundError(f"Missing CSV files in {data_dir}: {', '.join(missing)}")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = OFF")

        for table_name in reversed(LOAD_ORDER):
            connection.execute(f"DROP TABLE IF EXISTS {table_name}")

        for table_name in LOAD_ORDER:
            connection.execute(TABLE_SCHEMAS[table_name])

        counts = {}
        for table_name in LOAD_ORDER:
            counts[table_name] = load_csv(connection, table_name, data_dir / f"{table_name}.csv")

        if sql_path.exists():
            connection.executescript(sql_path.read_text(encoding="utf-8"))

        connection.commit()

    print(f"SQLite database built: {db_path}")
    for table_name in LOAD_ORDER:
        print(f"{table_name}: {counts[table_name]:,} rows")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a SQLite database from processed social media CSV files.")
    parser.add_argument("--data-dir", default="data/processed", help="Directory containing processed CSV files.")
    parser.add_argument("--db-path", default="data/social_media_analytics.sqlite", help="Output SQLite database path.")
    parser.add_argument("--sql-path", default="sql/schema_and_views.sql", help="SQL file containing analysis views.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_database(Path(args.data_dir), Path(args.db_path), Path(args.sql_path))
