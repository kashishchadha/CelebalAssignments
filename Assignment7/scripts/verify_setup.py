"""
verify_setup.py
---------------
Run this BEFORE opening the notebooks. It checks every prerequisite in order and
tells you exactly what to fix if something is missing.

    python scripts/verify_setup.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

OK, BAD, WARN = "[ OK ]", "[FAIL]", "[WARN]"
failures = []


def check(label, ok, detail="", fix=""):
    print(f"{OK if ok else BAD} {label}" + (f"  -> {detail}" if detail else ""))
    if not ok:
        failures.append((label, fix))
    return ok


print("=" * 68)
print("DELTA LAKE ASSIGNMENT — ENVIRONMENT CHECK")
print("=" * 68)

# 1. Python ------------------------------------------------------------------
v = sys.version_info
check(
    "Python 3.9 – 3.12",
    (3, 9) <= (v.major, v.minor) <= (3, 12),
    f"{v.major}.{v.minor}.{v.micro}",
    "PySpark 3.5 does not support Python 3.13+. Create the venv with python3.11.",
)
print(f"       interpreter: {sys.executable}")

# 2. Virtual environment -----------------------------------------------------
in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
if not in_venv:
    print(f"{WARN} Not running inside a virtual environment (recommended, not required)")

# 3. Java --------------------------------------------------------------------
java = shutil.which("java")
if check("Java on PATH", java is not None, java or "",
         "Install Temurin JDK 17 from https://adoptium.net and reopen the terminal."):
    out = subprocess.run(["java", "-version"], capture_output=True, text=True)
    line = (out.stderr or out.stdout).strip().splitlines()[0]
    print(f"       {line}")
    ver = "".join(ch for ch in line.split('"')[1] if ch.isdigit() or ch == ".") if '"' in line else ""
    major = ver.split(".")[0]
    if major == "1":
        major = ver.split(".")[1]
    if major.isdigit() and int(major) not in (8, 11, 17, 21):
        print(f"{WARN} Java {major} is untested with Spark 3.5. Java 17 is the safe choice.")

jh = os.environ.get("JAVA_HOME")
if not jh:
    print(f"{WARN} JAVA_HOME is not set. Spark usually copes, but set it if the session fails.")
else:
    print(f"       JAVA_HOME = {jh}")

# 4. Python packages ---------------------------------------------------------
for mod, label in [
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("matplotlib", "matplotlib"),
    ("pyspark", "pyspark"),
    ("delta", "delta-spark"),
]:
    try:
        m = __import__(mod)
        check(f"package: {label}", True, getattr(m, "__version__", "installed"))
    except ImportError:
        check(f"package: {label}", False, "not installed",
              "Run: pip install -r requirements.txt")

# 5. Data files --------------------------------------------------------------
root = Path(__file__).resolve().parent.parent
for f in ["superstore_orders.csv", "customer_master.csv", "customer_incremental.csv"]:
    p = root / "data" / f
    check(f"data file: {f}", p.exists(),
          f"{p.stat().st_size:,} bytes" if p.exists() else "missing",
          "Run: python scripts/generate_datasets.py")

# 6. Windows-specific --------------------------------------------------------
if os.name == "nt":
    hh = os.environ.get("HADOOP_HOME")
    if hh and (Path(hh) / "bin" / "winutils.exe").exists():
        check("Windows: winutils.exe", True, str(Path(hh) / "bin" / "winutils.exe"))
    else:
        check(
            "Windows: HADOOP_HOME + winutils.exe", False, "not found",
            "See README -> 'Windows extra step'. Without it, Spark cannot write local files.",
        )

# 7. Spark smoke test --------------------------------------------------------
print("-" * 68)
print("Starting a Spark session (first run downloads the Delta jars — be patient)...")
try:
    python_executable = sys.executable
    os.environ.setdefault("PYSPARK_PYTHON", python_executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", python_executable)

    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession

    builder = (
        SparkSession.builder.appName("SetupCheck").master("local[2]")
        .config("spark.pyspark.python", python_executable)
        .config("spark.pyspark.driver.python", python_executable)
        .config("spark.executorEnv.PYSPARK_PYTHON", python_executable)
        .config("spark.executorEnv.PYSPARK_DRIVER_PYTHON", python_executable)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.shuffle.partitions", "2")
    )
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    check("Spark session started", True, f"Spark {spark.version}")

    tmp = root / "output" / "_setup_check_delta"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.parent.mkdir(exist_ok=True)

    df = spark.sql("SELECT 1 AS id, 'a' AS val UNION ALL SELECT 2 AS id, 'b' AS val")
    df.write.format("delta").mode("overwrite").save(tmp.resolve().as_uri())
    n = spark.read.format("delta").load(tmp.resolve().as_uri()).count()
    check("Delta write + read", n == 2, f"{n} rows round-tripped")

    shutil.rmtree(tmp, ignore_errors=True)
    spark.stop()
except Exception as exc:  # noqa: BLE001
    check("Spark / Delta smoke test", False, type(exc).__name__,
          "Read the error above. Most common causes: no JDK, no internet on first run "
          "(Delta jars come from Maven), or missing winutils on Windows.")
    print(f"\n       {exc}\n")

# ---------------------------------------------------------------------------
print("=" * 68)
if failures:
    print(f"{len(failures)} CHECK(S) FAILED — fix these before running the notebooks:\n")
    for label, fix in failures:
        print(f"  * {label}\n      {fix}")
    sys.exit(1)

print("ALL CHECKS PASSED. Open notebooks/01_pandas_basics.ipynb and start running cells.")
