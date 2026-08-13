import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max as spark_max
from delta.tables import DeltaTable

try:
    from config.settings import BRONZE_DIR
    from utils.hwm_manager import HWMManager
except ImportError:
    from Assignment8.config.settings import BRONZE_DIR
    from Assignment8.utils.hwm_manager import HWMManager

class BronzeLayer:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.hwm_manager = HWMManager(spark)

    def process_to_bronze(self, landing_paths: dict) -> dict:
        bronze_outputs = {}

        timestamp_cols = {
            "customers": "updated_at",
            "customer_interactions": "interaction_timestamp",
            "stores": "updated_at",
            "products": "updated_at",
            "orders": "updated_at",
            "order_items": "updated_at",
            "product_returns": "return_timestamp"
        }

        for entity, landing_path in landing_paths.items():
            landing_df = self.spark.read.parquet(landing_path)
            ts_col = timestamp_cols.get(entity, "updated_at")

            last_hwm = self.hwm_manager.get_watermark(entity)

            if ts_col in landing_df.columns:
                incremental_df = landing_df.filter(col(ts_col) > last_hwm)
            else:
                incremental_df = landing_df

            target_path = os.path.join(str(BRONZE_DIR), entity)

            if DeltaTable.isDeltaTable(self.spark, target_path):
                incremental_df.write.format("delta").mode("append").save(target_path)
            else:
                incremental_df.write.format("delta").mode("overwrite").save(target_path)

            bronze_outputs[entity] = target_path

            if ts_col in incremental_df.columns and incremental_df.count() > 0:
                max_ts_val = incremental_df.select(spark_max(col(ts_col))).collect()[0][0]
                if max_ts_val:
                    self.hwm_manager.update_watermark(entity, str(max_ts_val))

        return bronze_outputs
