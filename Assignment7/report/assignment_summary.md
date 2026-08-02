# Assignment Summary

**Name:** _<your name>_
**Date:** _<date>_
**Repository:** _<your GitHub URL>_

---

## Part 1 — Python & Pandas: exploration and cleaning

**Notebook:** `notebooks/01_pandas_basics.ipynb`
**Source:** `data/superstore_orders.csv` — a Superstore-style order file seeded with
missing values, duplicate rows and untidy text.

### What was done

**Loading.** `pd.read_csv()` read the file into a DataFrame.

**Exploration.** `.shape`, `.columns`, `.dtypes`, `.head()`, `.tail()`, `.sample()`,
`.info()`, `.describe()` and `.value_counts()` established the size, structure and
distribution of the data before anything was changed.

**Missing values.** `.isnull().sum()` located them; the strategy was then chosen per
column rather than applied blindly:

| Column | Strategy | Reasoning |
|---|---|---|
| `unit_price` | median fill | median resists the skew a few high-priced items create |
| `quantity` | median fill, cast to `int` | must remain a whole number |
| `discount` | fill with `0` | a missing discount most plausibly means none was applied |
| `city`, `segment`, `customer_name` | fill with `"Unknown"` | keeps the row usable |
| `order_id`, `product_id` | drop the row | a record with no key cannot be joined or de-duplicated |

Text columns were also stripped of whitespace and case-normalised, and the two date
columns were parsed with `pd.to_datetime(..., dayfirst=True)`.

**Basic operations.** Column selection (single column vs list), `.loc` / `.iloc`, boolean
filtering with `&` / `|`, `.isin()`, `.between()`, sorting and a `groupby().agg()`.

**Duplicates.** Removed in two passes: exact duplicate rows via `.drop_duplicates()`, then
business-key duplicates on `(order_id, product_id)` keeping the last occurrence.

**Derived columns.** The required `total_amount = unit_price × quantity`, plus
`discount_amount`, `net_amount`, `shipping_days`, `order_year`, `order_month`, and a
`value_band` built with `pd.cut()`.

**Output.** `output/superstore_orders_cleaned.csv`.

### Results

| Metric | Value |
|---|---|
| Rows loaded (raw) | _fill from notebook §8_ |
| Missing cells (raw) | _fill_ |
| Exact duplicates removed | _fill_ |
| Key duplicates removed | _fill_ |
| Rows after cleaning | _fill_ |
| Missing cells remaining | 0 |

---

## Part 2 — Delta Lake: incremental processing with `MERGE`

**Notebook:** `notebooks/02_delta_lake_merge.ipynb`
**Sources:** `data/customer_master.csv` (initial load), `data/customer_incremental.csv`
(simulated next-day feed).

### Approach

**1. Load and clean.** The master CSV was read into Spark, trimmed, filtered to drop the
row with a null `customer_id`, null-filled on optional attributes, date-cast on
`updated_at`, and de-duplicated — first exact rows, then one row per `customer_id` using a
`row_number()` window ordered by `updated_at DESC`. 18 raw rows became 15 clean ones.

**2. Write Delta tables.** The cleaned snapshot was written twice: `customer_scd1` as a
plain table, and `customer_scd2` with the history columns `start_date`, `end_date` and
`is_current`. Both were registered in the metastore so the SQL `MERGE` syntax could be
demonstrated alongside the Python API.

**3. Incremental batch.** The second CSV deliberately mixes five cases: genuine attribute
changes (`C002`, `C005`, `C009`, `C012`), a no-op identical to what was stored (`C001`),
three brand-new customers (`C016`–`C018`), a late-arriving *older* row for `C002`, and an
exact duplicate of `C017`. The same `row_number()` window collapsed 10 rows to 8 —
necessary because Delta rejects a `MERGE` where two source rows match one target row.

**4a. SCD Type 1.** A single `MERGE`:

```sql
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

The `s.updated_at > t.updated_at` guard is what stops the late-arriving `C002` row from
overwriting newer data. 15 rows became 18; no history retained.

**4b. SCD Type 2.** Delta's `MERGE` can take only one action per matched row, so the
standard **staged-source** pattern was used. Every incoming row was staged with
`mergeKey = customer_id` (matches the current version → closes it by setting
`is_current = false` and `end_date`). Rows whose tracked attributes had actually changed
were staged a *second* time with `mergeKey = NULL`, which can never match and therefore
falls through to `WHEN NOT MATCHED` → inserted as a new version.

Change detection used the null-safe operator: `NOT (t.city <=> s.city) OR …`. This is why
`C001` produced no new version — nothing about it had changed.

**5. Bonus.** `WHEN NOT MATCHED BY SOURCE` was demonstrated on a separate table to flag
customers absent from the incremental feed as `dormant` — a soft delete.

### Results

| Metric | Value |
|---|---|
| Master CSV rows → after cleaning | 18 → 15 |
| Incremental CSV rows → after de-dup | 10 → 8 |
| Records inserted (new customers) | 3 |
| Records matched for update | 5 |
| `customer_scd1` final rows | 18 |
| `customer_scd2` total versions | 22 |
| `customer_scd2` current versions | 18 |
| `customer_scd2` closed versions | 4 |
| Duplicate keys in SCD1 | 0 |
| Duplicate current rows in SCD2 | 0 |

### Validation performed

- Row counts compared at every stage.
- `groupBy("customer_id").count() > 1` returned zero rows for SCD1.
- Exactly one `is_current = true` row per customer in SCD2.
- Flag consistency: no current row carries an `end_date`, no closed row lacks one.
- Assertions that `C002` shows Bengaluru (the newer value won) and that `C001` still has
  exactly one version (the no-op created no junk history).
- `DESCRIBE HISTORY` showed the full transaction log, and version 0 was still readable
  via time travel.

---

## What I learned

- `MERGE` is a single atomic transaction that decides insert vs update vs delete per row —
  the reason it replaces the read-modify-overwrite pattern entirely.
- **De-duplicating the source batch is mandatory**, not a nicety. Two source rows matching
  one target row is an ambiguous update and Delta refuses it outright.
- **Late-arriving data is a real hazard.** Without a timestamp guard on the matched clause,
  an old record silently overwrites a newer one.
- **Type 2 needs null-safe comparison.** Ordinary `=` returns `NULL` when either side is
  `NULL`, so a genuine change involving a null attribute would be missed — and a no-op
  would create a spurious version.
- The `mergeKey`-with-`NULL` trick exists because one merge clause cannot both close a row
  and insert its replacement.
- Delta's transaction log gives an audit trail and time travel for free, which is the
  practical difference between a data lake and a pile of Parquet files.

---

## Files submitted

```
data/          three source CSVs
notebooks/     01_pandas_basics.ipynb, 02_delta_lake_merge.ipynb (with outputs)
output/        superstore_orders_cleaned.csv, customer_scd1_final.csv, customer_scd2_final.csv
screenshots/   data_loading, data_cleaning, scd1, scd2, validation, final_output
report/        this file
scripts/       verify_setup.py, generate_datasets.py
README.md      setup and run instructions
```

> To submit as PDF: open this file in VS Code, `Ctrl+Shift+V` for the Markdown preview,
> then print to PDF. Or install the *Markdown PDF* extension and right-click → *Export (pdf)*.
