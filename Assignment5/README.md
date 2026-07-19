# Spark DataFrames – Cleaning, Transformation and Aggregation

Week 5 assignment: the 15 Spark questions answered in one PySpark notebook, run
against a messy transactions dataset built on top of the Sample Superstore CSV
from the earlier weeks.

## Folder layout

```
week5/
├── data/      superstore.csv        (raw Superstore, same file as week 2)
│              prepare_dataset.py    (builds transactions.csv from it)
│              transactions.csv      (10,494 rows, deliberately messy)
├── output/    store_revenue.csv     (final pipeline result)
└── notebook/  week5_spark_analysis.ipynb
```

## The dataset

Superstore covers region, city, category, sales and quantity, but the questions
also need age, subscription, status, email, username, store_id and a raw
timestamp column. So `prepare_dataset.py` keeps all 9,994 Superstore rows,
derives the missing columns, and injects realistic problems on top:

- 300 exact duplicate rows and 200 "retried payment" rows that differ only by
  transaction id
- ~5% null prices, ~6% missing statuses, ~4% missing emails
- usernames that arrive as whitespace instead of empty
- ~1% of timestamps in a `d/m/yyyy h.m` format that breaks casting

Final file is 10,494 rows.

## How to run

```
pip install pyspark pyarrow jupyter
jupyter notebook
```

Open `notebook/week5_spark_analysis.ipynb` and run top to bottom. Needs a JDK on
the PATH (tested with PySpark 4.2 on Java 24). The run rewrites
`output/store_revenue.csv`.

## Answers

Full code and executed outputs are in the notebook; this is the short version.

**Q1 – MapReduce limitations.** MapReduce writes intermediate results to disk
after every stage, so multi-stage jobs become chains of full jobs each paying
the HDFS write/read tax. The model is rigid (everything must be a map + reduce
pair), there is no interactive querying, and iterative algorithms re-read the
input from disk on every pass. Spark plans the whole job as one DAG, keeps
intermediate data in memory, and covers SQL, streaming and ML in one platform.

**Q2 – In-memory computing for iterative ML.** Training loops (gradient
descent, k-means) pass over the same data dozens of times. Spark caches the
dataset in executor memory with `.cache()`, so iteration 1 pays the disk read
and every later iteration reads RAM – that is where the 10–100x speedups come
from. Lineage means a lost executor only recomputes its partitions.

**Q3 – Dedup on a column subset.**
```python
df.dropDuplicates(["user_id", "transaction_date"])
```
On this dataset that collapses 10,494 rows to 4,992, because every line item of
an order shares a customer and a date – choosing the right key is the real
decision.

**Q4 – West region, average sale per category.**
```python
df.filter(F.col("region") == "West") \
  .groupBy("product_category") \
  .agg(F.avg("sale_amount"))
```
Technology 414.36, Furniture 356.19, Office Supplies 116.57.

**Q5 – `.na.drop()` vs `.na.fill()`.** Drop removes rows containing nulls;
fill keeps the rows and substitutes a value. Filling status:
```python
df.na.fill({"status": "Unknown"})
```
That converted 627 null statuses into an explicit 'Unknown' bucket.

**Q6 – Cities with more than 100 records.** Aggregate first, then filter on
the aggregated value (the DataFrame version of HAVING):
```python
df.groupBy("city").count().filter(F.col("count") > 100)
```
13 cities qualify, led by New York City (967) and Los Angeles (781).

**Q7 – Immutability.** DataFrames are never edited in place – dropping or
renaming a column returns a new DataFrame and the original survives untouched.
So cleaning code is a chain of assignments, forgetting the assignment is the
classic silent bug, and you keep the raw DataFrame around for free comparison.

**Q8 – Age 18–30 and Premium.** `between` is inclusive on both ends:
```python
df.filter(F.col("age").between(18, 30) & (F.col("subscription") == "Premium"))
```
860 matching rows.

**Q9 – Nulls before aggregation.** Spark's aggregations skip nulls silently:
`avg()` divides by the non-null count, `sum()` of an all-null group is null,
and null keys form their own group. Demo from the notebook: avg price is 60.85
skipping the 503 nulls but 57.94 after filling with 0 – the choice has to be
deliberate.

**Q10 – Cast and rename.**
```python
df.withColumn("raw_timestamp", F.col("raw_timestamp").try_cast(TimestampType())) \
  .withColumnRenamed("raw_timestamp", "event_time")
```
Spark 4 runs ANSI mode by default, so a plain `cast` actually crashed on the
malformed rows; `try_cast` nulls them instead (114 here).

**Q11 – The shuffle.** Rows for one key are scattered across partitions, so
grouping forces Spark to hash-partition and physically move data: shuffle files
on disk, transfers over the network, a stage boundary in the DAG. Wide because
one output partition depends on many input partitions (a filter is narrow –
one-to-one). The notebook shows it as `Exchange hashpartitioning` in the
physical plan.

**Q12 – Null emails / empty usernames.**
```python
df.filter(F.col("email").isNotNull() & (F.trim(F.col("username")) != ""))
```
672 rows removed. The `trim` matters: the bad usernames arrive as whitespace,
which is neither null nor equal to `""`.

**Q13 – Multiple statistics in one `.agg()`.**
```python
df.agg(F.min("price"), F.max("price"), F.avg("price"))
```
min 0.34, max 3773.08, mean 60.85 – one pass over the data. Works the same
after a `groupBy` for per-category stats.

**Q14 – The `inferSchema` risk.** With messy dates, inference either types the
column as string (so date logic silently becomes alphabetical comparison) or –
worse – picks a date type from a clean-looking sample and turns every
off-format row into null with no error. This project hit the first case:
`raw_timestamp` came in as string because ~1% of rows use `d/m/yyyy h.m`.
In production: explicit schema, read messy dates as string, convert with
`to_timestamp` and known format patterns so failures are countable.

**Q15 – The pipeline.**
```python
line_cols = [c for c in df.columns if c != "transaction_id"]
(df.dropDuplicates(line_cols)
   .na.fill({"price": 0})
   .withColumn("revenue", F.col("price") * F.col("quantity"))
   .groupBy("store_id")
   .agg(F.sum("revenue").alias("total_revenue")))
```
Dedup ignores transaction_id so it catches both exact double-submits and
retried payments. Result in `output/store_revenue.csv`: S02 on top (~199.8k),
S05 last (~159.6k).

## Takeaways

Three things this week actually drove home. First, cleaning decisions change
your numbers silently – the dedup key and the null-handling strategy are
modelling choices, not syntax, and the same column can honestly report two
different averages depending on them. Second, Spark 4's ANSI default means old
"cast and let the bad rows null out" habits now crash jobs; `try_cast` and
explicit schemas are the way. Third, grouping is only expensive because of the
shuffle behind it – seeing `Exchange hashpartitioning` in the physical plan
makes the narrow/wide distinction concrete instead of theoretical.
