# scripts/pipeline.py
import pandas as pd
import logging
import argparse
import os
from datetime import datetime

# -----------------------------------------------------------------------------
# TASK 3: Configure Logging with Timestamps
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# TASK 1: Build the Complete Pipeline (Ingest, Clean, Aggregate, Output)
# -----------------------------------------------------------------------------
def ingest(file_path):
    """Stage 1: Load raw data."""
    logger.info(f"Starting ingestion from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully ingested {len(df)} rows.")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise

def clean(df):
    """Stage 2: Clean and validate data."""
    logger.info("Starting data cleaning...")
    initial_count = len(df)
    
    # Drop rows with missing critical information
    df = df.dropna(subset=["customer_id", "amount"])
    
    # Ensure amount is strictly numeric and positive
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df[df["amount"] > 0]
    
    logger.info(f"Cleaning complete: {initial_count} -> {len(df)} rows retained.")
    return df

def aggregate(df):
    """Stage 3: Compute business aggregations."""
    logger.info("Starting aggregation...")
    agg = df.groupby("segment").agg(
        total_revenue=("amount", "sum"),
        order_count=("order_id", "count"),
        avg_order=("amount", "mean")
    ).reset_index()
    
    # Round metrics for clean output
    agg["total_revenue"] = agg["total_revenue"].round(2)
    agg["avg_order"] = agg["avg_order"].round(2)
    
    logger.info(f"Aggregation complete: {len(agg)} segment groups processed.")
    return agg

def output(df, agg, output_dir):
    """Stage 4: Write output files."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Writing output files to: {output_dir}")
    df.to_csv(f"{output_dir}/cleaned_data.csv", index=False)
    agg.to_csv(f"{output_dir}/aggregated_metrics.csv", index=False)
    
    # TASK 5: Confirm output with log entry
    logger.info("✅ Pipeline execution complete. Files saved successfully.")

# -----------------------------------------------------------------------------
# TASK 2: Accept Parameters via CLI
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Data Processing Pipeline")
    parser.add_argument("--input", required=True, help="Path to raw CSV dataset")
    parser.add_argument("--output", default="data/processed", help="Directory for output files")
    args = parser.parse_args()

    logger.info("=== PIPELINE RUN INITIATED ===")
    
    # Execute the pipeline chain
    raw_data = ingest(args.input)
    cleaned_data = clean(raw_data)
    aggregated_data = aggregate(cleaned_data)
    output(cleaned_data, aggregated_data, args.output)