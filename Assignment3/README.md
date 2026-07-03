# Week 3 - Superstore Sales Analysis

SQL analysis of the Sample Superstore dataset using subqueries, CTEs and window
functions. The dataset is loaded into a SQLite database, split into three tables
(`customers`, `products`, `orders`), and then queried to answer a set of business
questions about customer sales.

## Folder structure

```
superstore-sql-analysis/
├── data/
│   └── Sample - Superstore.csv     raw dataset
├── notebook/
│   └── analysis.ipynb              main notebook (setup + all queries + results)
├── sql/
│   ├── schema.sql                  creates customers, products, orders
│   └── queries.sql                 all required queries as a plain SQL script
├── output/                         SQLite database is created here when you run
├── requirements.txt
└── README.md
```

## What it does

- Loads `Sample - Superstore.csv` into a table called `superstore_raw`.
- Builds three tables from it with `SELECT DISTINCT`:
  - `customers` (customer_id, customer_name, segment)
  - `products` (product_id, category, sub_category, product_name)
  - `orders` (order and line-item level fields, including sales)
- Runs the Step 2 queries, the final combined query, and the mini-project questions.

## Setup

You need Python 3.9 or newer. SQLite comes with Python, so there is nothing extra to
install for the database itself.

1. Open the project folder in VS Code.
2. Open a terminal (`Terminal > New Terminal`) and create a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Activate it:

   - Windows: `.venv\Scripts\activate`
   - macOS / Linux: `source .venv/bin/activate`

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## How to run

1. Open `notebook/analysis.ipynb` in VS Code.
2. When prompted, select the `.venv` you just created as the kernel.
3. Run all cells from top to bottom (`Run All`).

The first cells load the CSV and build the tables. Running the notebook creates
`output/superstore.db`, so make sure the `output/` folder exists (it is already in the
project). Each query cell prints its result as a table right below it.

If you only want the raw SQL, `sql/schema.sql` and `sql/queries.sql` can be run against
any SQLite database (for example with the SQLite extension in VS Code, or the
`sqlite3` command line).

## Queries covered

Step 2:

1. Orders with sales above the overall average (subquery)
2. Highest sales order per customer (subquery)
3. Total sales per customer (CTE)
4. Customers with above-average total sales (CTE + subquery)
5. Customer ranking by total sales (window function)
6. Row number per order within each customer (window function + PARTITION BY)
7. Top 3 customers by total sales (window function)

Final combined query: customer name, total sales and rank in one result using a JOIN,
a CTE and a window function together.

Mini project:

1. Top 5 customers
2. Bottom 5 customers
3. Customers with only one order
4. Customers with above-average sales
5. Highest order value per customer

## Notes

- The CSV stores dates as `MM/DD/YYYY` strings. They are converted to `YYYY-MM-DD`
  before loading so that ordering by date in the window function stays chronological.
- The `orders` table is at line-item level (one row per product on an order), which is
  how the original dataset is laid out. Order-level totals are computed in the queries
  where they are needed.
