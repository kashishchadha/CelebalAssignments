import os
import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from data_generator.generate_source_data import generate_datasets
from utils.spark_session import get_spark_session
from layers.layer_01_inbound import InboundLayer
from layers.layer_02_raw import RawLayer
from layers.layer_03_landing import LandingLayer
from layers.layer_04_bronze import BronzeLayer
from layers.layer_05_silver_staging import SilverStagingLayer
from layers.layer_06_silver import SilverLayer
from layers.layer_07_gold import GoldLayer

def run_batch(spark, batch_id: str):
    inbound = InboundLayer(batch_name=batch_id)
    inbound_files = inbound.get_inbound_files()
    
    raw = RawLayer(spark)
    raw_outputs = raw.process_to_raw(inbound_files)
    
    landing = LandingLayer(spark)
    landing_outputs = landing.process_to_landing(raw_outputs, batch_id)
    
    bronze = BronzeLayer(spark)
    bronze_outputs = bronze.process_to_bronze(landing_outputs)
    
    silver_staging = SilverStagingLayer(spark)
    silver_staging_outputs = silver_staging.process_to_silver_staging(landing_outputs, batch_id)
    
    silver = SilverLayer(spark)
    silver_outputs = silver.process_to_silver(silver_staging_outputs)
    
    gold = GoldLayer(spark)
    gold_outputs = gold.process_to_gold(silver_outputs)
    
    return gold_outputs

def main():
    generate_datasets()
    spark = get_spark_session("RetailPipelineMasterRunner")
    
    run_batch(spark, "batch_01")
    run_batch(spark, "batch_02")
    
    print("PIPELINE_EXECUTION_SUCCESSFUL")
    spark.stop()

if __name__ == "__main__":
    main()
