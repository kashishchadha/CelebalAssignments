# PySpark Data Processing & Architecture — Assignment 6

![PySpark](https://img.shields.io/badge/PySpark-4.2.0-orange?logo=apachespark)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter)

A comprehensive guide and submission repository for **Spark Assignment 6**. This repository covers fundamental Spark architecture, core data structures, execution mechanics, file formats (CSV vs. Parquet), data transformations, filtering pipelines, and real-world Superstore sales analytics.

---

## 📌 Table of Contents

- [Overview & Architecture](#-overview--architecture)
- [Folder Architecture](#-folder-architecture)
- [Setup & Environment Prerequisites](#-setup--environment-prerequisites)
- [How to Run the Assignment](#-how-to-run-the-assignment)
- [Questions & Core Concepts](#-questions--core-concepts)
  - [Q1: Driver, Cluster Manager & Executor Roles](#q1-explain-the-roles-of-the-driver-cluster-manager-and-executor-in-a-spark-application)
  - [Q2: Lazy Evaluation Strategy & Optimizations](#q2-how-does-sparks-lazy-evaluation-strategy-improve-performance-when-chain-processing-large-datasets)
  - [Q3: Reading CSV Files with Headers & Schema Inference](#q3-write-a-spark-command-to-read-a-csv-file-located-at-datasourcecsv-ensuring-the-first-row-is-treated-as-a-header-and-inferschema-is-enabled)
  - [Q4: Storage Comparison: CSV (Row-Based) vs. Parquet (Columnar)](#q4-what-is-the-difference-between-csv-and-parquet-in-terms-of-storage-row-based-vs-columnar-and-why-does-it-matter-for-performance)
  - [Q5: Filtering & Selecting Specific Columns](#q5-given-a-dataframe-df-write-a-query-to-select-the-columns-product_id-and-price-where-the-category-is-electronics)
  - [Q6: Renaming Columns and Type Casting](#q6-write-the-code-to-revise-a-dataframe-by-renaming-the-column-old_name-to-new_name-and-casting-the-price-column-from-a-string-to-a-double)
  - [Q7: Fault Tolerance with Lineage Graphs (DAG)](#q7-how-does-spark-use-the-lineage-graph-dag-to-provide-fault-tolerance-if-a-worker-node-fails)
  - [Q8: Multi-Condition Filtering (AND Logic)](#q8-write-a-query-to-filter-a-dataframe-df_orders-for-rows-where-the-status-is-completed-and-the-amount-is-greater-than-1000)
  - [Q9: Predicate Pushdown in Parquet Storage](#q9-explain-the-concept-of-predicate-pushdown-in-parquet-and-how-it-affects-the-amount-of-data-loaded-into-memory)
  - [Q10: Adding Calculated Columns (Tax Addition)](#q10-write-a-code-snippet-to-add-a-new-column-final_price-which-is-the-base_price-multiplied-by-118-18-tax)
  - [Q11: Transformations vs. Actions](#q11-what-is-the-difference-between-transformations-and-actions-provide-two-examples-of-each)
  - [Q12: End-to-End Pipeline (Parquet Read -> Filter Nulls -> CSV Export)](#q12-write-the-spark-command-to-load-a-parquet-file-from-pathtoinput-filter-out-any-rows-where-user_id-is-null-and-save-the-result-as-a-csv-at-pathtooutput)
  - [Q13: Deployment Modes: Client Mode vs. Cluster Mode](#q13-in-spark-architecture-what-is-the-difference-between-client-mode-and-cluster-mode)
  - [Q14: Logical OR Filtering](#q14-write-a-query-to-filter-a-dataset-for-rows-where-the-region-is-north-or-the-priority-is-high)
  - [Q15: Safe Data Exploration: `.show()` vs. `.collect()`](#q15-when-exploring-a-dataset-why-is-it-safer-to-use-show5-instead-of-collect-on-a-multi-terabyte-dataset)
- [Output Deliverables Summary](#-output-deliverables-summary)
- [Troubleshooting & Windows Support](#-troubleshooting--windows-support)

---

## 🏗️ Overview & Architecture

PySpark is the Python API for Apache Spark, designed for fast, distributed large-scale data processing. This assignment demonstrates:
1. **Architectural Foundations**: Driver-Executor interaction, Cluster Managers, and Deployment Modes.
2. **Execution Engine Mechanics**: Lazy evaluation, Catalyst Optimizer, DAG lineage, and Fault Tolerance.
3. **Data Storage & I/O**: Structural differences and performance implications of Row-oriented (CSV) vs. Columnar (Parquet) formats.
4. **PySpark DataFrames API**: Filtering, column mutations, type casting, schema inference, null handling, aggregation metrics, and disk exports.

---

## 📁 Folder Architecture

```text
Assignment6/
├── data/                                 # Raw input data directory
│   ├── Sample - Superstore.csv           # Global Superstore retail dataset (~9,994 rows)
│   ├── source.csv                        # Transactions source dataset for Q3-Q14
│   └── input_parquet/
│       └── data.parquet                  # Sample Parquet format dataset for Q12
├── output/                               # Processed pipeline export deliverables
│   ├── completed_large_orders.csv        # Output for Q8 (Status = Completed & Amount > 1000)
│   ├── electronics_items.csv             # Output for Q5 (Category = Electronics)
│   ├── filtered_users_output.csv         # Output for Q12 (Non-null user_id filter)
│   ├── north_or_high_priority.csv        # Output for Q14 (Region = North OR Priority = High)
│   ├── revised_sales.csv                 # Output for Q6 (Renamed column + cast price)
│   ├── superstore_analytics.csv          # Aggregate metrics (Category & Sub-Category Sales)
│   └── tax_calculated.csv                # Output for Q10 (18% tax addition)
├── Spark_Assignment.ipynb                # Fully executed Jupyter Notebook with outputs
└── README.md                             # Comprehensive assignment report & documentation
```

---

## ⚙️ Setup & Environment Prerequisites

Before running the notebook, ensure your local environment meets the following requirements:

1. **Python 3.10+**: Ensure Python is installed.
2. **Java Development Kit (JDK 11, 17, or 21)**: Apache Spark requires Java JVM.
   ```powershell
   java -version
   ```
3. **Environment Variables**: `JAVA_HOME` should point to your JDK installation path.
4. **Python Dependencies**: Installed inside your virtual environment (`.venv`):
   ```powershell
   pip install pyspark pandas pyarrow jupyter ipykernel
   ```

---

## 🚀 How to Run the Assignment

### Option A: Interactive VS Code / Jupyter Interface (Recommended)
1. Open [Spark_Assignment.ipynb](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/Spark_Assignment.ipynb) in VS Code.
2. Click **Select Kernel** at the top right corner.
3. Select **Python Environments...** and pick the workspace environment:  
   `.venv (Python 3.12.x) .venv\Scripts\python.exe`
4. Click **Run All** or execute cells individually with `Shift + Enter`.

### Option B: Jupyter Notebook Browser
```powershell
cd Assignment6
..\.venv\Scripts\jupyter-notebook.exe Spark_Assignment.ipynb
```

### Option C: Headless Terminal Execution
```powershell
cd Assignment6
..\.venv\Scripts\python.exe -c "import json; nb=json.load(open('Spark_Assignment.ipynb', encoding='utf-8')); [exec(''.join(c['source'])) for c in nb['cells'] if c['cell_type']=='code']"
```

---

## ❓ Questions & Core Concepts

### Q1: Explain the roles of the Driver, Cluster Manager, and Executor in a Spark application.

A Spark application operates on a master-worker architecture comprising three primary components:

```
                  +-----------------------------------+
                  |           DRIVER NODE             |
                  |  - SparkSession / SparkContext    |
                  |  - DAG Scheduler / Task Scheduler |
                  +-----------------+-----------------+
                                    |
                        Resource Request / Allocation
                                    v
                  +-----------------------------------+
                  |          CLUSTER MANAGER          |
                  |   (YARN / Kubernetes / Standalone)|
                  +-----------------+-----------------+
                                    |
                        Launches / Monitors Executors
                                    v
         +--------------------------+--------------------------+
         |                                                     |
         v                                                     v
+------------------+                                 +------------------+
|    EXECUTOR 1    |                                 |    EXECUTOR 2    |
| - Runs Tasks     |                                 | - Runs Tasks     |
| - In-Memory Cache|                                 | - In-Memory Cache|
+------------------+                                 +------------------+
```

* **Driver Node**: The central control process hosting the `SparkSession`. It parses user code, creates a logical execution plan, translates transformations into a Directed Acyclic Graph (DAG), divides work into stages and tasks, and schedules task execution across worker nodes.
* **Cluster Manager**: An external resource orchestrator (such as YARN, Kubernetes, or Spark Standalone). It manages cluster node allocations and provisions JVM containers for Executors.
* **Executors**: Distributed worker processes launched on cluster nodes. They execute individual tasks assigned by the Driver, store cached data partitions in RAM/Disk, and report execution metrics back to the Driver.

---

### Q2: How does Spark’s Lazy Evaluation strategy improve performance when chain-processing large datasets?

> [!NOTE]  
> **Lazy Evaluation** means Spark registers dataset transformations (`filter`, `select`, `join`) into an internal logical plan without computing them immediately. Computation only occurs when an **Action** (`show`, `count`, `collect`, `write`) is called.

#### Performance Advantages:
1. **Catalyst Optimizer Rules**: Spark inspects the entire transformation chain before execution, enabling optimization techniques like operation merging, dead-code elimination, and column pruning.
2. **Predicate Pushdown**: Filter statements are pushed directly to file source readers (e.g., Parquet / ORC), avoiding unnecessary disk reads for non-matching records.
3. **Pipeline Merging**: Multiple consecutive narrow transformations (e.g., `map` -> `filter`) execute in a single memory pass per partition, preventing expensive temporary file writes to disk.

---

### Q3: Write a Spark command to read a CSV file located at "data/source.csv", ensuring the first row is treated as a header and inferSchema is enabled.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("CSV_Reader").getOrCreate()

sales_df = (
    spark.read.option("header", "true")
    .option("inferSchema", "true")
    .csv("data/source.csv")
)

sales_df.printSchema()
```

---

### Q4: What is the difference between CSV and Parquet in terms of storage (row-based vs. columnar) and why does it matter for performance?

| Feature | CSV (Row-Based) | Parquet (Columnar) |
| :--- | :--- | :--- |
| **Storage Structure** | Stores data row-by-row in uncompressed text format. | Stores data column-by-column in compressed binary format. |
| **Read Efficiency** | Must scan and parse full lines even to read 1 column. | Reads only requested columns, skipping unneeded byte ranges. |
| **Compression Ratio** | Low (mixed datatypes in identical storage blocks). | High (homogenous data types enable Snappy/Dictionary compression). |
| **Schema Metadata** | Missing (requires scanning data to infer schema). | Embedded in file footers (datatype, row counts, min/max statistics). |
| **I/O Speed** | Disk-bound and network-heavy on large datasets. | Extremely fast disk I/O with Predicate Pushdown support. |

---

### Q5: Given a DataFrame df, write a query to select the columns product_id and price where the category is 'Electronics'.

```python
import pyspark.sql.functions as func

electronics_df = sales_df.filter(func.col("category") == "Electronics").select(
    "product_id", "price"
)

electronics_df.show()
```

---

### Q6: Write the code to "revise" a DataFrame by renaming the column old_name to new_name and casting the price column from a String to a Double.

```python
import pyspark.sql.functions as func

revised_df = sales_df.withColumnRenamed("old_name", "new_name").withColumn(
    "price", func.col("price").cast("double")
)

revised_df.printSchema()
```

---

### Q7: How does Spark use the Lineage Graph (DAG) to provide fault tolerance if a worker node fails?

Because Spark DataFrames and RDDs are **immutable**, Spark does not rely on expensive data replication across cluster nodes. Instead, it logs every transformation applied to a dataset in a **Lineage Graph (DAG)**.

```
[Raw CSV Source] ---> (Filter Category) ---> (Rename Column) ---> (Cast Price)
```

If a worker node crashes and loses a data partition:
1. The Driver detects partition failure.
2. It references the Lineage Graph for that specific partition.
3. The Driver re-executes only the required sequence of transformations to reconstruct the lost partition on an active worker node, eliminating full job restarts.

---

### Q8: Write a query to filter a DataFrame df_orders for rows where the status is 'Completed' AND the amount is greater than 1000.

```python
import pyspark.sql.functions as func

completed_large_orders = sales_df.filter(
    (func.col("status") == "Completed") & (func.col("amount") > 1000)
)

completed_large_orders.show()
```

---

### Q9: Explain the concept of Predicate Pushdown in Parquet and how it affects the amount of data loaded into memory.

> [!TIP]  
> **Predicate Pushdown** evaluates filter expressions at the file-storage layer *before* data is transferred into executor RAM.

Parquet files divide data into **Row Groups** and record minimum and maximum column statistics in metadata footers. When executing a query like `df.filter(col("amount") > 1000)`:
- Spark inspects the Parquet footer statistics.
- If a Row Group's `max(amount)` is `<= 1000`, Spark skips reading that entire Row Group from disk.
- This drastically reduces disk read operations, network transfer latency, and JVM heap memory usage.

---

### Q10: Write a code snippet to add a new column final_price which is the base_price multiplied by 1.18 (18% tax).

```python
import pyspark.sql.functions as func

tax_calculated_df = sales_df.withColumn(
    "final_price", func.round(func.col("base_price") * 1.18, 2)
)

tax_calculated_df.select("product_id", "base_price", "final_price").show()
```

---

### Q11: What is the difference between Transformations and Actions? Provide two examples of each.

```
Transformations (Lazy)  ---> Build Logical Plan (DAG)
Actions (Eager)         ---> Trigger Spark Execution Job
```

* **Transformations**: Operations that return a new DataFrame without evaluating data immediately. They construct the execution plan.
  * *Examples*: `.filter()`, `.withColumn()`, `.select()`, `.groupBy()`
* **Actions**: Operations that trigger task execution, compute results, and return values to the Driver or write outputs to storage.
  * *Examples*: `.show()`, `.count()`, `.collect()`, `.write.csv()`

---

### Q12: Write the Spark command to load a Parquet file from "path/to/input", filter out any rows where user_id is null, and save the result as a CSV at "path/to/output".

```python
import pyspark.sql.functions as func

(
    spark.read.parquet("data/input_parquet/data.parquet")
    .filter(func.col("user_id").isNotNull())
    .write.mode("overwrite")
    .option("header", "true")
    .csv("output/filtered_users_output")
)
```

---

### Q13: In Spark Architecture, what is the difference between Client Mode and Cluster Mode?

| Feature | Client Mode | Cluster Mode |
| :--- | :--- | :--- |
| **Driver Location** | Runs on the user machine (submitting host/laptop). | Runs inside a worker container inside the cluster. |
| **Network Latency** | High driver-to-executor communication overhead over WAN. | Low latency (driver and executors share cluster network). |
| **Use Case** | Interactive exploration, Jupyter notebooks, debugging. | Scheduled production batch jobs (Airflow / cron). |
| **Fault Tolerance** | If user machine disconnects, the job terminates. | Fully managed by Cluster Manager; resilient to disconnects. |

---

### Q14: Write a query to filter a dataset for rows where the region is 'North' OR the priority is 'High'.

```python
import pyspark.sql.functions as func

north_or_high_priority = sales_df.filter(
    (func.col("region") == "North") | (func.col("priority") == "High")
)

north_or_high_priority.show()
```

---

### Q15: When exploring a dataset, why is it safer to use .show(5) instead of .collect() on a multi-terabyte dataset?

> [!CAUTION]  
> Executing `.collect()` on multi-terabyte datasets can instantly crash your Driver node due to **Java OutOfMemoryError (OOM)**!

* **`.collect()`**: Transfers **all rows** across all distributed executor partitions over the network into the single Driver JVM memory space. On large datasets, memory allocation exceeds heap limits and crashes the application.
* **`.show(5)`**: Fetches only the **first 5 records** from the first partition. It uses minimal network bandwidth and negligible memory, making it safe for data inspection.

---

## 📊 Output Deliverables Summary

All pipeline execution outputs generated during notebook runs are stored in the [output/](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/output/) directory:

| Exported File | Description | Source Question / Feature |
| :--- | :--- | :--- |
| [superstore_analytics.csv](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/output/superstore_analytics.csv) | Revenue, order counts & avg sales per Category/Sub-Category | Superstore Dataset Analysis |
| [tax_calculated.csv](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/output/tax_calculated.csv) | `final_price` calculated with 18% tax addition | Question 10 |
| [filtered_users_output.csv](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/output/filtered_users_output.csv) | Parquet input dataset filtered for non-null `user_id` | Question 12 |
| [north_or_high_priority.csv](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/output/north_or_high_priority.csv) | Filtered for Region = 'North' OR Priority = 'High' | Question 14 |
| [completed_large_orders.csv](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/output/completed_large_orders.csv) | Orders with Status = 'Completed' and Amount > 1000 | Question 8 |
| [revised_sales.csv](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/output/revised_sales.csv) | Renamed column `old_name` -> `new_name` & cast `price` | Question 6 |
| [electronics_items.csv](file:///c:/Users/hp/Desktop/CelebalAssignments/Assignment6/output/electronics_items.csv) | Selected `product_id` & `price` where Category = 'Electronics' | Question 5 |

---

## 🛠️ Troubleshooting & Windows Support

If you encounter errors on Windows laptops:

1. **`ModuleNotFoundError: No module named 'pyspark'`**:
   Ensure VS Code notebook kernel is set to `.venv\Scripts\python.exe`.
2. **`JAVA_HOME is not set` / `Py4JJavaError`**:
   Install OpenJDK 17 or 21 and verify environment variables:
   ```powershell
   echo $env:JAVA_HOME
   ```
3. **PySpark Worker Connection Errors**:
   Cell 1 configures `PYSPARK_PYTHON` automatically. If running custom scripts, add:
   ```python
   import os, sys

   os.environ["PYSPARK_PYTHON"] = sys.executable
   os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
   ```
