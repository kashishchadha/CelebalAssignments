"""Generates the four raw CSV files.

The data is deliberately imperfect - the percentages of each problem are set in
config.py. Everything here uses the standard library only, so the generated data
does not depend on any package versions.

Referential integrity: order_items are always built by picking an order_id from
the list of orders we just created, so the link is correct by construction. On
top of that we push in a fixed number of orphan rows (N_ORPHAN_ORDER_ITEMS) so
the validation step in clean_data.py has something real to catch.
"""

import csv
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import config as cfg

FIRST_NAMES = [
    "Aarav", "Diya", "Vivaan", "Ananya", "Aditya", "Ishaan", "Kavya", "Rohan",
    "Meera", "Arjun", "Sana", "Kabir", "Nisha", "Yash", "Priya", "Dev",
    "Tara", "Manav", "Riya", "Karan", "Neha", "Sahil", "Anjali", "Varun",
]
LAST_NAMES = [
    "Sharma", "Verma", "Nair", "Iyer", "Patel", "Reddy", "Gupta", "Mehta",
    "Bose", "Kapoor", "Joshi", "Rao", "Chopra", "Malhotra", "Das", "Sinha",
]
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com"]

PRODUCT_WORDS = {
    "Electronics": ["Pro", "Max", "Lite", "Ultra", "Neo", "Plus", "Air"],
    "Clothing": ["Slim Fit", "Regular", "Classic", "Casual", "Formal"],
    "Home": ["Premium", "Compact", "Deluxe", "Basic", "Wooden"],
    "Books": ["Volume 1", "Volume 2", "Revised Edition", "Illustrated"],
}
PRODUCT_NOUNS = {
    "Electronics": ["Smartphone", "Headphone", "Laptop", "Camera", "Speaker", "Charger"],
    "Clothing": ["Shirt", "Jeans", "Kurta", "Jacket", "Sneakers", "Saree"],
    "Home": ["Chair", "Lamp", "Cookware Set", "Bedsheet", "Wall Clock", "Mixer"],
    "Books": ["Data Science Handbook", "Short Stories", "Physics Guide", "Comic Pack"],
}


def _daterange_random(start: datetime, end: datetime) -> datetime:
    delta = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta))


def _messy(name: str) -> str:
    """Break a clean product name the way a bad upstream feed would."""
    style = random.choice(["spaces", "upper", "lower", "mixed"])
    if style == "spaces":
        return "  " + name + "   "
    if style == "upper":
        return name.upper()
    if style == "lower":
        return name.lower()
    return "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(name))


def generate_customers(n):
    rows = []
    reg_start = datetime.strptime(cfg.DATA_START, "%Y-%m-%d") - timedelta(days=180)
    reg_end = datetime.strptime(cfg.DATA_END, "%Y-%m-%d") - timedelta(days=30)
    for i in range(1, n + 1):
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@{random.choice(EMAIL_DOMAINS)}"
        if random.random() < cfg.PCT_INVALID_EMAIL:
            email = random.choice([
                email.replace("@", "."),            # missing @
                email.split("@")[0],                # no domain at all
                email.split("@")[0] + "@",          # domain missing after @
            ])
        rows.append({
            "customer_id": f"CUST{i:05d}",
            "customer_name": name,
            "email": email,
            "registration_date": _daterange_random(reg_start, reg_end).strftime("%Y-%m-%d"),
            "customer_type": random.choices(cfg.CUSTOMER_TYPES, cfg.CUSTOMER_TYPE_WEIGHTS)[0],
        })
    return rows


def generate_products(n):
    rows = []
    categories = list(cfg.CATEGORIES)
    for i in range(1, n + 1):
        category = random.choice(categories)
        subcategory = random.choice(cfg.CATEGORIES[category])
        name = f"{random.choice(PRODUCT_NOUNS[category])} {random.choice(PRODUCT_WORDS[category])}"
        if random.random() < cfg.PCT_MESSY_PRODUCT_NAME:
            name = _messy(name)
        base = {"Electronics": 8000, "Clothing": 700, "Home": 1500, "Books": 250}[category]
        rows.append({
            "product_id": f"PROD{i:05d}",
            "product_name": name,
            "category": category,
            "subcategory": subcategory,
            "cost_price": round(base * random.uniform(0.5, 2.5), 2),
        })
    return rows


def generate_orders(n, customer_ids):
    rows = []
    start = datetime.strptime(cfg.DATA_START, "%Y-%m-%d")
    end = datetime.strptime(cfg.DATA_END, "%Y-%m-%d")
    for i in range(1, n + 1):
        order_dt = _daterange_random(start, end)
        order_date = order_dt.strftime("%Y-%m-%d %H:%M:%S")
        if random.random() < cfg.PCT_BAD_DATE_FORMAT:
            order_date = order_dt.strftime("%d-%m-%Y")

        customer_id = random.choice(customer_ids)
        if random.random() < cfg.PCT_NULL_CUSTOMER_ID:
            customer_id = random.choice(["", "NULL"])

        rows.append({
            "order_id": f"ORD{i:06d}",
            "customer_id": customer_id,
            "order_date": order_date,
            "status": random.choices(cfg.ORDER_STATUSES, cfg.STATUS_WEIGHTS)[0],
            "region_code": random.choice(cfg.REGIONS),
            "payment_method": random.choice(cfg.PAYMENT_METHODS),
        })
    # a handful of orders dated after today, to exercise the future-date check
    for k in range(cfg.N_FUTURE_DATED_ORDERS):
        future = datetime.now() + timedelta(days=random.randint(5, 90))
        rows.append({
            "order_id": f"ORD8{k:05d}",
            "customer_id": random.choice(customer_ids),
            "order_date": future.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "PLACED",
            "region_code": random.choice(cfg.REGIONS),
            "payment_method": random.choice(cfg.PAYMENT_METHODS),
        })

    return rows


def generate_order_items(orders, products):
    rows = []
    order_ids = [o["order_id"] for o in orders]
    price_lookup = {p["product_id"]: p["cost_price"] for p in products}
    product_ids = list(price_lookup)
    # a small set of products that customers send back far more often, so the
    # return analysis has real signal instead of noise spread evenly everywhere
    problem_products = set(random.sample(product_ids, cfg.N_RETURN_PRONE_PRODUCTS))
    item_no = 0

    for order_id in order_ids:
        for _ in range(random.randint(cfg.MIN_ITEMS_PER_ORDER, cfg.MAX_ITEMS_PER_ORDER)):
            item_no += 1
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 5)
            return_rate = (cfg.PCT_RETURN_PRONE if product_id in problem_products
                           else cfg.PCT_NEGATIVE_QUANTITY)
            if random.random() < return_rate:
                quantity = -quantity
            elif random.random() < cfg.PCT_ZERO_QUANTITY:
                quantity = 0

            discount = random.choices([0, 5, 10, 15, 20, 30, 50], [30, 20, 20, 12, 10, 6, 2])[0]
            if random.random() < cfg.PCT_INVALID_DISCOUNT:
                discount = random.choice([-10, 110, 150])
            rows.append({
                "order_item_id": f"ITEM{item_no:07d}",
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                # selling price sits above cost price
                "unit_price": round(price_lookup[product_id] * random.uniform(1.15, 1.6), 2),
                "discount_percent": discount,
            })

    # orphan rows: order_ids that were never created
    for k in range(cfg.N_ORPHAN_ORDER_ITEMS):
        item_no += 1
        product_id = random.choice(product_ids)
        rows.append({
            "order_item_id": f"ITEM{item_no:07d}",
            "order_id": f"ORD9{k:05d}",
            "product_id": product_id,
            "quantity": random.randint(1, 3),
            "unit_price": round(price_lookup[product_id] * 1.3, 2),
            "discount_percent": 0,
        })

    random.shuffle(rows)
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {path.name:<20} {len(rows):>6} rows")


def main():
    random.seed(cfg.SEED)
    cfg.ensure_dirs()

    customers = generate_customers(cfg.N_CUSTOMERS)
    products = generate_products(cfg.N_PRODUCTS)
    orders = generate_orders(cfg.N_ORDERS, [c["customer_id"] for c in customers])
    order_items = generate_order_items(orders, products)

    print("Writing raw files to", cfg.RAW_DIR)
    write_csv(customers, cfg.RAW_DIR / "customers.csv")
    write_csv(products, cfg.RAW_DIR / "products.csv")
    write_csv(orders, cfg.RAW_DIR / "orders.csv")
    write_csv(order_items, cfg.RAW_DIR / "order_items.csv")


if __name__ == "__main__":
    main()
