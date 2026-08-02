"""
generate_datasets.py
--------------------
Regenerates the three CSV files in ../data.

The data is *deliberately messy* (nulls, duplicates, whitespace, bad casing,
mixed date formats) so that the cleaning steps in the notebooks have real work
to do. Run it only if you want to reset the data:

    python scripts/generate_datasets.py
"""

import os
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------- superstore
def build_superstore(n_rows: int = 320) -> pd.DataFrame:
    segments = ["Consumer", "Corporate", "Home Office"]
    regions = ["West", "East", "Central", "South"]
    ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
    categories = {
        "Furniture": ["Bookcases", "Chairs", "Tables", "Furnishings"],
        "Office Supplies": ["Binders", "Paper", "Storage", "Art", "Appliances"],
        "Technology": ["Phones", "Machines", "Accessories", "Copiers"],
    }
    cities = {
        "West": ["Los Angeles", "Seattle", "San Francisco", "Phoenix"],
        "East": ["New York City", "Philadelphia", "Newark", "Boston"],
        "Central": ["Chicago", "Dallas", "Houston", "Detroit"],
        "South": ["Miami", "Atlanta", "Richmond", "Jacksonville"],
    }
    first = ["Aaron", "Bella", "Chris", "Divya", "Ethan", "Farah", "Gopal",
             "Hina", "Ishan", "Julia", "Karan", "Lena", "Manav", "Nisha"]
    last = ["Sharma", "Mehta", "Coleman", "Iyer", "Blake", "Nair", "Rossi",
            "Khan", "Sullivan", "Patel", "Grant", "Verma"]

    start = date(2023, 1, 1)
    rows = []
    for i in range(1, n_rows + 1):
        region = random.choice(regions)
        cat = random.choice(list(categories))
        sub = random.choice(categories[cat])
        order_dt = start + timedelta(days=random.randint(0, 700))
        ship_dt = order_dt + timedelta(days=random.randint(1, 7))
        cust = f"{random.choice(first)} {random.choice(last)}"
        rows.append(
            {
                "row_id": i,
                "order_id": f"IN-{order_dt.year}-{100000 + i}",
                "order_date": order_dt.strftime("%d/%m/%Y"),
                "ship_date": ship_dt.strftime("%d/%m/%Y"),
                "ship_mode": random.choice(ship_modes),
                "customer_id": f"CU-{1000 + (i % 90)}",
                "customer_name": cust,
                "segment": random.choice(segments),
                "country": "United States",
                "city": random.choice(cities[region]),
                "region": region,
                "product_id": f"{cat[:3].upper()}-{sub[:2].upper()}-{2000 + (i % 60)}",
                "category": cat,
                "sub_category": sub,
                "product_name": f"{sub} Model {random.randint(100, 999)}",
                "unit_price": round(random.uniform(5, 1200), 2),
                "quantity": random.randint(1, 12),
                "discount": random.choice([0, 0, 0, 0.1, 0.15, 0.2, 0.3]),
            }
        )

    df = pd.DataFrame(rows)

    # ---- inject messiness -------------------------------------------------
    # 1. missing values
    df.loc[df.sample(22, random_state=1).index, "unit_price"] = np.nan
    df.loc[df.sample(14, random_state=2).index, "quantity"] = np.nan
    df.loc[df.sample(18, random_state=3).index, "city"] = np.nan
    df.loc[df.sample(9, random_state=4).index, "segment"] = np.nan
    df.loc[df.sample(6, random_state=5).index, "discount"] = np.nan
    df.loc[df.sample(4, random_state=6).index, "customer_name"] = np.nan

    # 2. untidy strings (leading/trailing spaces + random casing)
    dirty_idx = df.sample(30, random_state=7).index
    df.loc[dirty_idx, "ship_mode"] = df.loc[dirty_idx, "ship_mode"].map(
        lambda s: f"  {s.upper()} " if isinstance(s, str) else s
    )

    # 3. exact duplicate rows (same row repeated, row_id included)
    dupes = df.sample(15, random_state=8).copy()
    # 4. near duplicates: same order_id + product_id, different row_id
    near = df.sample(10, random_state=9).copy()
    near["row_id"] = range(n_rows + 1, n_rows + 11)

    out = pd.concat([df, dupes, near], ignore_index=True)
    out = out.sample(frac=1, random_state=10).reset_index(drop=True)
    return out


# ------------------------------------------------------- customer master/inc
def build_customers():
    master = pd.DataFrame(
        [
            # customer_id, name, email, city, segment, phone, updated_at
            ("C001", "Aarav Sharma",   "aarav.sharma@example.com",  "Mumbai",    "Consumer",    "9810000001", "2024-01-10"),
            ("C002", "Bhavna Mehta",   "bhavna.mehta@example.com",  "Pune",      "Corporate",   "9810000002", "2024-01-10"),
            ("C003", "Chirag Iyer",    "chirag.iyer@example.com",   "Bengaluru", "Consumer",    "9810000003", "2024-01-11"),
            ("C004", "Divya Nair",     "divya.nair@example.com",    "Kochi",     "Home Office", "9810000004", "2024-01-11"),
            ("C005", "Esha Khan",      "esha.khan@example.com",     "Delhi",     "Corporate",   None,         "2024-01-12"),
            ("C006", "Farhan Ali",     "farhan.ali@example.com",    "Hyderabad", "Consumer",    "9810000006", "2024-01-12"),
            ("C007", "Gita Verma",     None,                        "Jaipur",    "Consumer",    "9810000007", "2024-01-13"),
            ("C008", "Harsh Patel",    "harsh.patel@example.com",   "Ahmedabad", "Corporate",   "9810000008", "2024-01-13"),
            ("C009", "Ishita Rao",     "ishita.rao@example.com",    None,        "Home Office", "9810000009", "2024-01-14"),
            ("C010", "Jatin Grover",   "jatin.grover@example.com",  "Chandigarh","Consumer",    "9810000010", "2024-01-14"),
            ("C011", "Kavya Menon",    "kavya.menon@example.com",   "Chennai",   "Corporate",   "9810000011", "2024-01-15"),
            ("C012", "Lakshay Bhatia", "lakshay.b@example.com",     "Meerut",    "Consumer",    "9810000012", "2024-01-15"),
            ("C013", "Meera Joshi",    "meera.joshi@example.com",   "Indore",    "Home Office", "9810000013", "2024-01-16"),
            ("C014", "Nikhil Bose",    "nikhil.bose@example.com",   "Kolkata",   "Consumer",    "9810000014", "2024-01-16"),
            ("C015", "Ojas Kulkarni",  "ojas.k@example.com",        "Nagpur",    "Corporate",   "9810000015", "2024-01-17"),
            # duplicate rows inside the master file (to be cleaned)
            ("C003", "Chirag Iyer",    "chirag.iyer@example.com",   "Bengaluru", "Consumer",    "9810000003", "2024-01-11"),
            ("C010", "Jatin Grover",   "jatin.grover@example.com",  "Chandigarh","Consumer",    "9810000010", "2024-01-14"),
            # a row with no key at all (to be dropped)
            (None,   "Unknown Person", "ghost@example.com",         "Nowhere",   "Consumer",    "9999999999", "2024-01-17"),
        ],
        columns=["customer_id", "name", "email", "city", "segment", "phone", "updated_at"],
    )

    incremental = pd.DataFrame(
        [
            # --- UPDATES to existing customers (changed city / segment / email)
            ("C002", "Bhavna Mehta",  "bhavna.mehta@example.com", "Bengaluru", "Corporate",   "9810000002", "2024-03-02"),
            ("C005", "Esha Khan",     "esha.khan@corp.com",       "Delhi",     "Home Office", "9820000005", "2024-03-02"),
            ("C009", "Ishita Rao",    "ishita.rao@example.com",   "Goa",       "Home Office", "9810000009", "2024-03-03"),
            ("C012", "Lakshay Bhatia","lakshay.b@example.com",    "Noida",     "Corporate",   "9810000012", "2024-03-03"),
            # --- an "update" that changes nothing (no-op, should not create SCD2 version)
            ("C001", "Aarav Sharma",  "aarav.sharma@example.com", "Mumbai",    "Consumer",    "9810000001", "2024-03-04"),
            # --- BRAND NEW customers
            ("C016", "Priya Deshmukh","priya.d@example.com",      "Surat",     "Consumer",    "9810000016", "2024-03-04"),
            ("C017", "Rahul Sinha",   "rahul.sinha@example.com",  "Lucknow",   "Corporate",   "9810000017", "2024-03-05"),
            ("C018", "Sneha Kapoor",  None,                       "Bhopal",    "Consumer",    "9810000018", "2024-03-05"),
            # --- LATE-ARRIVING / OUT-OF-ORDER duplicate for C002 (older timestamp)
            ("C002", "Bhavna Mehta",  "bhavna.mehta@example.com", "Pune",      "Corporate",   "9810000002", "2024-02-28"),
            # --- exact duplicate inside the incremental batch
            ("C017", "Rahul Sinha",   "rahul.sinha@example.com",  "Lucknow",   "Corporate",   "9810000017", "2024-03-05"),
        ],
        columns=["customer_id", "name", "email", "city", "segment", "phone", "updated_at"],
    )
    return master, incremental


if __name__ == "__main__":
    store = build_superstore()
    store.to_csv(os.path.join(DATA_DIR, "superstore_orders.csv"), index=False)

    master, incremental = build_customers()
    master.to_csv(os.path.join(DATA_DIR, "customer_master.csv"), index=False)
    incremental.to_csv(os.path.join(DATA_DIR, "customer_incremental.csv"), index=False)

    print(f"superstore_orders.csv     -> {store.shape}")
    print(f"customer_master.csv       -> {master.shape}")
    print(f"customer_incremental.csv  -> {incremental.shape}")
    print(f"Written to: {os.path.abspath(DATA_DIR)}")
