import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.pipeline import analyze_missing_before, apply_missing_value_strategies, ingest_data, output_results, process_data


class PipelineFunctionsTestCase(unittest.TestCase):
    def test_ingest_data_reads_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "payments.csv"
            pd.DataFrame(
                [
                    {"payment_id": "p1", "amount": 100.0, "response_code": "00"},
                    {"payment_id": "p2", "amount": 50.0, "response_code": "T05"},
                ]
            ).to_csv(file_path, index=False)

            data = ingest_data(file_path)

            self.assertIsInstance(data, pd.DataFrame)
            self.assertEqual(len(data), 2)
            self.assertIn("payment_id", data.columns)

    def test_process_data_creates_expected_columns_and_fills_missing_values(self):
        data = pd.DataFrame(
            [
                {"payment_id": "p1", "amount": 100.0, "response_code": "00", "retry_count": 0},
                {"payment_id": "p2", "amount": None, "response_code": "T05", "retry_count": 2},
                {"payment_id": "p2", "amount": 50.0, "response_code": "T05", "retry_count": 2},
            ]
        )

        processed = process_data(data)

        self.assertIn("friction_flag", processed.columns)
        self.assertIn("friction_label", processed.columns)
        self.assertFalse(processed[processed["payment_id"] == "p2"]["amount"].isna().any())
        self.assertTrue(processed.loc[processed["payment_id"] == "p2", "friction_flag"].all())

    def test_output_results_writes_csv_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.csv"
            frame = pd.DataFrame([{"payment_id": "p1", "friction_flag": True}])

            result_path = output_results(frame, output_path)

            self.assertTrue(result_path.exists())
            self.assertTrue(result_path.name.endswith(".csv"))
            written = pd.read_csv(result_path)
            self.assertEqual(len(written), 1)

    def test_null_strategies_are_documented_and_applied(self):
        frame = pd.DataFrame(
            [
                {"payment_id": "p1", "amount": 100.0, "segment": "B2B", "status_date": "2024-01-01"},
                {"payment_id": None, "amount": None, "segment": None, "status_date": None},
                {"payment_id": "p3", "amount": 50.0, "segment": "B2C", "status_date": "2024-01-02"},
            ]
        )

        before_report = analyze_missing_before(frame)
        processed, audit_log = apply_missing_value_strategies(frame)

        self.assertGreater(len(before_report), 0)
        self.assertEqual(processed["payment_id"].isna().sum(), 0)
        self.assertFalse(processed["amount"].isna().any())
        self.assertFalse(processed["segment"].isna().any())
        self.assertTrue(any(entry["strategy"] == "drop_rows" for entry in audit_log))
        self.assertTrue(any(entry["strategy"] == "median" for entry in audit_log))
        self.assertTrue(any(entry["strategy"] == "mode" for entry in audit_log))


if __name__ == "__main__":
    unittest.main()
