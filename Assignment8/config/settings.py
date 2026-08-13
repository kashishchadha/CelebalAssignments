import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "storage"
INBOUND_DIR = DATA_DIR / "01_inbound"
RAW_DIR = DATA_DIR / "02_raw"
LANDING_DIR = DATA_DIR / "03_landing"
BRONZE_DIR = DATA_DIR / "04_bronze"
SILVER_STAGING_DIR = DATA_DIR / "05_silver_staging"
SILVER_DIR = DATA_DIR / "06_silver"
GOLD_DIR = DATA_DIR / "07_gold"
QUARANTINE_DIR = DATA_DIR / "quarantine"

CRM_INBOUND_DIR = INBOUND_DIR / "crm"
ERP_INBOUND_DIR = INBOUND_DIR / "erp"

CATALOG_NAME = "retail_catalog"
SCHEMA_BRONZE = "bronze"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"

HWM_TABLE_NAME = "hwm_watermarks"

TABLES_CRM = ["customers", "customer_interactions"]
TABLES_ERP = ["stores", "products", "orders", "order_items", "product_returns"]

ALL_ENTITIES = TABLES_CRM + TABLES_ERP

SCD_TYPE2_ENTITIES = ["customers"]
SCD_TYPE1_ENTITIES = ["stores", "products"]

def init_directories():
    directories = [
        INBOUND_DIR, RAW_DIR, LANDING_DIR, BRONZE_DIR,
        SILVER_STAGING_DIR, SILVER_DIR, GOLD_DIR, QUARANTINE_DIR,
        CRM_INBOUND_DIR, ERP_INBOUND_DIR
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
