"""Cleans the raw CSVs and writes a data quality report.

Rules applied (and why):

orders
  - order_date arrives in two formats. Both are parsed and everything is written
    back as YYYY-MM-DD HH:MM:SS. Rows that still fail to parse are dropped and
    counted, because a revenue row without a date cannot be placed on a timeline.
  - order dates in the future are counted and reported but not removed, since a
    pre-order is legitimate; the report makes the volume visible.
  - missing customer_id is stored as a real NULL instead of "" or the string
    "NULL". The order itself is still valid revenue, so the row is kept; every
    customer level query filters with `customer_id IS NOT NULL`.

products
  - product_name is trimmed, inner whitespace collapsed and title cased.

order_items
  - negative quantity is a return, not an error, so it is kept and marked with
    is_return = 1.
  - discount_percent outside 0-100 is clipped to the valid range.
  - rows pointing at an order_id that does not exist are moved out to
    data/clean/rejected_order_items.csv rather than silently deleted.

customers
  - invalid emails are reported but the customer row is kept, since the rest of
    the record is still usable.
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
import config as cfg

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")

# collected as we go, dumped at the end
issues = {}


def _parse_dates(series: pd.Series) -> pd.Series:
    """Handle YYYY-MM-DD HH:MM:SS and DD-MM-YYYY in the same column."""
    parsed = pd.to_datetime(series, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    fallback = pd.to_datetime(series, format="%d-%m-%Y", errors="coerce")
    return parsed.fillna(fallback)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before = len(df)

    df["customer_id"] = (
        df["customer_id"].astype("string").str.strip().replace({"": None, "NULL": None, "nan": None})
    )
    issues["orders_missing_customer_id"] = int(df["customer_id"].isna().sum())

    raw_dates = df["order_date"].astype("string").str.strip()
    wrong_format = raw_dates.str.match(r"^\d{2}-\d{2}-\d{4}$").fillna(False)
    issues["orders_wrong_date_format"] = int(wrong_format.sum())

    df["order_date"] = _parse_dates(raw_dates)
    unparsed = int(df["order_date"].isna().sum())
    issues["orders_unparsable_date_dropped"] = unparsed
    df = df.dropna(subset=["order_date"])

    # A future order date is not necessarily corrupt (pre-orders exist), so the
    # rows are kept and reported rather than dropped.
    future = df["order_date"] > pd.Timestamp.now()
    issues["orders_future_dated"] = int(future.sum())

    df["status"] = df["status"].astype("string").str.strip().str.upper()
    bad_status = ~df["status"].isin(cfg.ORDER_STATUSES)
    issues["orders_unknown_status"] = int(bad_status.sum())

    dupes = int(df.duplicated(subset=["order_id"]).sum())
    issues["orders_duplicate_ids_removed"] = dupes
    df = df.drop_duplicates(subset=["order_id"])

    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    issues["orders_rows_in"] = before
    issues["orders_rows_out"] = len(df)
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    raw = df["product_name"].astype("string")
    normalised = raw.str.strip().str.replace(r"\s+", " ", regex=True).str.title()

    issues["products_names_normalised"] = int((raw != normalised).sum())
    df["product_name"] = normalised

    df["category"] = df["category"].astype("string").str.strip().str.title()
    df["subcategory"] = df["subcategory"].astype("string").str.strip().str.title()
    df["cost_price"] = pd.to_numeric(df["cost_price"], errors="coerce").fillna(0).round(2)

    issues["products_rows_out"] = len(df)
    return df


def validate_emails(df: pd.DataFrame) -> list:
    """Return the customer_ids whose email does not look like an address."""
    emails = df["email"].astype("string").fillna("")
    invalid = ~emails.str.match(EMAIL_PATTERN).fillna(False)
    return df.loc[invalid, "customer_id"].tolist()


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["customer_name"] = df["customer_name"].astype("string").str.strip().str.title()
    df["email"] = df["email"].astype("string").str.strip().str.lower()
    df["customer_type"] = df["customer_type"].astype("string").str.strip().str.upper()
    df["registration_date"] = pd.to_datetime(
        df["registration_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    bad_emails = validate_emails(df)
    issues["customers_invalid_emails"] = len(bad_emails)
    issues["customers_invalid_email_ids"] = bad_emails[:20]  # sample for the report
    issues["customers_rows_out"] = len(df)
    return df


def check_referential_integrity(order_items: pd.DataFrame, orders: pd.DataFrame,
                                products: pd.DataFrame) -> dict:
    """Find order_items whose parent rows do not exist."""
    valid_orders = set(orders["order_id"])
    valid_products = set(products["product_id"])
    return {
        "orphan_order_ids": order_items.loc[
            ~order_items["order_id"].isin(valid_orders), "order_item_id"
        ].tolist(),
        "orphan_product_ids": order_items.loc[
            ~order_items["product_id"].isin(valid_products), "order_item_id"
        ].tolist(),
    }


def clean_order_items(df: pd.DataFrame, orders: pd.DataFrame,
                      products: pd.DataFrame) -> tuple:
    df = df.copy()
    before = len(df)

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0).round(2)
    df["discount_percent"] = pd.to_numeric(df["discount_percent"], errors="coerce").fillna(0)

    out_of_range = ((df["discount_percent"] < 0) | (df["discount_percent"] > 100)).sum()
    issues["items_discount_clipped"] = int(out_of_range)
    df["discount_percent"] = df["discount_percent"].clip(0, 100)

    df["is_return"] = (df["quantity"] < 0).astype(int)
    issues["items_returns_flagged"] = int(df["is_return"].sum())

    zero_qty = int((df["quantity"] == 0).sum())
    issues["items_zero_quantity_dropped"] = zero_qty
    df = df[df["quantity"] != 0]

    integrity = check_referential_integrity(df, orders, products)
    bad_ids = set(integrity["orphan_order_ids"]) | set(integrity["orphan_product_ids"])
    issues["items_orphan_order_id"] = len(integrity["orphan_order_ids"])
    issues["items_orphan_product_id"] = len(integrity["orphan_product_ids"])

    rejected = df[df["order_item_id"].isin(bad_ids)]
    df = df[~df["order_item_id"].isin(bad_ids)]

    df["line_revenue"] = (
        df["quantity"] * df["unit_price"] * (1 - df["discount_percent"] / 100)
    ).round(2)

    issues["items_rows_in"] = before
    issues["items_rows_out"] = len(df)
    return df, rejected


def write_report():
    lines = [
        "# Data Quality Report",
        "",
        "Generated by `src/clean_data.py`. Counts refer to the raw files in `data/raw`.",
        "",
        "| Check | Value |",
        "| --- | --- |",
    ]
    for key, value in issues.items():
        if isinstance(value, list):
            value = ", ".join(value) if value else "-"
        lines.append(f"| {key.replace('_', ' ')} | {value} |")

    (cfg.REPORTS_DIR / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")
    (cfg.REPORTS_DIR / "data_quality_report.json").write_text(
        json.dumps(issues, indent=2), encoding="utf-8"
    )


def main():
    cfg.ensure_dirs()
    print("Reading raw files from", cfg.RAW_DIR)

    orders = pd.read_csv(cfg.RAW_DIR / "orders.csv", dtype=str, keep_default_na=False)
    products = pd.read_csv(cfg.RAW_DIR / "products.csv", dtype=str, keep_default_na=False)
    customers = pd.read_csv(cfg.RAW_DIR / "customers.csv", dtype=str, keep_default_na=False)
    order_items = pd.read_csv(cfg.RAW_DIR / "order_items.csv", dtype=str, keep_default_na=False)

    orders = clean_orders(orders)
    products = clean_products(products)
    customers = clean_customers(customers)
    order_items, rejected = clean_order_items(order_items, orders, products)

    orders.to_csv(cfg.CLEAN_DIR / "orders.csv", index=False)
    products.to_csv(cfg.CLEAN_DIR / "products.csv", index=False)
    customers.to_csv(cfg.CLEAN_DIR / "customers.csv", index=False)
    order_items.to_csv(cfg.CLEAN_DIR / "order_items.csv", index=False)
    rejected.to_csv(cfg.CLEAN_DIR / "rejected_order_items.csv", index=False)

    write_report()

    print("Cleaned files written to", cfg.CLEAN_DIR)
    for key, value in issues.items():
        if not isinstance(value, list):
            print(f"  {key:<36} {value}")
    print("\nReport: reports/data_quality_report.md")


if __name__ == "__main__":
    main()
