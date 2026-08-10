# Clean Data Layer Naming Conventions

## Views
- **Prefix:** `vw_`
- **Pattern:** `vw_[business_entity]_[metric]`
- **Examples:**
  - `vw_active_customers` - Customers with recent activity.
  - `vw_product_performance` - Lifetime sales and metrics per product.
- **Rule:** Views must never contain destructive actions (INSERT/UPDATE). They are read-only logical layers ensuring all dashboards use the exact same calculation formula.

## Pre-Aggregated Tables
- **Prefix:** `agg_`
- **Pattern:** `agg_[grain]_[subject]`
- **Examples:**
  - `agg_daily_metrics` - Daily revenue aggregates.
- **Rule:** Dashboards querying over 1 million rows must hit an `agg_` table, not a `vw_` view, to prevent database timeouts.

## Columns in Aggregated Tables
- **Always include:** `updated_at` (Timestamp of when the aggregation was last computed). If this is older than 24 hours, the dashboard must throw a "Stale Data" warning.
- **Always include:** `row_count` (Count of raw rows collapsed into the aggregation, useful for auditing).
- **Always include:** Date/time grain column (`aggregation_date`).