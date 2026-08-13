from pyspark.sql import SparkSession

def setup_unity_catalog(spark: SparkSession):
    catalog_sqls = [
        "CREATE CATALOG IF NOT EXISTS retail_catalog",
        "USE CATALOG retail_catalog",
        "CREATE SCHEMA IF NOT EXISTS bronze",
        "CREATE SCHEMA IF NOT EXISTS silver",
        "CREATE SCHEMA IF NOT EXISTS gold"
    ]
    for sql_cmd in catalog_sqls:
        try:
            spark.sql(sql_cmd)
        except Exception:
            pass

if __name__ == "__main__":
    from utils.spark_session import get_spark_session
    spark = get_spark_session("SetupUnityCatalog")
    setup_unity_catalog(spark)
