DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;

CREATE TABLE customers AS
SELECT DISTINCT
    customer_id,
    customer_name,
    segment
FROM superstore_raw;

CREATE TABLE products AS
SELECT DISTINCT
    product_id,
    category,
    sub_category,
    product_name
FROM superstore_raw;

CREATE TABLE orders AS
SELECT DISTINCT
    row_id,
    order_id,
    order_date,
    ship_date,
    ship_mode,
    customer_id,
    product_id,
    region,
    sales,
    quantity,
    discount,
    profit
FROM superstore_raw;
