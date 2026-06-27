# E-Commerce Sales Database Analysis
### Celebal Summer Internship 2026 — Week 2

**Intern:** Kashish
**Track:** Data Engineering
**Week:** 2 — SQL & Relational Databases
**Dataset:** Superstore Sales (9,994 rows) + ShopEase Sample Tables

---

## Overview

This project is a complete SQL-based analysis of an e-commerce sales database. The goal was to take raw transactional data, load it into a relational database, and extract meaningful business insights using SQL queries — covering everything from basic filtering to multi-table joins and full ACID-compliant transactions.

The analysis is built on two datasets:
- **ShopEase tables** — a custom 4-table relational schema designed for the assignment (customers, products, orders, order_items)
- **Superstore dataset** — a real-world e-commerce dataset with 9,994 rows used for extended analysis

---

## Project Structure

```
week2_assignment/
│
├── analysis.ipynb       — main notebook with all queries and outputs
├── schema.sql           — CREATE TABLE statements with constraints and indexes
├── data.sql             — INSERT statements for ShopEase sample data
├── superstore.csv       — Superstore dataset (9,994 rows)
├── SETUP.env            — step-by-step setup and run instructions
└── README.md            — this file
```

---

## Database Schema

Four tables with proper constraints, foreign keys, and indexes:

```
customers       products
    │               │
    │               │
    ▼               ▼
  orders ──────▶ order_items
```

| Table | Rows | Description |
|---|---|---|
| customers | 8 | Customer profiles — city, state, premium status |
| products | 8 | Product catalog — category, brand, price, stock |
| orders | 10 | Order headers — status, date, total amount |
| order_items | 15 | Line items linking orders to products with discount |

---

## What I Did

### Section A — SQL Basics
- Retrieved all records and specific columns from tables
- Listed distinct product categories
- Identified primary keys across all tables and explained uniqueness and NOT NULL requirements
- Demonstrated UNIQUE constraint on email — attempted duplicate insert and captured the error
- Demonstrated CHECK constraint on unit_price — attempted negative price insert and captured the error

### Section B — Filtering & Optimization
- Filtered orders by status, category, price, state, and date ranges
- Used `BETWEEN` and `<>` operators for inclusive/exclusive filtering
- Explained how `idx_orders_date` improves date-range query performance using B-Tree indexing
- Rewrote a non-SARGable query (`YEAR(join_date) = 2024`) into an index-friendly range comparison

### Section C — Aggregation
- Counted total orders and computed total delivered revenue
- Calculated average unit price per product category
- Grouped orders by status and sorted by total revenue descending
- Found most expensive and cheapest products per category using MAX and MIN
- Used HAVING to filter categories where average price exceeds ₹2000

### Section D — Joins
- INNER JOIN across orders and customers to show order details with customer names
- LEFT JOIN to list all customers including those with no orders
- 3-table JOIN across orders → order_items → products to show full line-item details with computed totals
- Explained LEFT vs RIGHT vs FULL OUTER JOIN with examples from the schema
- Verified all foreign key relationships and demonstrated FK constraint violation

### Section E — Advanced Concepts
- Used CASE WHEN to classify products into Budget, Mid-Range, and Premium tiers
- Used CASE inside an aggregate to count Delivered vs Not Delivered orders in a single row
- Explained all four ACID properties with real-world examples
- Wrote a complete transaction — new order insert, two order items, stock deduction — with BEGIN, COMMIT, and ROLLBACK handling

### Extended Analysis — Superstore Dataset
- Sales and profit breakdown by region with a dual-axis chart
- Category-level revenue and profit margin analysis
- Monthly revenue trend from 2014 to 2017
- Top 10 customers by total spend
- Top 10 products by total sales
- Duplicate detection at order + product level
- Full data quality report — null checks, negative values, invalid quantities

---

## Key Findings

- **60% delivery rate** — 6 out of 10 ShopEase orders were Delivered
- **Shipped orders have the highest average value** — ₹6,798 vs ₹2,865 for Delivered
- **Electronics and Clothing** both exceed the ₹2,000 average price threshold
- **3 products are Budget** (under ₹1,000), 3 Mid-Range, 2 Premium
- **Superstore — West region** leads in total sales across all four years
- **Technology category** has the highest profit margin despite fewer transactions
- **No duplicate records** found in the Superstore dataset at order + product level

---

## Tools & Technologies

| Tool | Purpose |
|---|---|
| Python 3 | Scripting and notebook execution |
| SQLite | Local relational database engine |
| Pandas | Data loading, SQL query results as DataFrames |
| Matplotlib | Charts and visualizations |
| Jupyter / VS Code | Development environment |

---

## How to Run

**1. Install dependencies**
```bash
pip install pandas matplotlib jupyter ipykernel
```

**2. Open in VS Code**
```
File → Open Folder → select this folder
```

**3. Open `analysis.ipynb`**

**4. Select kernel** — top right corner → Python 3.x

**5. Run All** — click ▶▶ at the top of the notebook

All outputs, tables, and charts will appear inline. The database is created automatically on first run.

> Full step-by-step instructions with error fixes are in `SETUP.env`

---

## SQL Concepts Covered

`SELECT` `WHERE` `DISTINCT` `BETWEEN` `GROUP BY` `HAVING` `ORDER BY` `LIMIT`
`COUNT` `SUM` `AVG` `MIN` `MAX` `CASE WHEN` `INNER JOIN` `LEFT JOIN`
`PRIMARY KEY` `FOREIGN KEY` `CHECK` `UNIQUE` `NOT NULL` `INDEX`
`BEGIN` `COMMIT` `ROLLBACK` `ACID`