"""Generate a synthetic users/events dataset and load it into Postgres and ClickHouse."""

import numpy as np
import pandas as pd

from dataexpo.clickhouse import get_client
from dataexpo.db import get_engine

RNG = np.random.default_rng(42)
N_USERS = 2_000
N_EVENTS = 50_000
EVENT_TYPES = ["view", "add_to_cart", "purchase", "churn"]
EVENT_WEIGHTS = [0.60, 0.25, 0.12, 0.03]
COUNTRIES = ["US", "DE", "FR", "GB", "PL", "BR"]
PLANS = ["free", "pro", "enterprise"]
PLAN_WEIGHTS = [0.70, 0.25, 0.05]


def generate_users() -> pd.DataFrame:
    signup_date = pd.Timestamp("2025-01-01") + pd.to_timedelta(
        RNG.integers(0, 365, size=N_USERS), unit="D"
    )
    return pd.DataFrame(
        {
            "user_id": np.arange(1, N_USERS + 1),
            "signup_date": signup_date,
            "country": RNG.choice(COUNTRIES, size=N_USERS),
            "plan": RNG.choice(PLANS, size=N_USERS, p=PLAN_WEIGHTS),
        }
    )


def generate_events(users: pd.DataFrame) -> pd.DataFrame:
    user_ids = RNG.choice(users["user_id"], size=N_EVENTS)
    signup_by_user = users.set_index("user_id")["signup_date"]
    offsets = RNG.integers(0, 180, size=N_EVENTS)
    event_ts = signup_by_user.loc[user_ids].to_numpy() + pd.to_timedelta(
        offsets, unit="D"
    )
    event_type = RNG.choice(EVENT_TYPES, size=N_EVENTS, p=EVENT_WEIGHTS)
    revenue = np.where(
        event_type == "purchase",
        RNG.gamma(shape=2.0, scale=25.0, size=N_EVENTS).round(2),
        0.0,
    )
    return pd.DataFrame(
        {
            "event_id": np.arange(1, N_EVENTS + 1),
            "user_id": user_ids,
            "event_type": event_type,
            "event_ts": event_ts,
            "revenue": revenue,
        }
    )


def load_postgres(users: pd.DataFrame, events: pd.DataFrame) -> None:
    engine = get_engine()
    users.to_sql("users", engine, if_exists="replace", index=False)
    events.to_sql("events", engine, if_exists="replace", index=False)
    print(f"Postgres: loaded {len(users)} users, {len(events)} events")


def load_clickhouse(users: pd.DataFrame, events: pd.DataFrame) -> None:
    client = get_client()
    client.command(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id UInt32,
            signup_date Date,
            country String,
            plan String
        ) ENGINE = MergeTree ORDER BY user_id
        """
    )
    client.command(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id UInt32,
            user_id UInt32,
            event_type String,
            event_ts DateTime,
            revenue Float64
        ) ENGINE = MergeTree ORDER BY (user_id, event_ts)
        """
    )
    client.command("TRUNCATE TABLE users")
    client.command("TRUNCATE TABLE events")
    client.insert_df("users", users)
    client.insert_df("events", events)
    print(f"ClickHouse: loaded {len(users)} users, {len(events)} events")


def main() -> None:
    users = generate_users()
    events = generate_events(users)
    load_postgres(users, events)
    load_clickhouse(users, events)


if __name__ == "__main__":
    main()
