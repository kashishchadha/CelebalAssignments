"""Builds week 5's transactions dataset on top of the classic Superstore CSV.

Superstore already gives us real regions, cities, categories, sales and
quantities, but the assignment questions also mention columns it does not have
(age, subscription, status, email, username, store_id, raw_timestamp). This
script keeps every Superstore row, renames the columns to the names used in
the questions, derives the missing ones, and then injects the kind of mess the
cleaning steps are supposed to handle: duplicate rows, null prices and
statuses, blank usernames, missing emails and a few timestamps in the wrong
format.
"""

import csv
import random

random.seed(42)

STATUSES = ["Completed", "Pending", "Failed"]
SUBSCRIPTIONS = ["Free", "Basic", "Premium"]

with open("superstore.csv", newline="", encoding="cp1252") as f:
    src = list(csv.DictReader(f))

rows = []
for r in src:
    # Order Date comes as M/d/yyyy, normalise it once here
    month, day, year = r["Order Date"].split("/")
    txn_date = f"{year}-{int(month):02d}-{int(day):02d}"
    hour, minute, sec = random.randint(8, 21), random.randint(0, 59), random.randint(0, 59)
    raw_ts = f"{txn_date} {hour:02d}:{minute:02d}:{sec:02d}"
    # ~1% of timestamps arrive in a d/m/yyyy h.m format Spark's cast rejects
    if random.random() < 0.01:
        raw_ts = f"{int(day)}/{int(month)}/{year} {hour:02d}.{minute:02d}"

    price = round(float(r["Sales"]) / int(r["Quantity"]), 2)
    first = r["Customer Name"].split()[0].lower().strip("'.")
    last = r["Customer Name"].split()[-1].lower().strip("'.")
    email = f"{first}.{last}@example.com"
    username = f"{first}{random.randint(1, 99)}"
    # missing contact info: emails go fully missing, usernames tend to come in
    # as whitespace from the upstream form, which is nastier to catch
    if random.random() < 0.04:
        email = ""
    if random.random() < 0.03:
        username = " "

    rows.append({
        "transaction_id": f"T{int(r['Row ID']) + 10000}",
        "user_id": r["Customer ID"],
        "transaction_date": txn_date,
        "raw_timestamp": raw_ts,
        "region": r["Region"],
        "city": r["City"],
        "product_category": r["Category"],
        "price": price if random.random() > 0.05 else "",   # ~5% missing prices
        "quantity": r["Quantity"],
        "sale_amount": r["Sales"],
        "status": random.choice(STATUSES) if random.random() > 0.06 else "",
        "age": random.randint(18, 70),
        "subscription": random.choice(SUBSCRIPTIONS),
        "store_id": f"S{random.randint(1, 12):02d}",
        "email": email,
        "username": username,
    })

# ~3% exact duplicate rows (double submits)
rows += [dict(r) for r in random.sample(rows, 300)]

# same user + same date but a different transaction id (retried payments) --
# these are what Q3's dropDuplicates on (user_id, transaction_date) targets
for r in random.sample(rows, 200):
    clone = dict(r)
    clone["transaction_id"] = f"T{random.randint(30000, 39999)}"
    rows.append(clone)

random.shuffle(rows)

with open("transactions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"wrote {len(rows)} rows from {len(src)} superstore rows")
