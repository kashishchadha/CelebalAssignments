"""Builds the SQLite database from the cleaned CSVs.

Tables are created from sql/schema.sql, then loaded parent-first (customers and
products before orders, orders before order_items) so the foreign keys hold.
"""

import csv
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import config as cfg

LOAD_ORDER = [
    ("customers", ["customer_id", "customer_name", "email", "registration_date", "customer_type"]),
    ("products", ["product_id", "product_name", "category", "subcategory", "cost_price"]),
    ("orders", ["order_id", "customer_id", "order_date", "status", "region_code", "payment_method"]),
    ("order_items", ["order_item_id", "order_id", "product_id", "quantity", "unit_price",
                     "discount_percent", "is_return", "line_revenue"]),
]


def load_table(conn, table, columns):
    path = cfg.CLEAN_DIR / f"{table}.csv"
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            tuple(r[c] if r[c] != "" else None for c in columns)
            for r in reader
        ]

    placeholders = ", ".join("?" * len(columns))
    conn.executemany(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", rows
    )
    print(f"  {table:<14} {len(rows):>6} rows")


def main():
    if not cfg.CLEAN_DIR.exists():
        raise SystemExit("No cleaned data found. Run src/clean_data.py first.")

    if cfg.DB_PATH.exists():
        cfg.DB_PATH.unlink()

    conn = sqlite3.connect(cfg.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    conn.executescript((cfg.SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    print("Schema created in", cfg.DB_PATH.name)

    for table, columns in LOAD_ORDER:
        load_table(conn, table, columns)

    conn.commit()

    checks = conn.execute("""
        SELECT (SELECT COUNT(*) FROM orders),
               (SELECT COUNT(*) FROM order_items),
               (SELECT ROUND(SUM(revenue), 2) FROM item_revenue WHERE status <> 'CANCELLED')
    """).fetchone()
    print(f"\nOrders: {checks[0]}  Items: {checks[1]}  Net revenue: {checks[2]:,.2f}")

    conn.close()


if __name__ == "__main__":
    main()
