# End-to-End Production Retail Data Engineering Pipeline
## Medallion Architecture on Databricks & Delta Lake

An enterprise-grade, 7-layer data engineering pipeline built using **PySpark**, **Delta Lake**, **Unity Catalog**, and **Parquet**. The system ingests raw transactional data from heterogeneous source systems (CRM & ERP) in CSV format, applies robust data quality quarantine controls, maintains incremental state via a **High-Water Mark (HWM)** engine, enforces **Slowly Changing Dimensions (SCD Type 1 & Type 2)**, and outputs an analytics-ready **Star Schema** with specialized **Power BI Data Marts**.

---

## 1. Pipeline Architecture Overview

```
===================================================================================================================================
                                              RETAIL MEDALLION 7-LAYER DATA ENGINE
===================================================================================================================================

 [CRM System]                [ERP System]
 (Customers, Interactions)    (Stores, Products, Orders, Order Items, Returns)
      |                            |
      +------------+---------------+
                   |
                   v
  +---------------------------------+
  | Layer 01: INBOUND               |  Raw external directory landing zone (CSV)
  +---------------------------------+
                   |
                   v
  +---------------------------------+
  | Layer 02: RAW                   |  Persistent archive + Metadata injection (_ingest_timestamp, _source_file, _batch_id)
  +---------------------------------+
                   |
                   v
  +---------------------------------+
  | Layer 03: LANDING               |  Format conversion to Parquet + StructType Schema Validation + Corrupt Record Quarantine
  +---------------------------------+
                   |
                   v
  +---------------------------------+
  | Layer 04: BRONZE                |  Delta Lake ingestion + High-Water Mark (HWM) incremental watermark tracking
  +---------------------------------+
                   |
                   v
  +---------------------------------+
  | Layer 05: SILVER STAGING        |  Data cleaning, null imputation, string trimming, windowed deduplication (row_number)
  +---------------------------------+
                   |
                   v
  +---------------------------------+
  | Layer 06: SILVER                |  Conformed business entities + Delta MERGE (SCD Type 1 & SCD Type 2 with Hash Surrogate Keys)
  +---------------------------------+
                   |
                   v
  +---------------------------------+
  | Layer 07: GOLD                  |  Dimensional Star Schema (FactSales, FactReturns, DimCustomer, DimProduct, DimStore, DimDate)
  |                                 |  + Power BI Business Data Marts (Sales, Churn, Quality, Store Analytics)
  +---------------------------------+
===================================================================================================================================
```

---

## 2. Detailed 7-Layer Pipeline Breakdown

### Layer 01: Inbound (`01_inbound`)
- **Purpose**: Acts as the external drop zone receiving CSV files from source systems.
- **Source Systems**:
  - **CRM**: `customers.csv`, `customer_interactions.csv`
  - **ERP**: `stores.csv`, `products.csv`, `orders.csv`, `order_items.csv`, `product_returns.csv`
- **Execution**: Micro-batches are received as `batch_01` (historical initial load) and `batch_02` (incremental delta load).

### Layer 02: Raw (`02_raw`)
- **Purpose**: Immutably preserves source data in raw directory storage while adding system audit metadata.
- **Audit Metadata Injected**:
  - `_ingest_timestamp`: System UTC timestamp when file was ingested.
  - `_source_file`: File basename.
  - `_source_system`: Source system tag (`CRM` or `ERP`).
  - `_batch_id`: Batch directory identifier (`batch_01`, `batch_02`).

### Layer 03: Landing (`03_landing`)
- **Purpose**: Converts CSV payloads into optimized columnar Parquet format, enforces strict schema types, and isolates bad records.
- **Schema Enforcement**: Evaluates incoming data against pre-compiled PySpark `StructType` schemas (`utils/schema_definitions.py`).
- **Quarantine Engine**: Records failing primary key integrity or exhibiting corrupt payloads (e.g. missing primary key, string flags) are filtered into `/quarantine/<entity>/<batch_id>`.

### Layer 04: Bronze (`04_bronze`)
- **Purpose**: Manages append-only ingestion into Delta Lake tables under `retail_catalog.bronze` with High-Water Mark (HWM) tracking.
- **High-Water Mark Mechanism**:
  - Queries `hwm_watermarks` metadata table to fetch `last_watermark` for the target entity.
  - Filters records where `updated_at > last_watermark`.
  - Appends new records into Bronze Delta tables.
  - Calculates `MAX(updated_at)` from processed batch and updates `hwm_watermarks`.

### Layer 05: Silver Staging (`05_silver_staging`)
- **Purpose**: Performs foundational data hygiene and deduplication.
- **Transformations**:
  - Trims leading/trailing whitespace from string attributes.
  - Converts email addresses to lowercase.
  - Imputes default fallback values for null numerical metrics (e.g. `churn_risk_score`).
  - Executes windowed deduplication over entity primary key ordered by `updated_at DESC, _ingest_timestamp DESC`.

### Layer 06: Silver (`06_silver`)
- **Purpose**: Curates business entities using Delta Lake `MERGE INTO` operations.
- **SCD Type 1 (Overwrite Current State)**:
  - Applied to `stores`, `products`, `orders`, `order_items`, `product_returns`, `customer_interactions`.
  - Merges incoming records matching primary key and overwrites attribute values.
- **SCD Type 2 (History Preservation)**:
  - Applied to `customers`.
  - Tracks changes in profile attributes (`email`, `phone`, `city`, `state`, `segment`, `churn_risk_score`).
  - Computes `row_hash` using `SHA-256` of tracked columns.
  - Computes `surrogate_key` using `SHA-256(customer_id || effective_start_date)`.
  - Updates existing active record (`is_current = True`) setting `is_current = False` and `effective_end_date = incoming.updated_at`.
  - Inserts new record with `is_current = True`, `effective_start_date = incoming.updated_at`, and `effective_end_date = '9999-12-31 23:59:59'`.

### Layer 07: Gold (`07_gold`)
- **Purpose**: Constructs an analytics-ready Dimensional Star Schema and specialized Power BI business data marts.
- **Dimensional Star Schema**:
  - `dim_date`: Generated calendar date dimension (2023-2026).
  - `dim_customer`: Customer dimension with SCD Type 2 fields (`customer_sk`, `churn_risk_band`).
  - `dim_product`: Product dimension with hierarchy (`product_sk`, `category`, `subcategory`).
  - `dim_store`: Store dimension (`store_sk`, `sqft_area`, `region`).
  - `fact_sales`: Line-item order transaction facts (`gross_sales_amount`, `discount_amount`, `net_sales_amount`, `profit_amount`, `profit_margin_pct`).
  - `fact_returns`: Product return event facts (`refund_amount`, `return_reason`).

---

## 3. Unity Catalog Data Architecture

```
retail_catalog (Unity Catalog)
├── bronze (Schema)
│   ├── hwm_watermarks
│   ├── customers
│   ├── customer_interactions
│   ├── stores
│   ├── products
│   ├── orders
│   ├── order_items
│   └── product_returns
│
├── silver (Schema)
│   ├── customers (SCD Type 2)
│   ├── customer_interactions (SCD Type 1)
│   ├── stores (SCD Type 1)
│   ├── products (SCD Type 1)
│   ├── orders (SCD Type 1)
│   ├── order_items (SCD Type 1)
│   └── product_returns (SCD Type 1)
│
└── gold (Schema)
    ├── dim_date
    ├── dim_customer
    ├── dim_product
    ├── dim_store
    ├── fact_sales
    ├── fact_returns
    ├── gold_sales_performance_mart
    ├── gold_customer_churn_mart
    ├── gold_product_quality_mart
    └── gold_store_analytics_mart
```

---

## 4. Power BI Business Data Marts & Analytical Metrics

### 1. Sales Performance Mart (`gold_sales_performance_mart`)
- **Grain**: Region x Store x Category x Year x Month
- **Metrics**:
  - `total_net_sales`: Sum of net sales amount after discounts.
  - `total_gross_sales`: Sum of gross sales amount before discounts.
  - `total_discounts`: Sum of discount amounts applied.
  - `total_orders`: Count of distinct order IDs.
  - `total_units_sold`: Sum of item quantities sold.
  - `avg_profit_margin_pct`: Average profit margin percentage across line items.

### 2. Customer Churn Mart (`gold_customer_churn_mart`)
- **Grain**: Customer Segment x City x Churn Risk Band
- **Metrics**:
  - `customer_count`: Count of active customers in segment/city/risk band.
  - `avg_churn_risk_score`: Average churn propensity score (0.0 to 1.0).
  - `total_support_tickets`: Total support tickets submitted by group.
- **Risk Bands**:
  - `High Risk`: `churn_risk_score >= 0.70`
  - `Medium Risk`: `0.40 <= churn_risk_score < 0.70`
  - `Low Risk`: `churn_risk_score < 0.40`

### 3. Product Quality Mart (`gold_product_quality_mart`)
- **Grain**: Category x Subcategory x Product
- **Metrics**:
  - `units_sold`: Total quantity sold.
  - `return_count`: Total return events recorded.
  - `refund_amount`: Total monetary refund value issued.
  - `avg_quality_rating`: Average customer product rating score.
  - `return_rate_pct`: `(return_count / units_sold) * 100`

### 4. Store Analytics Mart (`gold_store_analytics_mart`)
- **Grain**: Store ID x Store Name x Region x Store Type
- **Metrics**:
  - `total_revenue`: Total net sales generated by store.
  - `total_orders`: Total order volume completed by store.
  - `avg_order_value`: Average transaction value per order (`total_revenue / total_orders`).
  - `revenue_per_sqft`: Store sales efficiency metric (`total_revenue / sqft_area`).

---

## 5. Directory & Project Structure

```
Assignment8/
├── config/
│   ├── __init__.py
│   └── settings.py
├── data_generator/
│   ├── __init__.py
│   └── generate_source_data.py
├── databricks_notebooks/
│   ├── 01_setup_catalog.py
│   └── 02_pipeline_job.py
├── layers/
│   ├── __init__.py
│   ├── layer_01_inbound.py
│   ├── layer_02_raw.py
│   ├── layer_03_landing.py
│   ├── layer_04_bronze.py
│   ├── layer_05_silver_staging.py
│   ├── layer_06_silver.py
│   └── layer_07_gold.py
├── utils/
│   ├── __init__.py
│   ├── hwm_manager.py
│   ├── scd_handler.py
│   ├── schema_definitions.py
│   └── spark_session.py
├── README.md
├── requirements.txt
├── run_pipeline.py
└── validate_pipeline.py
```

---

## 6. Local & Databricks Execution Instructions

### Local Environment Setup

1. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the end-to-end master pipeline (generates source datasets, executes Batch 1 historical load, and executes Batch 2 incremental load):
   ```bash
   python run_pipeline.py
   ```

3. Execute the pipeline verification suite:
   ```bash
   python validate_pipeline.py
   ```

### Databricks Deployment

1. Import the `Assignment8` project into Databricks Workspace or Repos.
2. Run `databricks_notebooks/01_setup_catalog.py` to create the `retail_catalog` Unity Catalog schemas.
3. Configure a **Databricks Workflow Job** pointing to `databricks_notebooks/02_pipeline_job.py` with parameters:
   - Task 1: `batch_01` (Initial Load)
   - Task 2: `batch_02` (Incremental Scheduled Job)
