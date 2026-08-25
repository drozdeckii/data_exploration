from dataexpo.db import get_connection


def main() -> None:
    conn = get_connection()
    try:
        print("Connected:", conn.info.dbname)
    finally:
        conn.close()
