import sys
import os
from pyspark.sql import SparkSession

def get_spark_session(app_name="RetailMedallionPipeline"):
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    builder = SparkSession.builder \
        .appName(app_name) \
        .config("spark.pyspark.python", sys.executable) \
        .config("spark.pyspark.driver.python", sys.executable) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.driver.memory", "4g") \
        .master("local[*]")
    
    try:
        # pyrefly: ignore [missing-import]
        import delta
        spark = delta.configure_spark_with_delta_pip(builder).getOrCreate()
    except Exception:
        spark = builder.getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")
    return spark
