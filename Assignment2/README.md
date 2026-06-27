# 📊 SQL Sales Data Analysis
### Celebal Technologies Summer Internship 2026 | Week 2 Assignment

> End-to-end SQL analysis of an E-Commerce Sales Database demonstrating data exploration, filtering, aggregation, joins, transactions, and business insights.

---

## 📌 Project Overview

This project was completed as part of the **Celebal Technologies Summer Internship 2026 (Week 2)**.

The objective was to analyze an **E-Commerce Sales Database** using SQL by applying real-world database concepts such as filtering, aggregation, joins, constraints, indexing, transactions, and business reporting.

The project also extends the assignment by performing additional sales analysis and visualizations using Python and SQL to derive actionable business insights.

---

## 🎯 Assignment Objectives

✔ Load the dataset into a SQL database

✔ Explore the database schema and sample data

✔ Filter records using SQL

✔ Perform aggregations using GROUP BY

✔ Rank and sort business metrics

✔ Solve business use cases

✔ Validate data quality

✔ Generate insights through SQL queries and visualizations

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| SQL (SQLite) | Database Queries |
| Python | Data Analysis |
| Pandas | Data Manipulation |
| SQLite3 | Database Connectivity |
| Matplotlib | Data Visualization |
| Jupyter Notebook | Implementation |

---

# 📂 Repository Structure

```
Assignment2
│
├── data/
│   ├── Superstore.csv
│   ├── schema.sql
│   ├── data.sql
│   └── shopease.db
│
├── notebook/
│   └── SQL_Assignment.ipynb
│
├── requirements.txt
│
└── README.md
```

---

# 🗂 Database Schema

The project is based on a relational database consisting of four interconnected tables.

| Table | Description |
|--------|-------------|
| Customers | Customer information |
| Products | Product catalog |
| Orders | Customer orders |
| Order Items | Product-level order details |

### Entity Relationship

```
Customers
     │
     │ 1 : N
     ▼
Orders
     │
     │ 1 : N
     ▼
Order_Items
     ▲
     │
Products
```

---

# 📚 SQL Concepts Covered

### ✅ Data Retrieval

- SELECT
- DISTINCT
- LIMIT

### ✅ Filtering

- WHERE
- BETWEEN
- LIKE
- IN
- AND / OR / NOT

### ✅ Aggregation

- COUNT()
- SUM()
- AVG()
- MIN()
- MAX()
- GROUP BY
- HAVING

### ✅ Sorting

- ORDER BY
- LIMIT

### ✅ Joins

- INNER JOIN
- LEFT JOIN

### ✅ Constraints

- Primary Key
- Foreign Key
- UNIQUE
- CHECK
- NOT NULL

### ✅ Advanced SQL

- CASE
- Transactions
- COMMIT
- ROLLBACK
- ACID Properties
- Indexes
- SARGable Queries

---

# 📈 Business Analysis Performed

The notebook includes SQL-based business analysis such as:

- 📍 Sales by Region
- 📦 Sales by Category
- 📅 Monthly Sales Trend
- 👤 Top Customers
- 🛒 Top Selling Products
- 💰 Revenue Analysis
- 🔍 Duplicate Detection
- ✔ Data Quality Validation

---

# 📊 Sample Insights

Some key insights obtained from the analysis:

- Regional sales performance varies significantly.
- Technology products generate the highest revenue.
- Monthly trends reveal seasonal demand patterns.
- A small percentage of customers contribute a major share of sales.
- No duplicate transactional records were found after validation.
- SQL aggregations provide quick business summaries for decision-making.

---

# ✔ Data Validation

The project includes validation checks to ensure data integrity.

- Total row counts
- Duplicate records
- Missing values
- Unique customers
- Unique orders
- Data consistency checks

---

# 🎓 Learning Outcomes

Through this assignment, I strengthened my understanding of:

- Relational Database Design
- SQL Query Writing
- Data Filtering
- Aggregation Techniques
- SQL Joins
- Transactions
- Constraints
- Index Optimization
- Business Analytics
- Data Validation

---

# ▶ How to Run

### Clone the Repository

```bash
git clone <repository-url>
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Launch Jupyter Notebook

```bash
jupyter notebook
```

Open **SQL_Assignment.ipynb** and run all cells.

---

# 📌 Assignment Information

**Organization:** Celebal Technologies

**Internship:** Summer Internship 2026

**Task:** Week 2 – E-Commerce Sales Database Analysis

---

# 👩‍💻 Author

### Kashish Chadha

**B.Tech Computer Science Engineering**

DIT University, Dehradun

Summer Intern @ Celebal Technologies

---

## ⭐ If you found this project useful, consider giving it a star!
