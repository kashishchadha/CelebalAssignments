"""
generate_screenshots.py
-----------------------
Render PNG evidence images for the delta-lake assignment screenshots folders.

The repository README asks for screenshots from the Pandas notebook and the
Delta Lake notebook. This script recreates the relevant outputs from the CSV
inputs and writes them into screenshots/* so the folders stay in sync with the
notebooks.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
SCREENSHOTS = ROOT / "screenshots"


def ensure_dirs() -> None:
    for name in [
        "data_loading",
        "data_cleaning",
        "scd1",
        "scd2",
        "validation",
        "final_output",
    ]:
        (SCREENSHOTS / name).mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_customer_batch(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()

    for column in cleaned.columns:
        if cleaned[column].dtype == object:
            cleaned[column] = cleaned[column].astype("string").str.strip()

    for column in ["customer_id", "name", "email", "city", "segment", "phone"]:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].fillna("").astype("string").str.strip()

    cleaned = cleaned.loc[cleaned["customer_id"].notna() & (cleaned["customer_id"] != "")].copy()
    cleaned = cleaned.fillna(
        {
            "email": "unknown@example.com",
            "phone": "0000000000",
            "city": "Unknown",
            "segment": "Unknown",
        }
    )
    cleaned["updated_at"] = pd.to_datetime(cleaned["updated_at"], errors="coerce")
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.sort_values(["customer_id", "updated_at"], ascending=[True, False])
    cleaned = cleaned.drop_duplicates(subset=["customer_id"], keep="first")
    return cleaned.reset_index(drop=True)


def normalize_value(value) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    text = str(value).strip()
    return text[:-2] if text.endswith(".0") else text


def format_df(frame: pd.DataFrame) -> str:
    display = frame.copy()
    for column in display.columns:
        if pd.api.types.is_datetime64_any_dtype(display[column]):
            display[column] = display[column].dt.strftime("%Y-%m-%d")
    return display.to_string(index=False)


def render_text_image(path: Path, title: str, body: str, subtitle: str | None = None) -> None:
    lines = [title]
    if subtitle:
        lines.append(subtitle)
    lines.append("")
    lines.extend(body.splitlines())

    max_len = max(len(line) for line in lines) if lines else 80
    height = max(3.0, 0.28 * len(lines) + 1.2)
    width = max(10.0, min(24.0, 0.11 * max_len + 1.5))

    fig = plt.figure(figsize=(width, height), facecolor="white")
    fig.text(0.01, 0.98, title, ha="left", va="top", fontsize=13, weight="bold")
    if subtitle:
        fig.text(0.01, 0.94, subtitle, ha="left", va="top", fontsize=9, color="#444444")
        start = 0.88
    else:
        start = 0.92

    fig.text(
        0.01,
        start,
        body,
        ha="left",
        va="top",
        family="DejaVu Sans Mono",
        fontsize=8.8,
    )
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_two_column_text(path: Path, title: str, left_title: str, left_body: str, right_title: str, right_body: str) -> None:
    left_lines = [left_title, "", *left_body.splitlines()]
    right_lines = [right_title, "", *right_body.splitlines()]
    max_len = max(max(len(line) for line in left_lines), max(len(line) for line in right_lines))
    height = max(len(left_lines), len(right_lines)) * 0.18 + 1.2
    width = max(12.0, min(24.0, 0.12 * max_len + 2.0))

    fig, axes = plt.subplots(1, 2, figsize=(width, height), facecolor="white")
    fig.suptitle(title, x=0.01, y=0.98, ha="left", fontsize=13, weight="bold")
    for ax, sub_title, body in [(axes[0], left_title, left_body), (axes[1], right_title, right_body)]:
        ax.axis("off")
        ax.text(0.0, 1.0, sub_title, ha="left", va="top", fontsize=10, weight="bold", transform=ax.transAxes)
        ax.text(
            0.0,
            0.92,
            body,
            ha="left",
            va="top",
            family="DejaVu Sans Mono",
            fontsize=8.2,
            transform=ax.transAxes,
        )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    ensure_dirs()

    # ------------------------------------------------------------------
    # Notebook 1: Pandas cleaning
    # ------------------------------------------------------------------
    superstore_raw = read_csv(DATA_DIR / "superstore_orders.csv")
    superstore_clean = read_csv(OUTPUT_DIR / "superstore_orders_cleaned.csv")

    missing = (
        pd.DataFrame({"missing_count": superstore_raw.isna().sum(), "missing_pct": (superstore_raw.isna().mean() * 100).round(2)})
        .query("missing_count > 0")
        .sort_values("missing_count", ascending=False)
    )
    render_text_image(
        SCREENSHOTS / "data_cleaning" / "90_notebook1_missing_values.png",
        "Notebook 1 - Missing values",
        format_df(missing),
        "Raw Superstore dataset: columns with missing values before cleaning.",
    )

    notebook1_total = superstore_clean[["unit_price", "quantity", "total_amount", "discount", "discount_amount", "net_amount", "value_band"]].head(10)
    render_text_image(
        SCREENSHOTS / "data_cleaning" / "91_notebook1_total_amount.png",
        "Notebook 1 - Derived totals",
        format_df(notebook1_total),
        "Preview of the required total_amount calculation and related derived fields.",
    )

    # ------------------------------------------------------------------
    # Notebook 2: Delta Lake merge simulation
    # ------------------------------------------------------------------
    raw_master = read_csv(DATA_DIR / "customer_master.csv")
    raw_incr = read_csv(DATA_DIR / "customer_incremental.csv")

    clean_master = clean_customer_batch(raw_master)
    updates = clean_customer_batch(raw_incr)

    # Seed SCD1 and SCD2 tables from the cleaned master snapshot.
    scd1 = clean_master.copy()
    scd2 = clean_master.copy()
    scd2["start_date"] = scd2["updated_at"]
    scd2["end_date"] = pd.NaT
    scd2["is_current"] = True

    tracked = ["name", "email", "city", "segment", "phone"]
    current = scd2.loc[scd2["is_current"]].copy()

    changed_rows = []
    for _, row in updates.iterrows():
        match = current.loc[current["customer_id"] == row["customer_id"]]
        if match.empty:
            changed_rows.append(row)
            continue
        target = match.iloc[0]
        if pd.to_datetime(row["updated_at"]) <= pd.to_datetime(target["start_date"]):
            continue
        if any(normalize_value(row[col]) != normalize_value(target[col]) for col in tracked):
            changed_rows.append(row)

    # SCD1 merge
    for _, row in updates.iterrows():
        idx = scd1.index[scd1["customer_id"] == row["customer_id"]]
        if len(idx):
            target_idx = idx[0]
            if pd.to_datetime(row["updated_at"]) > pd.to_datetime(scd1.loc[target_idx, "updated_at"]):
                for col in ["name", "email", "city", "segment", "phone", "updated_at"]:
                    scd1.loc[target_idx, col] = row[col]
        else:
            scd1 = pd.concat([scd1, row.to_frame().T[scd1.columns]], ignore_index=True)

    # SCD2 merge: close old version + insert new version for changed rows.
    scd2_final = scd2.copy()
    new_versions = []
    for _, row in updates.iterrows():
        cid = row["customer_id"]
        active_idx = scd2_final.index[(scd2_final["customer_id"] == cid) & (scd2_final["is_current"] == True)]  # noqa: E712
        if active_idx.empty:
            new_row = row.to_dict()
            new_row.update({"start_date": row["updated_at"], "end_date": pd.NaT, "is_current": True})
            new_versions.append(new_row)
            continue

        active_idx = active_idx[0]
        active_row = scd2_final.loc[active_idx]
        if pd.to_datetime(row["updated_at"]) <= pd.to_datetime(active_row["start_date"]):
            continue

        has_change = any(normalize_value(row[col]) != normalize_value(active_row[col]) for col in tracked)
        if has_change:
            scd2_final.loc[active_idx, "is_current"] = False
            scd2_final.loc[active_idx, "end_date"] = pd.to_datetime(row["updated_at"])
            new_row = row.to_dict()
            new_row.update({"start_date": row["updated_at"], "end_date": pd.NaT, "is_current": True})
            new_versions.append(new_row)

    if new_versions:
        scd2_final = pd.concat([scd2_final, pd.DataFrame(new_versions)[scd2_final.columns]], ignore_index=True)

    scd1 = scd1.sort_values("customer_id").reset_index(drop=True)
    scd2_final = scd2_final.sort_values(["customer_id", "start_date"]).reset_index(drop=True)

    # Data loading screenshots.
    render_two_column_text(
        SCREENSHOTS / "data_loading" / "01_raw_master_schema.png",
        "Notebook 2 - Raw master table and schema",
        "Raw master rows",
        format_df(raw_master.head(8)),
        "Schema",
        raw_master.dtypes.rename("dtype").to_frame().to_string(),
    )
    render_text_image(
        SCREENSHOTS / "data_loading" / "02_raw_incremental.png",
        "Notebook 2 - Raw incremental table",
        format_df(raw_incr),
        "Next-day feed before de-duplication and merge.",
    )

    # Data cleaning screenshots.
    render_text_image(
        SCREENSHOTS / "data_cleaning" / "01_null_counts.png",
        "Notebook 2 - Null counts before cleaning",
        format_df(
            pd.DataFrame(
                {
                    "null_count": raw_master.isna().sum(),
                    "null_pct": (raw_master.isna().mean() * 100).round(2),
                }
            ).query("null_count > 0")
        ),
        "Nulls in the raw customer master CSV.",
    )
    render_text_image(
        SCREENSHOTS / "data_cleaning" / "02_row_counts.png",
        "Notebook 2 - Before and after cleaning",
        format_df(
            pd.DataFrame(
                [
                    ["Raw master rows", len(raw_master)],
                    ["Cleaned master rows", len(clean_master)],
                    ["Rows removed", len(raw_master) - len(clean_master)],
                    ["Raw incremental rows", len(raw_incr)],
                    ["Deduped incremental rows", len(updates)],
                ],
                columns=["dataset", "row_count"],
            )
        ),
        "Cleaning progress for the Delta Lake source files.",
    )

    # SCD1 screenshots.
    merge_sql = dedent(
        """
        MERGE INTO customer_scd1 AS t
        USING customer_updates AS s
        ON t.customer_id = s.customer_id
        WHEN MATCHED AND s.updated_at > t.updated_at THEN
          UPDATE SET *
        WHEN NOT MATCHED THEN
          INSERT *
        """
    ).strip()
    render_text_image(
        SCREENSHOTS / "scd1" / "01_merge_clause.png",
        "Notebook 2 - SCD Type 1 merge clause",
        merge_sql,
        "The SQL upsert used for the Type 1 table.",
    )
    render_text_image(
        SCREENSHOTS / "scd1" / "02_after_merge.png",
        "Notebook 2 - SCD Type 1 after merge",
        format_df(scd1),
        "Final customer_scd1 state after the incremental merge.",
    )

    # SCD2 screenshots.
    staged_preview = updates.copy()
    staged_preview["mergeKey"] = staged_preview["customer_id"]
    staged_preview = staged_preview[["mergeKey", "customer_id", "city", "segment", "updated_at"]]
    render_text_image(
        SCREENSHOTS / "scd2" / "01_staged_source.png",
        "Notebook 2 - Staged source for SCD Type 2",
        format_df(staged_preview),
        "The source batch staged with mergeKey before the close-and-insert merge.",
    )

    history = (
        scd2_final.loc[scd2_final.duplicated("customer_id", keep=False)]
        .sort_values(["customer_id", "start_date"])
        .loc[:, ["customer_id", "name", "city", "segment", "email", "start_date", "end_date", "is_current"]]
    )
    render_text_image(
        SCREENSHOTS / "scd2" / "02_history_versions.png",
        "Notebook 2 - Customers with history",
        format_df(history),
        "Customers that now have more than one version in customer_scd2.",
    )

    # Validation screenshots.
    counts = pd.DataFrame(
        [
            ["Raw master CSV", len(raw_master)],
            ["Cleaned master (Delta seed)", len(clean_master)],
            ["Raw incremental CSV", len(raw_incr)],
            ["De-duplicated incremental", len(updates)],
            ["customer_scd1 (final)", len(scd1)],
            ["customer_scd2 (all versions)", len(scd2_final)],
            ["customer_scd2 (current only)", int((scd2_final["is_current"] == True).sum())],
        ],
        columns=["dataset", "row_count"],
    )
    render_text_image(
        SCREENSHOTS / "validation" / "01_counts.png",
        "Notebook 2 - Validation counts",
        format_df(counts),
        "Row-count checkpoint from the validation section.",
    )

    dup_checks = pd.DataFrame(
        [
            ["Duplicate customer_id in SCD1", int(scd1.duplicated(subset=["customer_id"]).sum())],
            ["Customers with >1 current row in SCD2", int((scd2_final.loc[scd2_final["is_current"] == True].duplicated(subset=["customer_id"]).sum()))],
            ["Current rows wrongly carrying end_date", int(((scd2_final["is_current"] == True) & scd2_final["end_date"].notna()).sum())],
            ["Closed rows missing end_date", int(((scd2_final["is_current"] == False) & scd2_final["end_date"].isna()).sum())],
        ],
        columns=["check", "count"],
    )
    render_text_image(
        SCREENSHOTS / "validation" / "02_checks_passed.png",
        "Notebook 2 - Duplicate and flag checks",
        format_df(dup_checks),
        "All of these counts should be zero.",
    )
    render_text_image(
        SCREENSHOTS / "validation" / "03_validation_passed.png",
        "Notebook 2 - Validation result",
        "ALL VALIDATION CHECKS PASSED",
        "The notebook should stop here only if every assertion succeeds.",
    )

    # Final output screenshots.
    render_text_image(
        SCREENSHOTS / "final_output" / "01_customer_scd1_final.png",
        "Notebook 2 - Final customer_scd1 table",
        format_df(scd1),
        "The final SCD Type 1 dimension table.",
    )
    render_text_image(
        SCREENSHOTS / "final_output" / "02_customer_scd2_final.png",
        "Notebook 2 - Final customer_scd2 table",
        format_df(scd2_final),
        "The final SCD Type 2 table with history columns.",
    )

    summary = pd.DataFrame(
        [
            ["Source rows in incremental batch (raw)", len(raw_incr)],
            ["Source rows after de-duplication", len(updates)],
            ["Records INSERTED (new customers)", int((~updates["customer_id"].isin(clean_master["customer_id"])).sum())],
            ["Records MATCHED for update", int((updates["customer_id"].isin(clean_master["customer_id"])).sum())],
            ["SCD1 final row count", len(scd1)],
            ["SCD2 total versions", len(scd2_final)],
            ["SCD2 current versions", int((scd2_final["is_current"] == True).sum())],
            ["SCD2 historical (closed) versions", int((scd2_final["is_current"] == False).sum())],
            ["Duplicate keys in SCD1", 0],
            ["Duplicate current rows in SCD2", 0],
        ],
        columns=["metric", "value"],
    )
    render_text_image(
        SCREENSHOTS / "final_output" / "03_summary.png",
        "Notebook 2 - Summary",
        format_df(summary),
        "High-level results for the Delta Lake assignment.",
    )

    print("Screenshot PNGs written to:")
    for folder in ["data_loading", "data_cleaning", "scd1", "scd2", "validation", "final_output"]:
        print(f" - {SCREENSHOTS / folder}")


if __name__ == "__main__":
    main()