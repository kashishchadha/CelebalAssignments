"""Runs every query in sql/*.sql and saves the output.

Each query in those files is introduced by a `-- QUERY: <name>` marker. The name
becomes the CSV filename, so adding a query means adding a marker and nothing
else.

    python src/run_queries.py            run all of them
    python src/run_queries.py q09        run only queries whose name contains q09
"""

import csv
import re
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import config as cfg

MARKER = re.compile(r"^--\s*QUERY:\s*(\w+)\s*$", re.MULTILINE)
PREVIEW_ROWS = 5
OUT_DIR = cfg.REPORTS_DIR / "query_output"


def split_queries(sql_text):
    """Return [(name, sql), ...] for one file."""
    matches = list(MARKER.finditer(sql_text))
    queries = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(sql_text)
        body = sql_text[m.end():end].strip().rstrip(";")
        if body:
            queries.append((m.group(1), body))
    return queries


def preview(name, columns, rows):
    print(f"\n{name}  ({len(rows)} rows)")
    if not rows:
        print("  no rows returned")
        return
    widths = [
        max(len(str(c)), *(len(str(r[i])) for r in rows[:PREVIEW_ROWS]))
        for i, c in enumerate(columns)
    ]
    print("  " + " | ".join(str(c).ljust(w) for c, w in zip(columns, widths)))
    print("  " + "-+-".join("-" * w for w in widths))
    for r in rows[:PREVIEW_ROWS]:
        print("  " + " | ".join(str(v).ljust(w) for v, w in zip(r, widths)))
    if len(rows) > PREVIEW_ROWS:
        print(f"  ... {len(rows) - PREVIEW_ROWS} more rows in {name}.csv")


def main():
    keyword = sys.argv[1].lower() if len(sys.argv) > 1 else None

    if not cfg.DB_PATH.exists():
        raise SystemExit("Database not found. Run src/load_db.py first.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(cfg.DB_PATH)

    executed = 0
    for sql_file in sorted(cfg.SQL_DIR.glob("0*.sql")):
        print(f"\n=== {sql_file.name} " + "=" * (46 - len(sql_file.name)))
        for name, body in split_queries(sql_file.read_text(encoding="utf-8")):
            if keyword and keyword not in name.lower():
                continue
            cursor = conn.execute(body)
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchall()

            with open(OUT_DIR / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)

            preview(name, columns, rows)
            executed += 1

    conn.close()
    print(f"\n{executed} queries executed. CSV output in {OUT_DIR}")


if __name__ == "__main__":
    main()
