import os

import psycopg
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def _config() -> dict:
    load_dotenv(find_dotenv())
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "sandbox_dev"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD"),
    }


def get_connection():
    return psycopg.connect(**_config())


def get_engine() -> Engine:
    cfg = _config()
    url = (
        f"postgresql+psycopg://{cfg['user']}:{cfg['password']}@"
        f"{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    )
    return create_engine(url)
