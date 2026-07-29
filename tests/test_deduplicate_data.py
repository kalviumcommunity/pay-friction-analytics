import unittest
from pathlib import Path

import pandas as pd

from scripts.deduplicate_data import (
    compare_before_after,
    detect_exact_duplicates,
    log_removed_duplicates,
    remove_exact_duplicates,
    remove_near_duplicates,
)


class DeduplicateDataTestCase(unittest.TestCase):
    def test_detect_exact_duplicates_identifies_duplicate_rows(self):
        df = pd.DataFrame(
            [
                {"customer_id": 1, "transaction_date": "2025-01-01", "amount": 100, "status": "completed"},
                {"customer_id": 1, "transaction_date": "2025-01-01", "amount": 100, "status": "completed"},
                {"customer_id": 2, "transaction_date": "2025-01-02", "amount": 50, "status": "pending"},
            ]
        )

        exact_count, dup_rows = detect_exact_duplicates(df)

        self.assertEqual(exact_count, 1)
        self.assertEqual(len(dup_rows), 2)
        self.assertEqual(dup_rows.iloc[0]["customer_id"], 1)

    def test_remove_near_duplicates_keeps_most_complete_record(self):
        df = pd.DataFrame(
            [
                {"customer_id": 1, "transaction_date": "2025-01-01", "amount": None, "status": "pending"},
                {"customer_id": 1, "transaction_date": "2025-01-01", "amount": 250, "status": "completed"},
                {"customer_id": 2, "transaction_date": "2025-01-02", "amount": 80, "status": "completed"},
            ]
        )

        deduped = remove_near_duplicates(df, key_columns=["customer_id", "transaction_date"], keep_strategy="most_complete")

        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped.loc[deduped["customer_id"] == 1, "amount"].iloc[0], 250)

    def test_log_removed_duplicates_and_compare_before_after_create_outputs(self):
        df_original = pd.DataFrame(
            [
                {"customer_id": 1, "transaction_date": "2025-01-01", "amount": 100, "status": "completed"},
                {"customer_id": 1, "transaction_date": "2025-01-01", "amount": 100, "status": "completed"},
                {"customer_id": 2, "transaction_date": "2025-01-02", "amount": 50, "status": "pending"},
            ]
        )
        df_dedup = remove_exact_duplicates(df_original, keep="first")

        removed, audit_summary = log_removed_duplicates(df_original, df_dedup)
        comparison = compare_before_after(df_original, df_dedup)

        self.assertEqual(len(removed), 1)
        self.assertEqual(audit_summary["total_removed"], 1)
        self.assertEqual(comparison["rows_removed"], 1)
        self.assertTrue(Path("output/removed_duplicates_audit.csv").exists())
        self.assertTrue(Path("output/dedup_audit_summary.json").exists())
        self.assertTrue(Path("output/dedup_summary.json").exists())


if __name__ == "__main__":
    unittest.main()
