import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, lower, coalesce, lit, row_number
from pyspark.sql.window import Window
from config.settings import SILVER_STAGING_DIR

class SilverStagingLayer:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def process_to_silver_staging(self, landing_paths: dict, batch_id: str = "batch_01") -> dict:
        silver_staging_outputs = {}

        pk_map = {
            "customers": "customer_id",
            "customer_interactions": "interaction_id",
            "stores": "store_id",
            "products": "product_id",
            "orders": "order_id",
            "order_items": "item_id",
            "product_returns": "return_id"
        }

        ts_map = {
            "customers": "updated_at",
            "customer_interactions": "interaction_timestamp",
            "stores": "updated_at",
            "products": "updated_at",
            "orders": "updated_at",
            "order_items": "updated_at",
            "product_returns": "return_timestamp"
        }

        for entity, landing_path in landing_paths.items():
            df = self.spark.read.parquet(landing_path)

            string_cols = [f.name for f in df.schema.fields if f.dataType.typeName() == "string"]
            for c in string_cols:
                if c not in ["_source_file", "_source_system", "_batch_id"]:
                    df = df.withColumn(c, trim(col(c)))

            if "email" in df.columns:
                df = df.withColumn("email", lower(col("email")))

            if "churn_risk_score" in df.columns:
                df = df.withColumn("churn_risk_score", coalesce(col("churn_risk_score"), lit(0.0)))

            pk = pk_map.get(entity)
            ts = ts_map.get(entity, "_ingest_timestamp")

            if pk in df.columns and ts in df.columns:
                window_spec = Window.partitionBy(pk).orderBy(col(ts).desc(), col("_ingest_timestamp").desc())
                dedup_df = df.withColumn("rn", row_number().over(window_spec)).filter(col("rn") == 1).drop("rn")
            else:
                dedup_df = df

            target_path = os.path.join(str(SILVER_STAGING_DIR), entity, batch_id)
            dedup_df.write.format("delta").mode("overwrite").save(target_path)
            silver_staging_outputs[entity] = target_path

        return silver_staging_outputs
