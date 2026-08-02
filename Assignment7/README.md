# Delta Lake Assignment — Pandas Cleaning + Incremental `MERGE` (SCD Type 1 & Type 2)

Two notebooks, runnable end to end in VS Code, plus a small helper script that can regenerate the screenshot evidence:

| Notebook | What it covers |
|---|---|
| `notebooks/01_pandas_basics.ipynb` | Python + Pandas: load CSV, explore, handle nulls, filter, de-duplicate, derive `total_amount = price × quantity`, save cleaned CSV |
| `notebooks/02_delta_lake_merge.ipynb` | Delta Lake: load into a Delta table, clean, simulate an incremental batch, `MERGE` for SCD Type 1 and Type 2, validate, summarise |
| `scripts/generate_screenshots.py` | Rebuilds the PNG evidence under `screenshots/` from the checked-in CSV outputs |

Everything needed is in this repo — the datasets are included, nothing has to be
downloaded from Kaggle.

## At a glance

If you want the shortest path to a finished submission:

1. Create and activate `.venv`.
2. Run `python scripts/verify_setup.py` until it says `ALL CHECKS PASSED`.
3. Open `notebooks/01_pandas_basics.ipynb` and run it top to bottom.
4. Open `notebooks/02_delta_lake_merge.ipynb` and run it top to bottom.
5. If you want the screenshot folders refreshed, run `python scripts/generate_screenshots.py`.
6. Use `report/assignment_summary.md` as the write-up for the final submission.

---

## Table of contents

1. [Requirements](#1-requirements)
2. [Setup — step by step](#2-setup--step-by-step)
3. [Windows extra step (winutils)](#3-windows-extra-step-winutils)
4. [Running the notebooks in VS Code](#4-running-the-notebooks-in-vs-code)
5. [What each notebook produces](#5-what-each-notebook-produces)
6. [Screenshots to capture](#6-screenshots-to-capture)
7. [Pushing to GitHub](#7-pushing-to-github)
8. [Troubleshooting](#8-troubleshooting)
9. [Project structure](#9-project-structure)
10. [Concepts reference](#10-concepts-reference)

---

## 1. Requirements

| Thing | Version | Why |
|---|---|---|
| **Python** | **3.9 – 3.12** (3.11 recommended) | PySpark 3.5 does **not** support Python 3.13+ |
| **Java (JDK)** | **17** (11 also fine) | Spark runs on the JVM |
| **VS Code** | any recent | plus the *Python* and *Jupyter* extensions |
| **Internet** | on first run only | Delta Lake jars are pulled from Maven Central once, then cached |
| **Disk** | ~1.5 GB | Spark + Delta jars |

Notebook 1 (Pandas) needs **none of the Java/Spark machinery** — if you only want to
submit Assignment 1, you can skip straight to it after `pip install pandas numpy matplotlib`.

---

## 2. Setup — step by step

### Step 1 — Install a JDK

Download **Eclipse Temurin JDK 17** from <https://adoptium.net>.
During install, tick **"Set JAVA_HOME variable"** if the installer offers it.

Verify in a **new** terminal:

```bash
java -version
```

You should see something like `openjdk version "17.0.x"`.

If `JAVA_HOME` is not set:

<details>
<summary><b>Windows</b></summary>

```powershell
setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-17.0.11.9-hotspot"
setx PATH "%PATH%;%JAVA_HOME%\bin"
```
Close and reopen the terminal afterwards.
</details>

<details>
<summary><b>macOS / Linux</b></summary>

```bash
# add to ~/.zshrc or ~/.bashrc
export JAVA_HOME=$(/usr/libexec/java_home -v 17)   # macOS
# export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64   # Linux
export PATH=$JAVA_HOME/bin:$PATH
```
</details>

### Step 2 — Open the project in VS Code

```bash
cd delta-lake-assignment
code .
```

### Step 3 — Create a virtual environment

Open the VS Code terminal (`` Ctrl + ` ``) and run:

<details open>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
</details>

<details>
<summary><b>macOS / Linux</b></summary>

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```
</details>

Your prompt should now start with `(.venv)`.

### Step 4 — Install the Python packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This takes a few minutes — PySpark is a ~300 MB wheel.

### Step 5 — Verify the environment

```bash
python scripts/verify_setup.py
```

This checks Python, Java, every package, the data files, and finally starts a real Spark
session and does a Delta write + read. **The first run downloads the Delta jars from
Maven, so give it 1–3 minutes.** Do not move on until you see:

```
ALL CHECKS PASSED
```

If a check fails, the script prints the exact fix. See also
[Troubleshooting](#8-troubleshooting).

---

## 3. Windows extra step (winutils)

Spark uses Hadoop's filesystem layer, and on Windows that needs a small native helper.
**Without it, Delta writes fail with `HADOOP_HOME and hadoop.home.dir are unset` or
`UnsatisfiedLinkError`.**

1. Create a folder `C:\hadoop\bin`.
2. Download **`winutils.exe`** and **`hadoop.dll`** for **Hadoop 3.3.x** from
   <https://github.com/cdarlint/winutils> (folder `hadoop-3.3.6/bin`).
3. Put both files in `C:\hadoop\bin`.
4. Set the environment variables:

```powershell
setx HADOOP_HOME "C:\hadoop"
setx PATH "%PATH%;C:\hadoop\bin"
```

5. **Close and reopen VS Code entirely** (environment variables are read at process start).

> **Easier alternative:** run the whole project inside **WSL2 (Ubuntu)**. No winutils
> needed, and Spark is noticeably faster. VS Code's *WSL* extension makes this seamless.

---

## 4. Running the notebooks in VS Code

1. Install the VS Code extensions **Python** (`ms-python.python`) and
   **Jupyter** (`ms-toolsai.jupyter`) if you haven't.
2. Open `notebooks/01_pandas_basics.ipynb`.
3. Click **Select Kernel** in the top-right → **Python Environments** → pick the
   interpreter inside `.venv`.
   *(If `.venv` isn't listed: `Ctrl+Shift+P` → "Python: Select Interpreter" → Enter
   interpreter path → browse to `.venv\Scripts\python.exe` or `.venv/bin/python`.)*
4. Click **Run All**, or step through with `Shift + Enter`.
5. Repeat for `notebooks/02_delta_lake_merge.ipynb`.

**Order matters:** run notebook 1 first, then notebook 2. Each notebook is independently
re-runnable — notebook 2 deletes and rebuilds its Delta tables at the start, so you can
run it as many times as you like and always get the same result.

### Expected runtimes

| Notebook | First run | Later runs |
|---|---|---|
| 01 — Pandas | ~10 seconds | ~10 seconds |
| 02 — Delta Lake | 2–4 minutes (jar download + JVM start) | ~60–90 seconds |

If you are only refreshing the PNG evidence, `python scripts/generate_screenshots.py` is much faster than re-running the Spark notebook.

---

## 5. What each notebook produces

Everything lands in `output/` (which is git-ignored except for the CSV results):

| File | From |
|---|---|
| `output/superstore_orders_cleaned.csv` | Notebook 1, step 7 |
| `output/customer_scd1_final.csv` | Notebook 2, section 9 |
| `output/customer_scd2_final.csv` | Notebook 2, section 9 |
| `output/delta/customer_scd1/` | Delta table (Parquet + `_delta_log`) |
| `output/delta/customer_scd2/` | Delta table with full history |
| `output/delta/customer_sync_demo/` | `WHEN NOT MATCHED BY SOURCE` demo |
| `screenshots/*/*.png` | Regenerated evidence images for the notebook checkpoints |

### Headline numbers you should see in notebook 2

| Metric | Value |
|---|---|
| Master CSV rows → after cleaning | 18 → 15 |
| Incremental CSV rows → after de-dup | 10 → 8 |
| Records inserted (new customers) | 3 |
| Records matched for update | 5 |
| `customer_scd1` final rows | **18** |
| `customer_scd2` total versions | **22** |
| `customer_scd2` current versions | **18** |
| Duplicate keys anywhere | **0** |

Section 8 asserts all of this — if an assertion fires, something genuinely went wrong.

---

## 6. Screenshots to capture

Save them into the matching folder. Windows: `Win + Shift + S`. macOS: `Cmd + Shift + 4`.
If you prefer reproducible artifacts, run `python scripts/generate_screenshots.py` and use the PNGs it creates.

| Folder | What to capture |
|---|---|
| `screenshots/data_loading/` | Notebook 2 §1 raw master table + schema, and §4 raw incremental table |
| `screenshots/data_cleaning/` | Notebook 1 missing-values and `total_amount` outputs, plus Notebook 2 §2 null-count table and row-count comparison |
| `screenshots/scd1/` | Notebook 2 §5 the merge clause and the `AFTER merge` result table |
| `screenshots/scd2/` | Notebook 2 §6 the staged source, and the "customers that now have HISTORY" output |
| `screenshots/validation/` | Notebook 2 §8 counts table, duplicate checks, `ALL VALIDATION CHECKS PASSED` |
| `screenshots/final_output/` | Notebook 2 §9 both final tables and the summary table |

Notebook 1's missing-values and `total_amount` outputs are already represented in `screenshots/data_cleaning/`.

---

## 7. Pushing to GitHub

```bash
git init
git add .
git commit -m "Delta Lake assignment: pandas cleaning + SCD1/SCD2 merge"
git branch -M main
git remote add origin https://github.com/<your-username>/delta-lake-assignment.git
git push -u origin main
```

`.gitignore` already excludes `.venv/`, `output/delta/`, `spark-warehouse/`,
`.ipynb_checkpoints/` and `metastore_db/`, so only source, data, notebooks, screenshots
and the small result CSVs get committed.

**Before pushing, run both notebooks top to bottom** so the saved `.ipynb` files contain
their outputs — a reviewer should be able to read the results without running anything.

---

## 8. Troubleshooting

<details>
<summary><b><code>JAVA_GATEWAY_EXITED</code> / "Java gateway process exited before sending its port number"</b></summary>

Spark could not start the JVM. In order of likelihood:

1. No JDK installed, or `java -version` fails in the terminal → install Temurin 17.
2. `JAVA_HOME` points at a JRE or a stale path → fix it, reopen VS Code.
3. Java 22+ installed — too new for Spark 3.5. Install 17 alongside and point
   `JAVA_HOME` at it.
4. **First run with no internet** — the Delta jars come from Maven Central. Connect and
   retry; after one successful run they're cached in `~/.ivy2`.
</details>

<details>
<summary><b><code>Python worker exited unexpectedly</code> / worker version mismatch</b></summary>

The driver and worker are using different Python interpreters. Notebook 2 already sets
`PYSPARK_PYTHON` and `PYSPARK_DRIVER_PYTHON` to `sys.executable` in section 0 — make sure
you ran that cell, and that the selected kernel is the `.venv` one.

Also confirm Python is ≤ 3.12: `python -c "import sys; print(sys.version)"`.
</details>

<details>
<summary><b><code>HADOOP_HOME and hadoop.home.dir are unset</code> (Windows)</b></summary>

You need `winutils.exe` — see [section 3](#3-windows-extra-step-winutils). A plain
*warning* about this in the log is harmless; a *failure* on write means winutils is
genuinely missing.
</details>

<details>
<summary><b><code>Cannot perform Merge as multiple source rows matched…</code></b></summary>

The source batch has more than one row per key. Notebook 2 handles this in section 4.1
with a `row_number()` window — make sure you ran that cell rather than merging `raw_incr`
directly. This is the single most common Delta `MERGE` error.
</details>

<details>
<summary><b><code>DELTA_MISSING_DELTA_TABLE</code> or "is not a Delta table"</b></summary>

Section 3 was skipped or a previous run was interrupted. Delete the `output/delta/`
folder and run notebook 2 from the top.
</details>

<details>
<summary><b>Port binding / "Service 'sparkDriver' could not bind"</b></summary>

An old Spark session is still alive. Restart the notebook kernel
(`Ctrl+Shift+P` → "Jupyter: Restart Kernel"). The last cell of notebook 2 calls
`spark.stop()` for exactly this reason.
</details>

<details>
<summary><b>It's very slow</b></summary>

Normal for local Spark — JVM startup and query planning dominate on datasets this small.
`spark.sql.shuffle.partitions` is already lowered to 4. On Windows, WSL2 is faster.
</details>

<details>
<summary><b>I want to use the real Kaggle Superstore dataset</b></summary>

Download `Sample - Superstore.csv` from
<https://www.kaggle.com/datasets/vivek468/superstore-dataset-final>, put it in `data/`,
then in notebook 1 section 1 set:

```python
CSV_PATH = os.path.join(DATA_DIR, "Sample - Superstore.csv")
PRICE_COL, QTY_COL = "Sales", "Quantity"
```

The Kaggle file has no missing values and uses different column names, so the null-handling
cells will report zero nulls and the string/date cells will need their column names adjusted.
</details>

---

## 9. Project structure

```
delta-lake-assignment/
│
├── data/
│   ├── superstore_orders.csv         # Assignment 1 source (messy on purpose)
│   ├── customer_master.csv           # Assignment 2 initial full load
│   └── customer_incremental.csv      # Assignment 2 incremental batch
│
├── notebooks/
│   ├── 01_pandas_basics.ipynb        # Assignment 1
│   └── 02_delta_lake_merge.ipynb     # Assignment 2
│
├── scripts/
│   ├── verify_setup.py               # run this first
│   ├── generate_datasets.py          # regenerates data/ if needed
│   └── generate_screenshots.py       # rebuilds screenshot PNGs from the CSV outputs
│
├── screenshots/
│   ├── data_loading/  data_cleaning/  scd1/
│   └── scd2/  validation/  final_output/
│
├── output/                           # generated — CSVs kept, Delta tables ignored
│
├── report/
│   └── assignment_summary.md         # write-up; export to PDF for submission
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 10. Concepts reference

### Why `MERGE`?

A plain `INSERT` duplicates existing customers; a plain `OVERWRITE` rewrites the whole
table and destroys history. `MERGE` decides row by row, in **one atomic ACID transaction** —
either all of it lands or none of it does.

```sql
MERGE INTO target t
USING source s
ON t.key = s.key
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE
```

### SCD Type 1 vs Type 2

| | Type 1 | Type 2 |
|---|---|---|
| On change | overwrite in place | close the old row, insert a new one |
| History | none | complete |
| Extra columns | none | `start_date`, `end_date`, `is_current` |
| Row count | one per key | one per key **per version** |
| Answers | "where does this customer live?" | "where did they live last March?" |
| Cost | cheap | more storage, more complex queries |

### The three gotchas this project demonstrates

1. **Duplicate source rows break `MERGE`.** Only one source row may match a given target
   row. De-duplicate the batch first (§4.1).
2. **Late-arriving data can overwrite newer data.** Guard the matched clause with
   `s.updated_at > t.updated_at` (§5).
3. **No-op updates create junk history in Type 2.** Compare tracked attributes with the
   null-safe operator `<=>` so unchanged records produce no new version (§6).

### Useful Delta commands

```sql
DESCRIBE HISTORY  customer_scd2;   -- full audit trail
DESCRIBE DETAIL   customer_scd1;   -- file count, size, location
SELECT * FROM customer_scd2 VERSION AS OF 0;   -- time travel
OPTIMIZE customer_scd1;            -- compact small files
VACUUM   customer_scd1 RETAIN 168 HOURS;       -- drop old versions
```

### References

- Delta Lake `MERGE` — <https://learn.microsoft.com/en-us/azure/databricks/delta/merge>
- `MERGE INTO` SQL reference — <https://docs.delta.io/latest/delta-update.html>
- Superstore dataset — <https://www.kaggle.com/datasets/vivek468/superstore-dataset-final>
