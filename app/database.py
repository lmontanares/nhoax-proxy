import os
import sqlite3
from contextlib import contextmanager
from typing import Generator


def get_db_path() -> str:
    return os.environ.get("DB_PATH", "nhoax.db")


@contextmanager
def get_connection(db_path: str | None = None) -> Generator[sqlite3.Connection, None, None]:
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: str | None = None) -> None:
    with get_connection(db_path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS urls (url TEXT PRIMARY KEY)")
        conn.commit()


def is_url_malicious(url: str, db_path: str | None = None) -> bool:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT 1 FROM urls WHERE url = ?", (url,)).fetchone()
        return row is not None
