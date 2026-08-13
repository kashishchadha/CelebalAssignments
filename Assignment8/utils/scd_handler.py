import os
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, sha2, concat_ws, lit, coalesce
from delta.tables import DeltaTable

class SCDHandler:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def execute_scd_type_1(self, target_path: str, source_df: DataFrame, primary_key: str):
        if not DeltaTable.isDeltaTable(self.spark, target_path):
            source_df.write.format("delta").mode("overwrite").save(target_path)
            return

        delta_table = DeltaTable.forPath(self.spark, target_path)
        merge_condition = f"target.{primary_key} = source.{primary_key}"

        delta_table.alias("target").merge(
            source_df.alias("source"),
            merge_condition
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

    def execute_scd_type_2(
        self,
        target_path: str,
        source_df: DataFrame,
        primary_key: str,
        tracked_cols: list,
        timestamp_col: str = "updated_at"
    ):
        source_with_hash = source_df.withColumn(
            "row_hash",
            sha2(concat_ws("||", *[coalesce(col(c).cast("string"), lit("")) for c in tracked_cols]), 256)
        ).withColumn(
            "surrogate_key",
            sha2(concat_ws("||", col(primary_key), col(timestamp_col)), 256)
        ).withColumn(
            "effective_start_date",
            col(timestamp_col)
        ).withColumn(
            "effective_end_date",
            lit("9999-12-31 23:59:59")
        ).withColumn(
            "is_current",
            lit(True)
        )

        if not DeltaTable.isDeltaTable(self.spark, target_path):
            source_with_hash.write.format("delta").mode("overwrite").save(target_path)
            return

        delta_table = DeltaTable.forPath(self.spark, target_path)
        target_df = delta_table.toDF()

        staged_updates = source_with_hash.alias("src").join(
            target_df.filter(col("is_current") == True).alias("tgt"),
            on=primary_key,
            how="inner"
        ).filter(
            col("src.row_hash") != col("tgt.row_hash")
        ).select(
            lit(None).cast("string").alias("merge_key"),
            col("src.*")
        )

        non_updated_records = source_with_hash.selectExpr(f"{primary_key} as merge_key", "*")
        union_source = non_updated_records.unionByName(staged_updates)

        merge_condition = f"target.{primary_key} = source.merge_key AND target.is_current = true"

        delta_table.alias("target").merge(
            union_source.alias("source"),
            merge_condition
        ).whenMatchedUpdate(
            condition="target.row_hash != source.row_hash",
            set={
                "is_current": "false",
                "effective_end_date": "source.effective_start_date"
            }
        ).whenNotMatchedInsert(
            values={
                "surrogate_key": "source.surrogate_key",
                primary_key: f"source.{primary_key}",
                **{c: f"source.{c}" for c in tracked_cols if c != primary_key},
                "row_hash": "source.row_hash",
                "effective_start_date": "source.effective_start_date",
                "effective_end_date": "source.effective_end_date",
                "is_current": "source.is_current"
            }
        ).execute()
