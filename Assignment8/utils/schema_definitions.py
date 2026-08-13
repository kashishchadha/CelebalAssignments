from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, DateType
)

CUSTOMERS_SCHEMA = StructType([
    StructField("customer_id", StringType(), True),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("country", StringType(), True),
    StructField("segment", StringType(), True),
    StructField("churn_risk_score", DoubleType(), True),
    StructField("created_at", StringType(), True),
    StructField("updated_at", StringType(), True)
])

CUSTOMER_INTERACTIONS_SCHEMA = StructType([
    StructField("interaction_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("channel", StringType(), True),
    StructField("sentiment", StringType(), True),
    StructField("support_tickets_count", IntegerType(), True),
    StructField("interaction_timestamp", StringType(), True)
])

STORES_SCHEMA = StructType([
    StructField("store_id", StringType(), True),
    StructField("store_name", StringType(), True),
    StructField("store_type", StringType(), True),
    StructField("city", StringType(), True),
    StructField("region", StringType(), True),
    StructField("sqft_area", IntegerType(), True),
    StructField("manager_name", StringType(), True),
    StructField("opened_date", StringType(), True),
    StructField("updated_at", StringType(), True)
])

PRODUCTS_SCHEMA = StructType([
    StructField("product_id", StringType(), True),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("subcategory", StringType(), True),
    StructField("unit_cost", DoubleType(), True),
    StructField("msrp", DoubleType(), True),
    StructField("quality_rating", DoubleType(), True),
    StructField("updated_at", StringType(), True)
])

ORDERS_SCHEMA = StructType([
    StructField("order_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("store_id", StringType(), True),
    StructField("order_status", StringType(), True),
    StructField("payment_method", StringType(), True),
    StructField("order_timestamp", StringType(), True),
    StructField("updated_at", StringType(), True)
])

ORDER_ITEMS_SCHEMA = StructType([
    StructField("item_id", StringType(), True),
    StructField("order_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DoubleType(), True),
    StructField("discount_amount", DoubleType(), True),
    StructField("tax_amount", DoubleType(), True),
    StructField("updated_at", StringType(), True)
])

PRODUCT_RETURNS_SCHEMA = StructType([
    StructField("return_id", StringType(), True),
    StructField("order_id", StringType(), True),
    StructField("item_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("return_reason", StringType(), True),
    StructField("refund_amount", DoubleType(), True),
    StructField("return_timestamp", StringType(), True)
])

SCHEMAS = {
    "customers": CUSTOMERS_SCHEMA,
    "customer_interactions": CUSTOMER_INTERACTIONS_SCHEMA,
    "stores": STORES_SCHEMA,
    "products": PRODUCTS_SCHEMA,
    "orders": ORDERS_SCHEMA,
    "order_items": ORDER_ITEMS_SCHEMA,
    "product_returns": PRODUCT_RETURNS_SCHEMA
}
