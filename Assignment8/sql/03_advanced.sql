-- Advanced queries: window functions, CTEs and subqueries.

-- QUERY: q07_running_total_per_region
WITH daily AS (
    SELECT
        region_code,
        DATE(order_date)       AS order_date,
        ROUND(SUM(revenue), 2) AS daily_revenue
    FROM item_revenue
    WHERE status <> 'CANCELLED'
    GROUP BY region_code, DATE(order_date)
)
SELECT
    region_code,
    order_date,
    daily_revenue,
    ROUND(SUM(daily_revenue) OVER (
        PARTITION BY region_code
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_total
FROM daily
ORDER BY region_code, order_date;


-- QUERY: q08_product_rank_within_category
-- DENSE_RANK so two products on identical revenue share a rank and the next
-- product is not pushed down a place.
WITH product_revenue AS (
    SELECT
        category,
        product_name,
        ROUND(SUM(revenue), 2) AS total_revenue
    FROM item_revenue
    WHERE status <> 'CANCELLED'
    GROUP BY category, product_name
)
SELECT
    category,
    product_name,
    total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;


-- QUERY: q09_customer_order_gaps
-- LAG gives the previous order date per customer; the average gap decides
-- whether the customer is drifting away.
WITH customer_orders AS (
    SELECT DISTINCT customer_id, DATE(order_date) AS order_date
    FROM orders
    WHERE customer_id IS NOT NULL
      AND status <> 'CANCELLED'
),
gaps AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM customer_orders
)
SELECT
    customer_id,
    order_date,
    previous_order_date,
    CAST(JULIANDAY(order_date) - JULIANDAY(previous_order_date) AS INTEGER) AS days_gap,
    CASE
        WHEN AVG(JULIANDAY(order_date) - JULIANDAY(previous_order_date))
             OVER (PARTITION BY customer_id) > 30 THEN 'At Risk'
        ELSE 'Active'
    END AS risk_flag
FROM gaps
ORDER BY customer_id, order_date;


-- QUERY: q10_monthly_customer_value_bands
-- Level 1: revenue per customer per month.
-- Level 2: put each customer-month into a band.
-- Level 3: how many customers sit in each band, month by month.
WITH monthly_customer_revenue AS (
    SELECT
        STRFTIME('%Y-%m', order_date) AS order_month,
        customer_id,
        SUM(revenue)                  AS revenue
    FROM item_revenue
    WHERE customer_id IS NOT NULL
      AND status <> 'CANCELLED'
    GROUP BY order_month, customer_id
),
banded AS (
    SELECT
        order_month,
        customer_id,
        revenue,
        CASE
            WHEN revenue > 10000 THEN 'High'
            WHEN revenue >= 5000 THEN 'Medium'
            ELSE 'Low'
        END AS value_band
    FROM monthly_customer_revenue
)
SELECT
    order_month,
    value_band,
    COUNT(*)                 AS customer_count,
    ROUND(SUM(revenue), 2)   AS band_revenue
FROM banded
GROUP BY order_month, value_band
ORDER BY order_month,
         CASE value_band WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;


-- QUERY: q11_customer_quartiles
WITH lifetime_value AS (
    SELECT
        customer_id,
        ROUND(SUM(revenue), 2) AS total_value
    FROM item_revenue
    WHERE customer_id IS NOT NULL
      AND status <> 'CANCELLED'
    GROUP BY customer_id
),
quartiles AS (
    SELECT
        customer_id,
        total_value,
        NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM lifetime_value
)
SELECT
    customer_id,
    total_value,
    quartile,
    CASE quartile
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS quartile_label
FROM quartiles
ORDER BY total_value DESC;


-- QUERY: q12_year_over_year_revenue
-- LEFT JOIN back onto the same CTE so months without a prior year still appear,
-- with NULL growth instead of a divide-by-zero.
WITH monthly_revenue AS (
    SELECT
        CAST(STRFTIME('%Y', order_date) AS INTEGER) AS year,
        CAST(STRFTIME('%m', order_date) AS INTEGER) AS month,
        ROUND(SUM(revenue), 2)                      AS revenue
    FROM item_revenue
    WHERE status <> 'CANCELLED'
    GROUP BY year, month
)
SELECT
    cur.year,
    cur.month,
    cur.revenue,
    prev.revenue AS prev_year_revenue,
    CASE
        WHEN prev.revenue IS NULL OR prev.revenue = 0 THEN NULL
        ELSE ROUND(100.0 * (cur.revenue - prev.revenue) / prev.revenue, 2)
    END AS yoy_growth_percent
FROM monthly_revenue cur
LEFT JOIN monthly_revenue prev
       ON prev.year  = cur.year - 1
      AND prev.month = cur.month
ORDER BY cur.year, cur.month;


-- QUERY: q13_first_and_last_category
-- LAST_VALUE needs an explicit frame, otherwise the default frame stops at the
-- current row and returns the same value as the current row.
WITH customer_items AS (
    SELECT customer_id, order_date, category
    FROM item_revenue
    WHERE customer_id IS NOT NULL
      AND status <> 'CANCELLED'
),
edges AS (
    SELECT DISTINCT
        customer_id,
        FIRST_VALUE(category) OVER (
            PARTITION BY customer_id ORDER BY order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS first_category,
        LAST_VALUE(category) OVER (
            PARTITION BY customer_id ORDER BY order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS latest_category
    FROM customer_items
)
SELECT
    customer_id,
    first_category,
    latest_category,
    CASE WHEN first_category <> latest_category THEN 'Yes' ELSE 'No' END AS category_shift
FROM edges
ORDER BY customer_id;


-- QUERY: q14_revenue_concentration
-- Answers "what share of revenue comes from the top N% of customers".
WITH customer_revenue AS (
    SELECT
        customer_id,
        ROUND(SUM(revenue), 2) AS revenue
    FROM item_revenue
    WHERE customer_id IS NOT NULL
      AND status <> 'CANCELLED'
    GROUP BY customer_id
)
SELECT
    customer_id,
    revenue,
    ROUND(SUM(revenue) OVER (ORDER BY revenue DESC
                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2)
        AS cumulative_revenue,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC
                                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          / SUM(revenue) OVER (), 2) AS cumulative_percent,
    ROUND(100.0 * CUME_DIST() OVER (ORDER BY revenue DESC), 2) AS customer_percentile
FROM customer_revenue
ORDER BY revenue DESC;


-- QUERY: q15_cohort_retention
-- Cohort = registration month. month_offset counts calendar months between
-- registration and the order, so month 0 is the registration month itself.
WITH cohort AS (
    SELECT
        customer_id,
        STRFTIME('%Y-%m', registration_date) AS cohort_month,
        CAST(STRFTIME('%Y', registration_date) AS INTEGER) * 12
            + CAST(STRFTIME('%m', registration_date) AS INTEGER) AS reg_index
    FROM customers
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS customers_in_cohort
    FROM cohort
    GROUP BY cohort_month
),
activity AS (
    SELECT DISTINCT
        c.cohort_month,
        o.customer_id,
        CAST(STRFTIME('%Y', o.order_date) AS INTEGER) * 12
            + CAST(STRFTIME('%m', o.order_date) AS INTEGER) - c.reg_index AS month_offset
    FROM orders o
    JOIN cohort c ON c.customer_id = o.customer_id
    WHERE o.status <> 'CANCELLED'
)
SELECT
    cs.cohort_month,
    cs.customers_in_cohort,
    a.month_offset,
    COUNT(DISTINCT a.customer_id) AS active_customers,
    ROUND(100.0 * COUNT(DISTINCT a.customer_id) / cs.customers_in_cohort, 2) AS retention_percent
FROM cohort_size cs
JOIN activity a ON a.cohort_month = cs.cohort_month
WHERE a.month_offset BETWEEN 0 AND 3
GROUP BY cs.cohort_month, cs.customers_in_cohort, a.month_offset
ORDER BY cs.cohort_month, a.month_offset;


-- QUERY: q16_order_over_order_change
-- Self-join on the same customer, then a window function picks out the single
-- most recent earlier order rather than every earlier order.
WITH order_totals AS (
    SELECT
        order_id,
        customer_id,
        DATE(order_date)       AS order_date,
        ROUND(SUM(revenue), 2) AS order_value
    FROM item_revenue
    WHERE customer_id IS NOT NULL
      AND status <> 'CANCELLED'
    GROUP BY order_id, customer_id, DATE(order_date)
),
paired AS (
    SELECT
        cur.customer_id,
        cur.order_id,
        cur.order_date,
        cur.order_value,
        prev.order_id    AS previous_order_id,
        prev.order_value AS previous_order_value,
        ROW_NUMBER() OVER (
            PARTITION BY cur.order_id
            ORDER BY prev.order_date DESC
        ) AS recency
    FROM order_totals cur
    JOIN order_totals prev
      ON prev.customer_id = cur.customer_id
     AND prev.order_date  < cur.order_date
)
SELECT
    customer_id,
    order_id,
    order_date,
    order_value,
    previous_order_id,
    previous_order_value,
    ROUND(order_value - previous_order_value, 2) AS change_in_value,
    CASE
        WHEN order_value > previous_order_value THEN 'Up'
        WHEN order_value < previous_order_value THEN 'Down'
        ELSE 'Flat'
    END AS trend
FROM paired
WHERE recency = 1
ORDER BY customer_id, order_date;
