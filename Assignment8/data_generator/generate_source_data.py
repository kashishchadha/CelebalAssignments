import os
import csv
import random
from datetime import datetime, timedelta
from config.settings import CRM_INBOUND_DIR, ERP_INBOUND_DIR, init_directories

def generate_datasets():
    init_directories()
    random.seed(42)
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Dallas", "Seattle", "Miami"]
    states = ["NY", "CA", "IL", "TX", "AZ", "TX", "WA", "FL"]
    segments = ["Consumer", "Corporate", "Home Office", "VIP"]
    categories = {
        "Electronics": ["Smartphones", "Laptops", "Tablets", "Headphones"],
        "Apparel": ["Men Wear", "Women Wear", "Footwear", "Accessories"],
        "Home": ["Furniture", "Kitchenware", "Bedding", "Decor"]
    }
    channels = ["Web", "Mobile App", "In-Store", "Phone Support"]
    sentiments = ["Positive", "Neutral", "Negative"]
    store_types = ["Flagship", "Superstore", "Express", "Outlet"]
    payment_methods = ["Credit Card", "Debit Card", "UPI", "PayPal", "Cash"]
    order_statuses = ["COMPLETED", "DELIVERED", "PROCESSING", "CANCELLED", "RETURNED"]

    batch1_crm = CRM_INBOUND_DIR / "batch_01"
    batch1_erp = ERP_INBOUND_DIR / "batch_01"
    batch2_crm = CRM_INBOUND_DIR / "batch_02"
    batch2_erp = ERP_INBOUND_DIR / "batch_02"

    for path in [batch1_crm, batch1_erp, batch2_crm, batch2_erp]:
        path.mkdir(parents=True, exist_ok=True)

    base_time = datetime(2024, 1, 1, 10, 0, 0)

    customers_b1 = []
    for i in range(1, 201):
        cid = f"CUST-{i:04d}"
        city_idx = random.randint(0, len(cities) - 1)
        created = base_time + timedelta(days=random.randint(0, 30))
        updated = created
        customers_b1.append([
            cid, f"First_{i}", f"Last_{i}", f"user_{i}@example.com",
            f"+1-555-{random.randint(100,999):03d}-{i:04d}",
            cities[city_idx], states[city_idx], "USA",
            random.choice(segments), round(random.uniform(0.05, 0.85), 2),
            created.strftime("%Y-%m-%d %H:%M:%S"),
            updated.strftime("%Y-%m-%d %H:%M:%S")
        ])
    
    customers_b1.append(["CORRUPT-001", "", "", "invalid_email_at_domain", "", "", "", "", "", "INVALID_SCORE", "2024-01-01", "2024-01-01"])
    customers_b1.append(customers_b1[0])

    with open(batch1_crm / "customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "first_name", "last_name", "email", "phone", "city", "state", "country", "segment", "churn_risk_score", "created_at", "updated_at"])
        writer.writerows(customers_b1)

    interactions_b1 = []
    for i in range(1, 301):
        iid = f"INT-{i:05d}"
        cid = f"CUST-{random.randint(1, 200):04d}"
        ts = base_time + timedelta(days=random.randint(0, 45), hours=random.randint(0, 23))
        interactions_b1.append([
            iid, cid, random.choice(channels), random.choice(sentiments),
            random.randint(0, 3), ts.strftime("%Y-%m-%d %H:%M:%S")
        ])

    with open(batch1_crm / "customer_interactions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["interaction_id", "customer_id", "channel", "sentiment", "support_tickets_count", "interaction_timestamp"])
        writer.writerows(interactions_b1)

    stores_b1 = []
    for i in range(1, 11):
        sid = f"STR-{i:03d}"
        city_idx = i % len(cities)
        opened = base_time - timedelta(days=random.randint(300, 1000))
        stores_b1.append([
            sid, f"Store {cities[city_idx]} #{i}", random.choice(store_types),
            cities[city_idx], states[city_idx], random.randint(15000, 85000),
            f"Manager_{i}", opened.strftime("%Y-%m-%d"),
            base_time.strftime("%Y-%m-%d %H:%M:%S")
        ])

    with open(batch1_erp / "stores.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["store_id", "store_name", "store_type", "city", "region", "sqft_area", "manager_name", "opened_date", "updated_at"])
        writer.writerows(stores_b1)

    products_b1 = []
    pid_counter = 1
    for cat, subcats in categories.items():
        for sub in subcats:
            for k in range(1, 6):
                pid = f"PROD-{pid_counter:04d}"
                pid_counter += 1
                cost = round(random.uniform(10.0, 500.0), 2)
                msrp = round(cost * random.uniform(1.2, 1.8), 2)
                products_b1.append([
                    pid, f"{sub} Item {k}", cat, sub, cost, msrp,
                    round(random.uniform(3.0, 5.0), 1),
                    base_time.strftime("%Y-%m-%d %H:%M:%S")
                ])

    with open(batch1_erp / "products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_name", "category", "subcategory", "unit_cost", "msrp", "quality_rating", "updated_at"])
        writer.writerows(products_b1)

    orders_b1 = []
    order_items_b1 = []
    returns_b1 = []
    item_id_counter = 1
    return_id_counter = 1

    for i in range(1, 501):
        oid = f"ORD-{i:05d}"
        cid = f"CUST-{random.randint(1, 200):04d}"
        sid = f"STR-{random.randint(1, 10):03d}"
        ots = base_time + timedelta(days=random.randint(1, 40), hours=random.randint(0, 23))
        status = random.choice(order_statuses)
        orders_b1.append([
            oid, cid, sid, status, random.choice(payment_methods),
            ots.strftime("%Y-%m-%d %H:%M:%S"), ots.strftime("%Y-%m-%d %H:%M:%S")
        ])

        num_items = random.randint(1, 4)
        for _ in range(num_items):
            itid = f"ITM-{item_id_counter:06d}"
            item_id_counter += 1
            prod = random.choice(products_b1)
            prod_id = prod[0]
            unit_price = prod[5]
            qty = random.randint(1, 5)
            discount = round(unit_price * qty * random.uniform(0.0, 0.15), 2)
            tax = round((unit_price * qty - discount) * 0.08, 2)
            order_items_b1.append([
                itid, oid, prod_id, qty, unit_price, discount, tax,
                ots.strftime("%Y-%m-%d %H:%M:%S")
            ])

            if status == "RETURNED" or (status == "DELIVERED" and random.random() < 0.08):
                ret_id = f"RET-{return_id_counter:05d}"
                return_id_counter += 1
                r_ts = ots + timedelta(days=random.randint(1, 5))
                returns_b1.append([
                    ret_id, oid, itid, prod_id, cid,
                    random.choice(["Defective Item", "Wrong Size", "Changed Mind", "Late Delivery"]),
                    round(unit_price * qty - discount, 2),
                    r_ts.strftime("%Y-%m-%d %H:%M:%S")
                ])

    with open(batch1_erp / "orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "customer_id", "store_id", "order_status", "payment_method", "order_timestamp", "updated_at"])
        writer.writerows(orders_b1)

    with open(batch1_erp / "order_items.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount", "tax_amount", "updated_at"])
        writer.writerows(order_items_b1)

    with open(batch1_erp / "product_returns.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["return_id", "order_id", "item_id", "product_id", "customer_id", "return_reason", "refund_amount", "return_timestamp"])
        writer.writerows(returns_b1)

    b2_time = base_time + timedelta(days=60)
    
    customers_b2 = []
    for i in range(1, 15):
        cid = f"CUST-{i:04d}"
        updated = b2_time + timedelta(days=random.randint(1, 5))
        city_idx = random.randint(0, len(cities) - 1)
        customers_b2.append([
            cid, f"First_{i}", f"Last_{i}", f"user_{i}_updated@example.com",
            f"+1-555-999-{i:04d}", cities[city_idx], states[city_idx], "USA",
            "VIP", round(random.uniform(0.1, 0.4), 2),
            base_time.strftime("%Y-%m-%d %H:%M:%S"),
            updated.strftime("%Y-%m-%d %H:%M:%S")
        ])

    for i in range(201, 230):
        cid = f"CUST-{i:04d}"
        city_idx = random.randint(0, len(cities) - 1)
        created = b2_time
        customers_b2.append([
            cid, f"NewFirst_{i}", f"NewLast_{i}", f"new_user_{i}@example.com",
            f"+1-555-888-{i:04d}", cities[city_idx], states[city_idx], "USA",
            random.choice(segments), round(random.uniform(0.1, 0.5), 2),
            created.strftime("%Y-%m-%d %H:%M:%S"),
            created.strftime("%Y-%m-%d %H:%M:%S")
        ])

    with open(batch2_crm / "customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "first_name", "last_name", "email", "phone", "city", "state", "country", "segment", "churn_risk_score", "created_at", "updated_at"])
        writer.writerows(customers_b2)

    interactions_b2 = []
    for i in range(301, 400):
        iid = f"INT-{i:05d}"
        cid = f"CUST-{random.randint(1, 220):04d}"
        ts = b2_time + timedelta(days=random.randint(1, 10))
        interactions_b2.append([
            iid, cid, random.choice(channels), random.choice(sentiments),
            random.randint(0, 2), ts.strftime("%Y-%m-%d %H:%M:%S")
        ])

    with open(batch2_crm / "customer_interactions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["interaction_id", "customer_id", "channel", "sentiment", "support_tickets_count", "interaction_timestamp"])
        writer.writerows(interactions_b2)

    stores_b2 = [
        ["STR-001", "Store New York Mega Flagship", "Superstore", "New York", "NY", 95000, "Manager_1_Renamed", "2023-01-01", b2_time.strftime("%Y-%m-%d %H:%M:%S")]
    ]
    with open(batch2_erp / "stores.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["store_id", "store_name", "store_type", "city", "region", "sqft_area", "manager_name", "opened_date", "updated_at"])
        writer.writerows(stores_b2)

    products_b2 = [
        ["PROD-0001", "Smartphones Item 1 Upgraded", "Electronics", "Smartphones", 450.0, 799.99, 4.8, b2_time.strftime("%Y-%m-%d %H:%M:%S")]
    ]
    with open(batch2_erp / "products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_name", "category", "subcategory", "unit_cost", "msrp", "quality_rating", "updated_at"])
        writer.writerows(products_b2)

    orders_b2 = []
    order_items_b2 = []
    returns_b2 = []

    for i in range(501, 650):
        oid = f"ORD-{i:05d}"
        cid = f"CUST-{random.randint(1, 220):04d}"
        sid = f"STR-{random.randint(1, 10):03d}"
        ots = b2_time + timedelta(days=random.randint(1, 10))
        status = random.choice(order_statuses)
        orders_b2.append([
            oid, cid, sid, status, random.choice(payment_methods),
            ots.strftime("%Y-%m-%d %H:%M:%S"), ots.strftime("%Y-%m-%d %H:%M:%S")
        ])

        num_items = random.randint(1, 3)
        for _ in range(num_items):
            itid = f"ITM-{item_id_counter:06d}"
            item_id_counter += 1
            prod = random.choice(products_b1)
            prod_id = prod[0]
            unit_price = prod[5]
            qty = random.randint(1, 4)
            discount = round(unit_price * qty * 0.1, 2)
            tax = round((unit_price * qty - discount) * 0.08, 2)
            order_items_b2.append([
                itid, oid, prod_id, qty, unit_price, discount, tax,
                ots.strftime("%Y-%m-%d %H:%M:%S")
            ])

    with open(batch2_erp / "orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "customer_id", "store_id", "order_status", "payment_method", "order_timestamp", "updated_at"])
        writer.writerows(orders_b2)

    with open(batch2_erp / "order_items.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount", "tax_amount", "updated_at"])
        writer.writerows(order_items_b2)

    with open(batch2_erp / "product_returns.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["return_id", "order_id", "item_id", "product_id", "customer_id", "return_reason", "refund_amount", "return_timestamp"])
        writer.writerows(returns_b2)

if __name__ == "__main__":
    generate_datasets()
