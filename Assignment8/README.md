# E-Commerce Order Analytics

A compact, end-to-end analytics pipeline that demonstrates data-generation,
cleaning, ingestion into SQLite, and analytical reporting over messy e-commerce
order data. It's designed for teaching data-quality techniques, SQL reporting
patterns, and small-scale ETL flows.

## Highlights

- Clean, well-documented pipeline: data generation → cleaning → load → queries.
- Reproducible dataset with configurable error rates (`config.py`).
- 16 analytical queries that showcase window functions, CTEs, aggregation,
  and ranking.

## Quickstart

1. Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the full pipeline from the project root:

```bash
python src/generate_data.py    # produce data/raw/*.csv
python src/clean_data.py       # produce data/clean/* and reports/data_quality_report.*
python src/load_db.py          # creates data/ecommerce.db
python src/run_queries.py      # writes reports/query_output/*.csv
```

3. Optional: interactive report on the terminal:

```bash
python src/report_cli.py
python src/report_cli.py --type monthly --from 2025-01-01 --to 2025-06-30
```

Run a single query by passing its short name (e.g. `q09`):

```bash
python src/run_queries.py q09
```

## Requirements

- Python 3.9+ (SQLite included)
- See `requirements.txt` for runtime and test dependencies (pandas, pytest).

## Project layout

```
Assignment8/
├── config.py                # rates, file paths and generation settings
├── requirements.txt
├── data/
│   ├── raw/                 # generated, intentionally messy CSVs
│   ├── clean/               # cleaned CSVs + rejected rows
│   └── ecommerce.db         # SQLite database produced by load_db.py
├── reports/
│   ├── data_quality_report.md
│   ├── data_quality_report.json
│   └── query_output/        # CSV outputs for each query
├── sql/                     # schema and SQL query files
├── src/                     # pipeline scripts and CLI
└── tests/                   # pytest test coverage
```

## Data & cleaning notes (short)

- Revenue calculation is centralized in an `item_revenue` view so queries
  don't repeat business logic.
- Some rows are intentionally malformed (missing `customer_id`, negative
  quantities for returns, malformed dates, etc.). The rules for handling these
  are implemented in `src/clean_data.py` and enforced by DB constraints.
- Broken or rejected rows are written to `data/clean/rejected_order_items.csv`
  for inspection instead of being deleted.

## Testing

Run the test suite with:

```bash
pytest -v
```

## Troubleshooting

- If data files do not appear, confirm the working directory is the project
  root and that the virtual environment is activated.
- To regenerate everything from scratch, delete `data/` and `reports/` then
  re-run the pipeline commands above.

## Next steps / Extensions

- Persist the data-quality report into a table to track issues over time.
- Add an incremental ingestion path to avoid full rebuilds for each run.
- Wire the `report_cli.py` output to email or schedule it with a simple
  cron/task scheduler.

If you'd like, I can also:
- add example command outputs, or
- create a short CONTRIBUTING section with development tips.
