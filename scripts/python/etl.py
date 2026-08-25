"""ETL: extract raw users/events from Postgres, aggregate into daily metrics,
load the result into ClickHouse for analytics.
"""

import pandas as pd

from dataexpo.clickhouse import get_client
from dataexpo.db import get_engine


def extract() -> tuple[pd.DataFrame, pd.DataFrame]:
    engine = get_engine()
    users = pd.read_sql("SELECT * FROM users", engine)
    events = pd.read_sql("SELECT * FROM events", engine)
    print(f"Extracted: {len(users)} users, {len(events)} events from Postgres")
    return users, events


def transform(users: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    events = events.merge(users[["user_id", "country", "plan"]], on="user_id")
    events["event_date"] = pd.to_datetime(events["event_ts"]).dt.date

    daily = (
        events.groupby(["event_date", "country", "plan"])
        .agg(
            active_users=("user_id", "nunique"),
            views=("event_type", lambda s: (s == "view").sum()),
            add_to_carts=("event_type", lambda s: (s == "add_to_cart").sum()),
            purchases=("event_type", lambda s: (s == "purchase").sum()),
            churns=("event_type", lambda s: (s == "churn").sum()),
            revenue=("revenue", "sum"),
        )
        .reset_index()
    )
    print(f"Transformed: {len(daily)} daily_metrics rows")
    return daily


def load(daily: pd.DataFrame) -> None:
    client = get_client()
    client.command(
        """
        CREATE TABLE IF NOT EXISTS daily_metrics (
            event_date Date,
            country String,
            plan String,
            active_users UInt32,
            views UInt32,
            add_to_carts UInt32,
            purchases UInt32,
            churns UInt32,
            revenue Float64
        ) ENGINE = MergeTree ORDER BY (event_date, country, plan)
        """
    )
    client.command("TRUNCATE TABLE daily_metrics")
    client.insert_df("daily_metrics", daily)
    print(f"Loaded: {len(daily)} rows into ClickHouse.daily_metrics")


def main() -> None:
    users, events = extract()
    daily = transform(users, events)
    load(daily)


if __name__ == "__main__":
    main()
