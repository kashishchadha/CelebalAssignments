import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from delta.tables import DeltaTable

try:
    from config.settings import BRONZE_DIR, HWM_TABLE_NAME
except ImportError:
    from Assignment8.config.settings import BRONZE_DIR, HWM_TABLE_NAME

class HWMManager:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.hwm_path = os.path.join(str(BRONZE_DIR), HWM_TABLE_NAME)
        self._ensure_hwm_table()

    def _ensure_hwm_table(self):
        if not DeltaTable.isDeltaTable(self.spark, self.hwm_path):
            empty_df = self.spark.sql("SELECT CAST(NULL as STRING) as entity_name, CAST(NULL as STRING) as last_watermark, CAST(NULL as TIMESTAMP) as updated_at WHERE 1=0")
            empty_df.write.format("delta").mode("overwrite").save(self.hwm_path)

    def get_watermark(self, entity_name: str) -> str:
        try:
            if DeltaTable.isDeltaTable(self.spark, self.hwm_path):
                df = self.spark.read.format("delta").load(self.hwm_path)
                res = df.filter(col("entity_name") == entity_name).select("last_watermark").collect()
                if res:
                    return res[0]["last_watermark"]
        except Exception:
            pass
        return "1970-01-01 00:00:00"

    def update_watermark(self, entity_name: str, watermark: str):
        updates_df = self.spark.sql(f"SELECT '{entity_name}' as entity_name, '{watermark}' as last_watermark, current_timestamp() as updated_at")
        
        if DeltaTable.isDeltaTable(self.spark, self.hwm_path):
            delta_table = DeltaTable.forPath(self.spark, self.hwm_path)
            delta_table.alias("target").merge(
                updates_df.alias("source"),
                "target.entity_name = source.entity_name"
            ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
        else:
            updates_df.write.format("delta").mode("overwrite").save(self.hwm_path)
