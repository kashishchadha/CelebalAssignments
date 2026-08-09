-- Basic queries.
-- Revenue always excludes CANCELLED orders and counts return lines as negative,
-- which is why the item_revenue view keeps the sign of quantity.

-- QUERY: q01_revenue_per_category
SELECT
    category,
    COUNT(DISTINCT order_id)    AS orders,
    SUM(quantity)               AS units,
    ROUND(SUM(revenue), 2)      AS total_revenue
FROM item_revenue
WHERE status <> 'CANCELLED'
GROUP BY category
ORDER BY total_revenue DESC;


-- QUERY: q02_top_10_customers
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    COUNT(DISTINCT ir.order_id) AS total_orders,
    ROUND(SUM(ir.revenue), 2)   AS total_order_value
FROM item_revenue ir
JOIN customers c ON c.customer_id = ir.customer_id
WHERE ir.status <> 'CANCELLED'
GROUP BY c.customer_id, c.customer_name, c.customer_type
ORDER BY total_order_value DESC
LIMIT 10;


-- QUERY: q03_monthly_order_count_last_12_months
-- "Last 12 months" is measured from the latest order that has actually
-- happened. Future dated pre-orders exist in the data and would otherwise drag
-- the window forward and leave most months empty.
WITH bounds AS (
    SELECT DATE(MAX(order_date), 'start of month', '-11 months') AS window_start
    FROM orders
    WHERE DATE(order_date) <= DATE('now')
)
SELECT
    STRFTIME('%Y-%m', o.order_date) AS order_month,
    COUNT(*)                        AS order_count,
    COUNT(DISTINCT o.customer_id)   AS unique_customers
FROM orders o, bounds b
WHERE DATE(o.order_date) >= b.window_start
  AND DATE(o.order_date) <= DATE('now')
GROUP BY order_month
ORDER BY order_month;
