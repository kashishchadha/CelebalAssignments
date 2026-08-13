import os
from pyspark.sql import SparkSession
from config.settings import SILVER_DIR, SCD_TYPE1_ENTITIES, SCD_TYPE2_ENTITIES
from utils.scd_handler import SCDHandler

class SilverLayer:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.scd_handler = SCDHandler(spark)

    def process_to_silver(self, silver_staging_paths: dict) -> dict:
        silver_outputs = {}

        pk_map = {
            "customers": "customer_id",
            "customer_interactions": "interaction_id",
            "stores": "store_id",
            "products": "product_id",
            "orders": "order_id",
            "order_items": "item_id",
            "product_returns": "return_id"
        }

        for entity, staging_path in silver_staging_paths.items():
            staging_df = self.spark.read.format("delta").load(staging_path)
            target_path = os.path.join(str(SILVER_DIR), entity)
            pk = pk_map.get(entity)

            if entity in SCD_TYPE2_ENTITIES:
                tracked_cols = ["first_name", "last_name", "email", "phone", "city", "state", "country", "segment", "churn_risk_score"]
                self.scd_handler.execute_scd_type_2(
                    target_path=target_path,
                    source_df=staging_df,
                    primary_key=pk,
                    tracked_cols=tracked_cols,
                    timestamp_col="updated_at"
                )
            else:
                self.scd_handler.execute_scd_type_1(
                    target_path=target_path,
                    source_df=staging_df,
                    primary_key=pk
                )

            silver_outputs[entity] = target_path

        return silver_outputs
