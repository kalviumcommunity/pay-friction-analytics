# 1. IMPORTS - Dependencies loaded once at the top for clarity
import logging
import sys
from pathlib import Path

import pandas as pd

# Ensure UTF-8 stdout on Windows so confirmation symbols print correctly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 2. CONFIGURATION - Paths and thresholds in one place for easy modification
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "sample.csv"
OUTPUT_FILE = PROJECT_ROOT / "output" / "processed.csv"
LOG_FILE = PROJECT_ROOT / "logs" / "workflow.log"
MIN_AMOUNT = 0
MAX_RETRY_COUNT = 5

# 3. LOGGING SETUP - Record pipeline steps for debugging unattended runs
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def ingest_data(filepath):
    """
    Load payment transaction data from a CSV file into a Pandas DataFrame.

    This function handles ingestion only. It reads the file and returns raw data
    without applying any transformations.

    Args:
        filepath (str | Path): Path to the source CSV file.

    Returns:
        pd.DataFrame: Raw transaction records with columns such as
            transaction_id, customer_id, amount, status, retry_count,
            and bank_response_code.

    Raises:
        FileNotFoundError: If the source file does not exist.
        pd.errors.EmptyDataError: If the CSV file contains no data rows.

    Assumptions:
        - Input is a valid CSV with a header row.
        - File encoding is UTF-8.
    """
    filepath = Path(filepath)

    try:
        # Read CSV as-is; cleaning happens in process_data
        df = pd.read_csv(filepath)
        logging.info("Ingested %s rows from %s", len(df), filepath)
        return df
    except FileNotFoundError:
        logging.error("File not found: %s", filepath)
        raise FileNotFoundError(
            f"Ingestion failed: source file not found at '{filepath}'"
        ) from None
    except pd.errors.EmptyDataError:
        logging.error("Empty data file: %s", filepath)
        raise ValueError(
            f"Ingestion failed: '{filepath}' contains no data rows"
        ) from None


def process_data(df, min_amount=MIN_AMOUNT, max_retry_count=MAX_RETRY_COUNT):
    """
    Transform raw payment data into an analysis-ready DataFrame.

    Applies cleaning, filtering, and derived column creation. This function
    performs pure transformation with no file I/O.

    Args:
        df (pd.DataFrame): Raw transaction data from ingest_data().
        min_amount (float): Minimum transaction amount to retain (default: 0).
        max_retry_count (int): Maximum retry attempts to include (default: 5).

    Returns:
        pd.DataFrame: Cleaned data with duplicates removed, nulls filled,
            invalid rows filtered, and a friction_category column added.

    Assumptions:
        - Required columns exist: amount, retry_count, status.
        - Numerical nulls in amount can be filled with the column median.
    """
    rows_before = len(df)

    # Remove exact duplicate rows (identical across all columns)
    df = df.drop_duplicates()

    # Fill missing numeric values with median to preserve row count for analysis
    # Median resists outliers from high-value transactions
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    # Keep transactions above the minimum amount threshold
    df = df[df["amount"] >= min_amount]

    # Exclude records with excessive retries (likely permanent failures)
    df = df[df["retry_count"] <= max_retry_count]

    # Classify payment outcomes for friction vs permanent loss analysis
    df["friction_category"] = df.apply(
        lambda row: "temporary_friction"
        if row["status"] == "failed" and row["retry_count"] <= 2
        else "permanent_loss"
        if row["status"] == "failed"
        else "successful",
        axis=1,
    )

    rows_after = len(df)
    logging.info("Processing: %s rows -> %s rows", rows_before, rows_after)
    return df


def output_results(df, output_path):
    """
    Persist processed results to a CSV file and print execution confirmation.

    This function handles delivery only. It does not transform data.

    Args:
        df (pd.DataFrame): Processed data from process_data().
        output_path (str | Path): Destination path for the output CSV file.

    Assumptions:
        - Parent directory for output_path exists or can be created.
        - df is non-empty after processing.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    logging.info("Output saved: %s (%s rows)", output_path, len(df))

    display_path = (
        output_path.relative_to(PROJECT_ROOT)
        if output_path.is_relative_to(PROJECT_ROOT)
        else output_path
    )
    print("✓ Data successfully processed")
    print(f"✓ Rows processed: {len(df)}")
    print(f"✓ Output saved to {display_path}")


# 5. MAIN EXECUTION - Orchestrate ingest -> process -> output workflow
if __name__ == "__main__":
    try:
        print("Starting PayFriction data workflow...")
        data = ingest_data(INPUT_FILE)
        processed = process_data(data)
        output_results(processed, OUTPUT_FILE)
        print("✓ Workflow completed successfully")
    except Exception as error:
        logging.error("Workflow failed: %s", error)
        print(f"Error: {error}")
        raise SystemExit(1) from error
