"""Paths and knobs used across the project. Change values here, not inside the scripts."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"
REPORTS_DIR = BASE_DIR / "reports"
SQL_DIR = BASE_DIR / "sql"

DB_PATH = BASE_DIR / "data" / "ecommerce.db"

# --- data generation -------------------------------------------------------
SEED = 42

N_CUSTOMERS = 800
N_PRODUCTS = 500
N_ORDERS = 3000
MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 4

# orders are spread over this window so year-over-year queries have data on both sides
DATA_START = "2023-07-01"
DATA_END = "2025-08-31"

# share of rows that get deliberately broken (see README "Dirty data" section)
PCT_NULL_CUSTOMER_ID = 0.05
PCT_NEGATIVE_QUANTITY = 0.03
PCT_BAD_DATE_FORMAT = 0.02
PCT_MESSY_PRODUCT_NAME = 0.08
PCT_INVALID_EMAIL = 0.02
PCT_INVALID_DISCOUNT = 0.01
N_RETURN_PRONE_PRODUCTS = 20   # products with an unusually high return rate
PCT_RETURN_PRONE = 0.60
PCT_ZERO_QUANTITY = 0.005
N_ORPHAN_ORDER_ITEMS = 25
N_FUTURE_DATED_ORDERS = 12

ORDER_STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
STATUS_WEIGHTS = [0.10, 0.15, 0.55, 0.10, 0.10]

REGIONS = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
CUSTOMER_TYPE_WEIGHTS = [0.6, 0.3, 0.1]
PAYMENT_METHODS = ["UPI", "CARD", "NETBANKING", "COD", "WALLET"]

CATEGORIES = {
    "Electronics": ["Mobiles", "Laptops", "Audio", "Cameras"],
    "Clothing": ["Men", "Women", "Kids", "Footwear"],
    "Home": ["Kitchen", "Furniture", "Decor", "Bedding"],
    "Books": ["Fiction", "Academic", "Comics", "Self Help"],
}


def ensure_dirs():
    for d in (RAW_DIR, CLEAN_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
