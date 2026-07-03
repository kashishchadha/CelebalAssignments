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
