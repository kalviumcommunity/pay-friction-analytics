# scripts/alert_config.py

ALERT_THRESHOLDS = {
    "churn_rate": {
        "metric": "Customer Churn Rate (%)",
        "threshold": 7.0,
        "direction": "above",
        "severity": "critical",
        "message": "Churn rate exceeds safe operating limits. Investigate retention pipeline immediately."
    },
    "avg_order_value": {
        "metric": "Average Order Value ($)",
        "threshold": 300.0,
        "direction": "below",
        "severity": "warning",
        "message": "AOV has dropped below target profitability threshold. Check pricing and discounting."
    },
    "null_percentage": {
        "metric": "Data Quality (Null %)",
        "threshold": 2.0,
        "direction": "above",
        "severity": "warning",
        "message": "Missing data exceeds acceptable limits. Verify data ingestion pipelines."
    }
}