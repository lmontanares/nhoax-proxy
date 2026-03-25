import sqlite3

import pytest

from app.database import init_db, is_url_malicious


def test_init_db_creates_urls_table(db_path):
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='urls'"
    ).fetchone()
    conn.close()
    assert row is not None


def test_init_db_is_idempotent(db_path):
    init_db(db_path)  # second call must not raise
    init_db(db_path)


def test_is_url_malicious_returns_true_for_known_url(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO urls (url) VALUES (?)", ("evil.com/malware",))
    conn.commit()
    conn.close()
    assert is_url_malicious("evil.com/malware", db_path) is True


def test_is_url_malicious_returns_false_for_unknown_url(db_path):
    assert is_url_malicious("good.com/safe", db_path) is False
