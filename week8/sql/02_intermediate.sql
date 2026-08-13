-- Intermediate queries.

-- QUERY: q04_customers_with_no_delivered_item
-- Customers who have ordered at least once but never reached DELIVERED.
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    COUNT(DISTINCT o.order_id) AS orders_placed,
    MAX(o.order_date)          AS last_order_date
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE NOT EXISTS (
        SELECT 1
        FROM orders d
        WHERE d.customer_id = c.customer_id
          AND d.status = 'DELIVERED'
      )
GROUP BY c.customer_id, c.customer_name, c.customer_type
ORDER BY orders_placed DESC, c.customer_id;


-- QUERY: q05_products_with_more_returns_than_purchases
-- Return units are stored as negative quantity, so ABS() puts both sides on the
-- same scale before comparing.
WITH product_flow AS (
    SELECT
        product_id,
        product_name,
        category,
        SUM(CASE WHEN quantity > 0 THEN quantity ELSE 0 END)      AS units_purchased,
        SUM(CASE WHEN quantity < 0 THEN ABS(quantity) ELSE 0 END) AS units_returned
    FROM item_revenue
    GROUP BY product_id, product_name, category
)
SELECT
    product_id,
    product_name,
    category,
    units_purchased,
    units_returned,
    units_returned - units_purchased AS net_loss_units
FROM product_flow
WHERE units_returned > units_purchased
ORDER BY net_loss_units DESC;


-- QUERY: q06_return_rate_per_category
SELECT
    category,
    SUM(CASE WHEN quantity > 0 THEN quantity ELSE 0 END)      AS units_purchased,
    SUM(CASE WHEN quantity < 0 THEN ABS(quantity) ELSE 0 END) AS units_returned,
    ROUND(
        100.0 * SUM(CASE WHEN quantity < 0 THEN ABS(quantity) ELSE 0 END)
        / NULLIF(SUM(ABS(quantity)), 0),
    2) AS return_rate_percent
FROM item_revenue
GROUP BY category
ORDER BY return_rate_percent DESC;
