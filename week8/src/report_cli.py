"""Command line summary report. Standard library only - sqlite3, argparse, datetime.

    python src/report_cli.py                                  prompts for input
    python src/report_cli.py --type monthly --from 2025-01-01 --to 2025-06-30

The previous period is the same number of days immediately before the start
date, so a 30 day window is always compared against the 30 days before it.
"""

import argparse
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "ecommerce.db"

BUCKET_FORMAT = {
    "daily": "%Y-%m-%d",
    "weekly": "%Y-W%W",
    "monthly": "%Y-%m",
}

TOTALS_SQL = """
    SELECT COUNT(DISTINCT o.order_id),
           COUNT(DISTINCT o.customer_id),
           COALESCE(SUM(oi.line_revenue), 0)
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status <> 'CANCELLED'
      AND DATE(o.order_date) BETWEEN ? AND ?
"""

BUCKET_SQL = """
    SELECT STRFTIME(?, o.order_date) AS bucket,
           COUNT(DISTINCT o.order_id),
           ROUND(SUM(oi.line_revenue), 2)
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.status <> 'CANCELLED'
      AND DATE(o.order_date) BETWEEN ? AND ?
    GROUP BY bucket
    ORDER BY bucket
"""

TOP_PRODUCTS_SQL = """
    SELECT p.product_name,
           SUM(oi.quantity) AS units,
           ROUND(SUM(oi.line_revenue), 2) AS revenue
    FROM order_items oi
    JOIN orders   o ON o.order_id   = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.status <> 'CANCELLED'
      AND DATE(o.order_date) BETWEEN ? AND ?
    GROUP BY p.product_name
    ORDER BY revenue DESC
    LIMIT 3
"""


def parse_date(value):
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit(f"'{value}' is not a valid date. Use YYYY-MM-DD.")


def pct_change(current, previous):
    if not previous:
        return None
    return (current - previous) / previous * 100


def fmt_change(value):
    if value is None:
        return "n/a (no data in previous period)"
    return f"{value:+.1f}%"


def get_args():
    parser = argparse.ArgumentParser(description="E-commerce summary report")
    parser.add_argument("--type", choices=list(BUCKET_FORMAT), help="report granularity")
    parser.add_argument("--from", dest="date_from", help="start date, YYYY-MM-DD")
    parser.add_argument("--to", dest="date_to", help="end date, YYYY-MM-DD")
    args = parser.parse_args()

    report_type = args.type
    while report_type not in BUCKET_FORMAT:
        report_type = input("Report type (daily/weekly/monthly): ").strip().lower()

    date_from = parse_date(args.date_from or input("Start date (YYYY-MM-DD): "))
    date_to = parse_date(args.date_to or input("End date   (YYYY-MM-DD): "))

    if date_from > date_to:
        raise SystemExit("Start date is after end date.")
    return report_type, date_from, date_to


def main():
    if not DB_PATH.exists():
        raise SystemExit("Database not found. Run src/load_db.py first.")

    report_type, date_from, date_to = get_args()

    span = (date_to - date_from).days + 1
    prev_to = date_from - timedelta(days=1)
    prev_from = prev_to - timedelta(days=span - 1)

    conn = sqlite3.connect(DB_PATH)

    orders, customers, revenue = conn.execute(
        TOTALS_SQL, (str(date_from), str(date_to))
    ).fetchone()
    p_orders, p_customers, p_revenue = conn.execute(
        TOTALS_SQL, (str(prev_from), str(prev_to))
    ).fetchone()

    if orders == 0:
        print("\nNo orders found in that range. Try a wider window.")
        conn.close()
        return

    width = 62
    print("\n" + "=" * width)
    print(f"{report_type.upper()} REPORT   {date_from} to {date_to}")
    print(f"compared with          {prev_from} to {prev_to}")
    print("=" * width)

    print(f"\n{'Metric':<20}{'Current':>14}{'Previous':>14}{'Change':>14}")
    print("-" * width)
    rows = [
        ("Total orders", orders, p_orders, "{:,.0f}"),
        ("Revenue", revenue, p_revenue, "{:,.2f}"),
        ("Unique customers", customers, p_customers, "{:,.0f}"),
    ]
    for label, cur, prev, fmt in rows:
        print(f"{label:<20}{fmt.format(cur):>14}{fmt.format(prev):>14}"
              f"{fmt_change(pct_change(cur, prev)):>14}")

    print(f"\nAverage order value: {revenue / orders:,.2f}")

    print(f"\nTop 3 products")
    print("-" * width)
    for i, (name, units, rev) in enumerate(
        conn.execute(TOP_PRODUCTS_SQL, (str(date_from), str(date_to))), start=1
    ):
        print(f"{i}. {name:<38}{units:>6} units{rev:>14,.2f}")

    print(f"\nBreakdown ({report_type})")
    print("-" * width)
    print(f"{'Period':<16}{'Orders':>10}{'Revenue':>18}")
    for bucket, cnt, rev in conn.execute(
        BUCKET_SQL, (BUCKET_FORMAT[report_type], str(date_from), str(date_to))
    ):
        print(f"{bucket:<16}{cnt:>10}{rev:>18,.2f}")

    print("=" * width + "\n")
    conn.close()


if __name__ == "__main__":
    main()
