import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
from config.settings import RAW_DIR

class RawLayer:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def process_to_raw(self, inbound_files: dict) -> dict:
        raw_outputs = {}
        for entity, info in inbound_files.items():
            file_path = info["file_path"]
            source_system = info["source_system"]
            batch_id = info["batch_id"]

            df = self.spark.read.option("header", "true").option("inferSchema", "false").csv(file_path)

            df_with_meta = df \
                .withColumn("_ingest_timestamp", current_timestamp()) \
                .withColumn("_source_file", lit(os.path.basename(file_path))) \
                .withColumn("_source_system", lit(source_system)) \
                .withColumn("_batch_id", lit(batch_id))

            target_path = os.path.join(str(RAW_DIR), entity, batch_id)
            df_with_meta.write.mode("overwrite").option("header", "true").csv(target_path)
            raw_outputs[entity] = target_path

        return raw_outputs
