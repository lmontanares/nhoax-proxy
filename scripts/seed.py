import csv
import sys

from app.database import get_connection, init_db


def seed(csv_path: str, db_path: str | None = None) -> None:
    try:
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            rows = [(row["url"],) for row in reader]
    except FileNotFoundError:
        print(f"File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.executemany("INSERT OR IGNORE INTO urls (url) VALUES (?)", rows)
        conn.commit()
    print(f"Loaded {len(rows)} URLs")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed malicious URLs from CSV")
    parser.add_argument("csv_path", help="Path to CSV file with a 'url' column")
    args = parser.parse_args()
    seed(args.csv_path)
