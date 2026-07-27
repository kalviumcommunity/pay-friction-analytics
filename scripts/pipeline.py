"""Production-ready pipeline for processing payment friction analytics data."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Union

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = PROJECT_ROOT / "output" / "pipeline.log"
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "payments.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "payments_summary.csv"
DEFAULT_THRESHOLD = 1

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def ingest_data(filepath: Union[str, Path]) -> pd.DataFrame:
    """Read payment data from a CSV file into a DataFrame.

    Args:
        filepath: Path to the input CSV file.

    Returns:
        A DataFrame containing the raw payment records.
    """
    path = Path(filepath)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    frame = pd.read_csv(path)
    logging.info("Ingested %s rows from %s", len(frame), path)
    return frame


def analyze_missing_before(frame: pd.DataFrame) -> List[str]:
    """Summarize missing values before any imputation is applied.

    Returns:
        A list of human-readable messages describing the missing-value profile.
    """
    if frame.empty:
        raise ValueError("Input DataFrame cannot be empty")

    report = []
    for column in frame.columns:
        null_count = int(frame[column].isnull().sum())
        if null_count > 0:
            null_pct = round((null_count / len(frame)) * 100, 1)
            report.append(f"{column}: {null_count} nulls ({null_pct}%)")
    return report


def apply_missing_value_strategies(frame: pd.DataFrame) -> tuple[pd.DataFrame, List[dict]]:
    """Apply a defensible null-handling strategy based on the column context.

    The function drops rows for critical identifiers, fills numeric columns with the median,
    fills categorical columns with the mode, and forward-fills time-like values when present.
    Each action is recorded as an audit entry for traceability.
    """
    if frame.empty:
        raise ValueError("Input DataFrame cannot be empty")

    working_frame = frame.copy()
    audit_log: List[dict] = []

    critical_columns = {"payment_id"}
    for column in critical_columns:
        if column in working_frame.columns:
            before_nulls = int(working_frame[column].isnull().sum())
            working_frame = working_frame.dropna(subset=[column])
            after_nulls = int(working_frame[column].isnull().sum())
            audit_log.append(
                {
                    "column": column,
                    "strategy": "drop_rows",
                    "reason": "Critical identifier values cannot be imputed safely.",
                    "before_nulls": before_nulls,
                    "after_nulls": after_nulls,
                }
            )

    for column in ["amount", "retry_count"]:
        if column in working_frame.columns:
            before_nulls = int(working_frame[column].isnull().sum())
            if pd.api.types.is_numeric_dtype(working_frame[column]):
                fill_value = working_frame[column].median()
                working_frame[column] = working_frame[column].fillna(fill_value)
                strategy = "median"
                reason = "Numeric fields use the median to reduce outlier distortion."
            else:
                working_frame[column] = pd.to_numeric(working_frame[column], errors="coerce")
                fill_value = working_frame[column].median()
                working_frame[column] = working_frame[column].fillna(fill_value)
                strategy = "median"
                reason = "Numeric fields use the median to reduce outlier distortion."
            after_nulls = int(working_frame[column].isnull().sum())
            audit_log.append(
                {
                    "column": column,
                    "strategy": strategy,
                    "reason": reason,
                    "before_nulls": before_nulls,
                    "after_nulls": after_nulls,
                }
            )

    for column in ["segment", "response_code"]:
        if column in working_frame.columns:
            before_nulls = int(working_frame[column].isnull().sum())
            if working_frame[column].dropna().empty:
                fill_value = "UNKNOWN"
            else:
                fill_value = working_frame[column].mode(dropna=True).iloc[0] if not working_frame[column].mode(dropna=True).empty else "UNKNOWN"
            working_frame[column] = working_frame[column].fillna(fill_value)
            after_nulls = int(working_frame[column].isnull().sum())
            audit_log.append(
                {
                    "column": column,
                    "strategy": "mode",
                    "reason": "Categorical fields use the mode to preserve the dominant category.",
                    "before_nulls": before_nulls,
                    "after_nulls": after_nulls,
                }
            )

    for column in ["status_date", "updated_at"]:
        if column in working_frame.columns and working_frame[column].notna().any():
            before_nulls = int(working_frame[column].isnull().sum())
            working_frame[column] = working_frame[column].ffill()
            after_nulls = int(working_frame[column].isnull().sum())
            audit_log.append(
                {
                    "column": column,
                    "strategy": "forward_fill",
                    "reason": "Time-ordered values use forward fill when the last known value is the safest proxy.",
                    "before_nulls": before_nulls,
                    "after_nulls": after_nulls,
                }
            )

    logging.info("Applied missing-value strategies to %s rows", len(working_frame))
    return working_frame, audit_log


def process_data(frame: pd.DataFrame, friction_threshold: int = DEFAULT_THRESHOLD) -> pd.DataFrame:
    """Clean and enrich payment data for friction analysis.

    Args:
        frame: Raw payment data with payment_id, amount, response_code, and retry_count.
        friction_threshold: Number of retries that indicates payment friction.

    Returns:
        A processed DataFrame with cleaned amounts and friction labels.
    """
    if frame.empty:
        raise ValueError("Input DataFrame cannot be empty")

    working_frame = frame.copy()
    working_frame = working_frame.drop_duplicates()

    working_frame, _ = apply_missing_value_strategies(working_frame)

    if "amount" in working_frame.columns:
        working_frame["amount"] = pd.to_numeric(working_frame["amount"], errors="coerce")

    if "retry_count" in working_frame.columns:
        working_frame["retry_count"] = pd.to_numeric(working_frame["retry_count"], errors="coerce").fillna(0)

    working_frame["friction_flag"] = False
    if "retry_count" in working_frame.columns:
        working_frame.loc[working_frame["retry_count"] >= friction_threshold, "friction_flag"] = True

    working_frame["friction_label"] = working_frame["friction_flag"].map({True: "high-friction", False: "stable"})

    logging.info("Processed %s rows", len(working_frame))
    return working_frame


def output_results(frame: pd.DataFrame, filepath: Union[str, Path]) -> Path:
    """Write processed results to a CSV file.

    Args:
        frame: Processed payment data.
        filepath: Destination path for the CSV output.

    Returns:
        The output path as a Path object.
    """
    output_path = Path(filepath)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    logging.info("Output saved to %s", output_path)
    return output_path


def run_pipeline(input_path: Union[str, Path] = INPUT_FILE, output_path: Union[str, Path] = OUTPUT_FILE) -> Path:
    """Run the full ingest-process-output workflow."""
    raw_data = ingest_data(input_path)
    processed_data = process_data(raw_data)
    return output_results(processed_data, output_path)


if __name__ == "__main__":
    try:
        print("Starting workflow...")
        output_path = run_pipeline()
        print(f"✓ Workflow completed successfully: {output_path}")
    except Exception as exc:  # pragma: no cover - CLI safety
        logging.error("Workflow failed: %s", exc)
        print(f"Error: {exc}")
        raise
