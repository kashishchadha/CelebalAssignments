"""Edge case tests.

Each of the four scenarios in the brief is checked twice: once against the
cleaning layer (what does the Python code do with the bad row) and once against
the database (does the schema stop it getting in at all).

Run with:  pytest -v
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import config as cfg
from src import clean_data as cd


@pytest.fixture
def orders():
    return pd.DataFrame([
        {"order_id": "ORD000001", "customer_id": "CUST00001",
         "order_date": "2025-01-10 10:00:00", "status": "DELIVERED",
         "region_code": "NORTH", "payment_method": "UPI"},
    ])


@pytest.fixture
def products():
    return pd.DataFrame([
        {"product_id": "PROD00001", "product_name": "  laptop PRO  ",
         "category": "Electronics", "subcategory": "Laptops", "cost_price": "50000"},
    ])


@pytest.fixture
def db():
    """Empty database built from the real schema."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((cfg.SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    conn.execute(
        "INSERT INTO customers VALUES ('CUST00001', 'Test User', 'a@b.com', '2024-12-01', 'REGULAR')"
    )
    conn.execute(
        "INSERT INTO products VALUES ('PROD00001', 'Laptop Pro', 'Electronics', 'Laptops', 50000)"
    )
    conn.execute(
        "INSERT INTO orders VALUES ('ORD000001', 'CUST00001', '2025-01-10 10:00:00',"
        " 'DELIVERED', 'NORTH', 'UPI')"
    )
    conn.commit()
    yield conn
    conn.close()


def item(**overrides):
    row = {
        "order_item_id": "ITEM0000001",
        "order_id": "ORD000001",
        "product_id": "PROD00001",
        "quantity": "2",
        "unit_price": "1000",
        "discount_percent": "10",
    }
    row.update(overrides)
    return row


# --- 1. order_item pointing at an order that does not exist -------------------

def test_orphan_order_id_is_detected(orders, products):
    df = pd.DataFrame([item(order_id="ORD999999")])
    result = cd.check_referential_integrity(df, orders, products)
    assert result["orphan_order_ids"] == ["ITEM0000001"]


def test_orphan_order_id_is_moved_to_rejected_file(orders, products):
    df = pd.DataFrame([item(), item(order_item_id="ITEM0000002", order_id="ORD999999")])
    clean, rejected = cd.clean_order_items(df, orders, products)
    assert list(clean["order_item_id"]) == ["ITEM0000001"]
    assert list(rejected["order_item_id"]) == ["ITEM0000002"]


def test_database_rejects_orphan_order_id(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO order_items VALUES ('ITEM0000009', 'ORD999999', 'PROD00001',"
            " 1, 100, 0, 0, 100)"
        )


# --- 2. discount_percent above 100 -------------------------------------------

def test_discount_above_100_is_clipped(orders, products):
    df = pd.DataFrame([item(discount_percent="150")])
    clean, _ = cd.clean_order_items(df, orders, products)
    assert clean.iloc[0]["discount_percent"] == 100
    # a fully discounted line contributes nothing, it must not go negative
    assert clean.iloc[0]["line_revenue"] == 0.0


def test_negative_discount_is_clipped_to_zero(orders, products):
    df = pd.DataFrame([item(discount_percent="-20")])
    clean, _ = cd.clean_order_items(df, orders, products)
    assert clean.iloc[0]["discount_percent"] == 0


def test_database_rejects_discount_above_100(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO order_items VALUES ('ITEM0000009', 'ORD000001', 'PROD00001',"
            " 1, 100, 150, 0, 100)"
        )


# --- 3. quantity of zero ------------------------------------------------------

def test_zero_quantity_row_is_dropped(orders, products):
    df = pd.DataFrame([item(quantity="0")])
    clean, _ = cd.clean_order_items(df, orders, products)
    assert clean.empty


def test_negative_quantity_is_kept_and_flagged_as_return(orders, products):
    df = pd.DataFrame([item(quantity="-3")])
    clean, _ = cd.clean_order_items(df, orders, products)
    assert clean.iloc[0]["is_return"] == 1
    assert clean.iloc[0]["line_revenue"] < 0


def test_database_rejects_zero_quantity(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO order_items VALUES ('ITEM0000009', 'ORD000001', 'PROD00001',"
            " 0, 100, 0, 0, 0)"
        )


# --- 4. order_date in the future ---------------------------------------------

def test_future_order_date_is_reported_not_dropped():
    future = (pd.Timestamp.now() + pd.Timedelta(days=45)).strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([{
        "order_id": "ORD000002", "customer_id": "CUST00001", "order_date": future,
        "status": "PLACED", "region_code": "SOUTH", "payment_method": "CARD",
    }])
    clean = cd.clean_orders(df)
    assert len(clean) == 1
    assert cd.issues["orders_future_dated"] == 1


# --- supporting cleaning rules ------------------------------------------------

def test_dd_mm_yyyy_dates_are_converted():
    df = pd.DataFrame([{
        "order_id": "ORD000003", "customer_id": "CUST00001", "order_date": "15-03-2025",
        "status": "SHIPPED", "region_code": "EAST", "payment_method": "COD",
    }])
    clean = cd.clean_orders(df)
    assert clean.iloc[0]["order_date"] == "2025-03-15 00:00:00"


def test_blank_and_literal_null_customer_ids_become_missing():
    df = pd.DataFrame([
        {"order_id": "ORD000004", "customer_id": "", "order_date": "2025-01-01 09:00:00",
         "status": "PLACED", "region_code": "WEST", "payment_method": "UPI"},
        {"order_id": "ORD000005", "customer_id": "NULL", "order_date": "2025-01-02 09:00:00",
         "status": "PLACED", "region_code": "WEST", "payment_method": "UPI"},
    ])
    clean = cd.clean_orders(df)
    assert clean["customer_id"].isna().all()


def test_product_names_are_normalised(products):
    clean = cd.clean_products(products)
    assert clean.iloc[0]["product_name"] == "Laptop Pro"


def test_invalid_emails_are_listed():
    df = pd.DataFrame([
        {"customer_id": "CUST00001", "email": "valid.user@gmail.com"},
        {"customer_id": "CUST00002", "email": "no-at-sign.gmail.com"},
        {"customer_id": "CUST00003", "email": "missing-domain@"},
    ])
    assert cd.validate_emails(df) == ["CUST00002", "CUST00003"]
