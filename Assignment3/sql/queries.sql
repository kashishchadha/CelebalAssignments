-- Q1. Orders where sales are greater than the average sales
SELECT order_id, customer_id, sales
FROM orders
WHERE sales > (SELECT AVG(sales) FROM orders)
ORDER BY sales DESC;


-- Q2. Highest sales order for each customer
SELECT o.customer_id, o.order_id, o.sales
FROM orders o
WHERE o.sales = (
    SELECT MAX(o2.sales)
    FROM orders o2
    WHERE o2.customer_id = o.customer_id
)
ORDER BY o.sales DESC;


-- Q3. Total sales for each customer
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
ORDER BY cs.total_sales DESC;


-- Q4. Customers whose total sales are above average
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
WHERE cs.total_sales > (SELECT AVG(total_sales) FROM customer_sales)
ORDER BY cs.total_sales DESC;


-- Q5. Rank all customers based on total sales
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name,
       ROUND(cs.total_sales, 2) AS total_sales,
       RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
ORDER BY sales_rank;


-- Q6. Row number for each order within a customer
SELECT customer_id,
       order_id,
       order_date,
       sales,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_seq
FROM orders
ORDER BY customer_id, order_seq;


-- Q7. Top 3 customers based on total sales
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
),
ranked AS (
    SELECT c.customer_name,
           cs.total_sales,
           RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
    FROM customer_sales cs
    JOIN customers c ON c.customer_id = cs.customer_id
)
SELECT customer_name, ROUND(total_sales, 2) AS total_sales, sales_rank
FROM ranked
WHERE sales_rank <= 3;


-- Final combined query: customer name, total sales, rank
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name,
       ROUND(cs.total_sales, 2) AS total_sales,
       RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
ORDER BY sales_rank;


-- Mini project 1. Top 5 customers
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
ORDER BY cs.total_sales DESC
LIMIT 5;


-- Mini project 2. Bottom 5 customers
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
ORDER BY cs.total_sales ASC
LIMIT 5;


-- Mini project 3. Customers who made only one order
SELECT c.customer_name, COUNT(DISTINCT o.order_id) AS order_count
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(DISTINCT o.order_id) = 1
ORDER BY c.customer_name;


-- Mini project 4. Customers with above-average sales
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, ROUND(cs.total_sales, 2) AS total_sales
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
WHERE cs.total_sales > (SELECT AVG(total_sales) FROM customer_sales)
ORDER BY cs.total_sales DESC;


-- Mini project 5. Highest order value per customer
WITH order_totals AS (
    SELECT customer_id, order_id, SUM(sales) AS order_value
    FROM orders
    GROUP BY customer_id, order_id
)
SELECT c.customer_name, ROUND(MAX(ot.order_value), 2) AS highest_order_value
FROM order_totals ot
JOIN customers c ON c.customer_id = ot.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY highest_order_value DESC;


-- Validation checks

-- V1. Row counts for core tables
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders;


-- V2. Null checks on key fields
SELECT 'customers.customer_id_nulls' AS check_name, COUNT(*) AS issue_count
FROM customers
WHERE customer_id IS NULL OR TRIM(customer_id) = ''
UNION ALL
SELECT 'products.product_id_nulls', COUNT(*)
FROM products
WHERE product_id IS NULL OR TRIM(product_id) = ''
UNION ALL
SELECT 'orders.order_id_nulls', COUNT(*)
FROM orders
WHERE order_id IS NULL OR TRIM(order_id) = ''
UNION ALL
SELECT 'orders.customer_id_nulls', COUNT(*)
FROM orders
WHERE customer_id IS NULL OR TRIM(customer_id) = ''
UNION ALL
SELECT 'orders.product_id_nulls', COUNT(*)
FROM orders
WHERE product_id IS NULL OR TRIM(product_id) = '';


-- V3. Duplicate IDs in dimension tables
SELECT 'duplicate_customer_ids' AS check_name, COUNT(*) AS issue_count
FROM (
    SELECT customer_id
    FROM customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'duplicate_product_ids', COUNT(*)
FROM (
    SELECT product_id
    FROM products
    GROUP BY product_id
    HAVING COUNT(*) > 1
);


-- V4. Foreign-key style orphan checks from orders to dimensions
SELECT 'orders_without_customer' AS check_name, COUNT(*) AS issue_count
FROM orders o
LEFT JOIN customers c ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL
UNION ALL
SELECT 'orders_without_product', COUNT(*)
FROM orders o
LEFT JOIN products p ON p.product_id = o.product_id
WHERE p.product_id IS NULL;


-- V5. Basic order_date format check (YYYY-MM-DD)
SELECT 'order_date_bad_format' AS check_name, COUNT(*) AS issue_count
FROM orders
WHERE order_date IS NULL
   OR order_date NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';
