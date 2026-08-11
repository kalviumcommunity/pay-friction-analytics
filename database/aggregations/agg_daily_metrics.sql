-- Table: agg_daily_metrics
-- Purpose: Pre-computed daily summary to power fast dashboard load times
-- Grain: Daily 
-- Subject: Revenue and Transaction counts
-- Refresh Strategy: Truncate and Reload (Nightly)
--
-- Columns:
--   aggregation_date: Date of the metrics summary
--   metric_name: Identifier of the business metric (e.g., total_revenue)
--   metric_value: Pre-computed metric numerical value
--   row_count: Number of raw transaction rows aggregated
--   updated_at: Timestamp when aggregation was computed

CREATE TABLE IF NOT EXISTS agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    row_count INTEGER,
    updated_at TIMESTAMP
);

-- Population Query:
-- INSERT INTO agg_daily_metrics
-- SELECT 
--     date(transaction_date) as aggregation_date,
--     'total_revenue' as metric_name,
--     SUM(amount) as metric_value,
--     COUNT(*) as row_count,
--     CURRENT_TIMESTAMP as updated_at
-- FROM transactions
-- GROUP BY date(transaction_date);