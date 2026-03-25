import csv
import sqlite3

import pytest

from scripts.seed import seed


def write_csv(path, urls):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url"])
        writer.writeheader()
        writer.writerows({"url": u} for u in urls)


def test_seed_inserts_urls(db_path, tmp_path):
    csv_path = tmp_path / "urls.csv"
    write_csv(csv_path, ["evil.com/malware", "bad.com:8080/virus"])
    seed(str(csv_path), db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT url FROM urls ORDER BY url").fetchall()
    conn.close()
    assert rows == [("bad.com:8080/virus",), ("evil.com/malware",)]


def test_seed_is_idempotent(db_path, tmp_path):
    csv_path = tmp_path / "urls.csv"
    write_csv(csv_path, ["evil.com/malware"])
    seed(str(csv_path), db_path)
    seed(str(csv_path), db_path)  # second call must not raise
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT url FROM urls").fetchall()
    conn.close()
    assert len(rows) == 1


def test_seed_ignores_duplicates_within_csv(db_path, tmp_path):
    csv_path = tmp_path / "urls.csv"
    write_csv(csv_path, ["evil.com/malware", "evil.com/malware"])
    seed(str(csv_path), db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT url FROM urls").fetchall()
    conn.close()
    assert len(rows) == 1


def test_seed_missing_file_exits_nonzero(db_path):
    with pytest.raises(SystemExit) as exc_info:
        seed("nonexistent.csv", db_path)
    assert exc_info.value.code != 0
