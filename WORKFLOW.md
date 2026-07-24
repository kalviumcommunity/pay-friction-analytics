# Data Workflow Documentation

This document describes how to run and maintain `scripts/data_workflow.py`, the production-ready pipeline for processing payment transaction data.

## How to Execute the Script

From the project root:

```bash
python scripts/data_workflow.py
```

Or from the scripts directory:

```bash
cd scripts
python data_workflow.py
```

Requirements: Python 3.x with dependencies installed (`pip install -r requirements.txt`).

## What Each Function Does

| Function | Responsibility | Input | Output |
|----------|----------------|-------|--------|
| `ingest_data(filepath)` | Reads raw CSV data from disk | Path to CSV file | Raw `pd.DataFrame` |
| `process_data(df)` | Cleans, filters, and enriches data | Raw DataFrame | Transformed DataFrame |
| `output_results(df, output_path)` | Writes results and prints confirmation | Processed DataFrame, output path | CSV file on disk |

### ingest_data

Loads `data/raw/sample.csv` (or any CSV path you provide). Performs no transformation. Raises a clear error if the file is missing or empty.

### process_data

- Removes duplicate rows
- Fills null numeric values with column medians
- Filters by minimum amount and maximum retry count
- Adds a `friction_category` column (`successful`, `temporary_friction`, or `permanent_loss`)

### output_results

Writes the processed DataFrame to `output/processed.csv` and prints row count and file path confirmation.

## How to Modify for New Datasets

1. **Change input/output paths** — Edit `INPUT_FILE` and `OUTPUT_FILE` at the top of `scripts/data_workflow.py`.
2. **Adjust filters** — Update `MIN_AMOUNT` or `MAX_RETRY_COUNT` in the configuration section.
3. **Add columns or logic** — Extend `process_data()` only; keep ingestion and output separate.
4. **New file format** — Update `ingest_data()` to read JSON or other formats; leave processing unchanged.

## Logs

Execution details are written to `logs/workflow.log` for debugging scheduled or unattended runs.

## Capture Sample Output

To save console output for verification:

```bash
python scripts/data_workflow.py > output/sample_run.txt
```
