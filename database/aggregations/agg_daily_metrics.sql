-- Table: agg_daily_metrics
-- Purpose: Pre-computed daily summary to power fast dashboard load times
-- Grain: Daily 
-- Subject: Revenue and Transaction counts
-- Refresh Strategy: Truncate and Reload (Nightly)

CREATE TABLE IF NOT EXISTS agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    row_count INTEGER,
    updated_at TIMESTAMP
);

-- Note: The INSERT statement will be executed dynamically via Python.