import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from config.settings import LANDING_DIR, QUARANTINE_DIR
from utils.schema_definitions import SCHEMAS

class LandingLayer:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def process_to_landing(self, raw_paths: dict, batch_id: str) -> dict:
        landing_outputs = {}

        for entity, raw_path in raw_paths.items():
            schema = SCHEMAS.get(entity)
            df = self.spark.read.option("header", "true").csv(raw_path)

            meta_cols = ["_ingest_timestamp", "_source_file", "_source_system", "_batch_id"]
            business_cols = [c for c in df.columns if c not in meta_cols]

            casted_df = df
            for field in schema.fields:
                if field.name in business_cols:
                    casted_df = casted_df.withColumn(field.name, col(field.name).cast(field.dataType))

            pk_col = f"{entity[:-1] if entity.endswith('s') else entity}_id"
            if entity == "customer_interactions":
                pk_col = "interaction_id"
            elif entity == "order_items":
                pk_col = "item_id"
            elif entity == "product_returns":
                pk_col = "return_id"

            if pk_col in casted_df.columns:
                valid_df = casted_df.filter(col(pk_col).isNotNull() & (col(pk_col) != "") & (~col(pk_col).startswith("CORRUPT")))
                corrupt_df = casted_df.filter(col(pk_col).isNull() | (col(pk_col) == "") | col(pk_col).startswith("CORRUPT"))
            else:
                valid_df = casted_df
                corrupt_df = self.spark.createDataFrame([], casted_df.schema)

            landing_path = os.path.join(str(LANDING_DIR), entity, batch_id)
            valid_df.write.mode("overwrite").parquet(landing_path)
            landing_outputs[entity] = landing_path

            if corrupt_df.count() > 0:
                quarantine_path = os.path.join(str(QUARANTINE_DIR), entity, batch_id)
                corrupt_df.write.mode("overwrite").parquet(quarantine_path)

        return landing_outputs
