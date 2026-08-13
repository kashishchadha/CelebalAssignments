import os
import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from utils.spark_session import get_spark_session
from config.settings import BRONZE_DIR, SILVER_DIR, GOLD_DIR, QUARANTINE_DIR, HWM_TABLE_NAME

def validate():
    spark = get_spark_session("RetailPipelineValidation")

    hwm_path = os.path.join(str(BRONZE_DIR), HWM_TABLE_NAME)
    hwm_df = spark.read.format("delta").load(hwm_path)
    print("=== HIGH-WATER MARK WATERMARKS ===")
    hwm_df.show(truncate=False)

    quarantine_cust = os.path.join(str(QUARANTINE_DIR), "customers", "batch_01")
    if os.path.exists(quarantine_cust):
        q_df = spark.read.parquet(quarantine_cust)
        print(f"=== QUARANTINED CUSTOMER RECORDS: {q_df.count()} ===")

    silver_cust_path = os.path.join(str(SILVER_DIR), "customers")
    silver_cust_df = spark.read.format("delta").load(silver_cust_path)
    total_cust = silver_cust_df.count()
    active_cust = silver_cust_df.filter("is_current = true").count()
    historical_cust = silver_cust_df.filter("is_current = false").count()
    print(f"=== SILVER CUSTOMERS (SCD TYPE 2) === Total: {total_cust} | Active: {active_cust} | Historical: {historical_cust}")

    fact_sales_path = os.path.join(str(GOLD_DIR), "fact_sales")
    fact_sales_df = spark.read.format("delta").load(fact_sales_path)
    print(f"=== GOLD FACT SALES RECORD COUNT: {fact_sales_df.count()} ===")
    fact_sales_df.select("order_id", "gross_sales_amount", "discount_amount", "net_sales_amount", "profit_amount", "profit_margin_pct").show(5)

    sales_mart_path = os.path.join(str(GOLD_DIR), "gold_sales_performance_mart")
    sales_mart_df = spark.read.format("delta").load(sales_mart_path)
    print("=== POWER BI SALES PERFORMANCE MART ===")
    sales_mart_df.show(5)

    churn_mart_path = os.path.join(str(GOLD_DIR), "gold_customer_churn_mart")
    churn_mart_df = spark.read.format("delta").load(churn_mart_path)
    print("=== POWER BI CUSTOMER CHURN MART ===")
    churn_mart_df.show(5)

    quality_mart_path = os.path.join(str(GOLD_DIR), "gold_product_quality_mart")
    quality_mart_df = spark.read.format("delta").load(quality_mart_path)
    print("=== POWER BI PRODUCT QUALITY MART ===")
    quality_mart_df.show(5)

    store_mart_path = os.path.join(str(GOLD_DIR), "gold_store_analytics_mart")
    store_mart_df = spark.read.format("delta").load(store_mart_path)
    print("=== POWER BI STORE ANALYTICS MART ===")
    store_mart_df.show(5)

    spark.stop()

if __name__ == "__main__":
    validate()
