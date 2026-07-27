# Python Pipeline Scripts Directory
Contains reusable, production-ready Python modules and execution scripts for data ingestion, cleaning, and transformation.

## Production pipeline example
The repository now includes a modular pipeline script at [scripts/pipeline.py](pipeline.py) that follows the ingest-process-output pattern and adds defensible null handling:

- `ingest_data()` reads raw CSV data
- `analyze_missing_before()` reports missing values before any treatment
- `apply_missing_value_strategies()` applies median, mode, forward-fill, and row-dropping strategies with an audit trail
- `process_data()` cleans and enriches the data
- `output_results()` writes the processed results to disk
- `run_pipeline()` orchestrates the workflow end to end

Run it from the repository root with:

```bash
python scripts/pipeline.py
```

The pipeline writes its output to [data/processed/payments_summary.csv](../data/processed/payments_summary.csv) and logs activity to [output/pipeline.log](../output/pipeline.log).