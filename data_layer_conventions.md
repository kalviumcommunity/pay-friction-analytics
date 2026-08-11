# Clean Data Layer Naming Conventions

## Overview
This document defines the architecture and naming conventions for the SQL data layer. Establishing a clean data layer prevents metric drift across dashboards (Sales, Customer Success, Operations) by defining business logic once and serving pre-aggregated data efficiently.

---

## 1. Views Architecture & Naming Conventions
- **Prefix:** `vw_`
- **Pattern:** `vw_[business_entity]_[metric]`
- **Description:** Saved queries that encapsulate metric calculations (read-only logical abstraction).
- **Rules:**
  - Views must never perform destructive actions (`INSERT`, `UPDATE`, `DROP`).
  - Views act as the single source of truth for metrics across reporting engines.
  - Keep views focused on a single business concept (e.g., 5–8 columns max).
- **Examples & Applied Objects:**
  - `vw_active_customers`: Identifies rolling 30-day customer activity, revenue, and churn risk indicators.
  - `vw_product_performance`: Aggregates lifetime transaction count and sales revenue per product.

---

## 2. Pre-Aggregated Tables & Naming Conventions
- **Prefix:** `agg_`
- **Pattern:** `agg_[grain]_[subject]`
- **Description:** Physical tables containing pre-computed metric aggregates for high-frequency or heavy dashboard queries.
- **Rules:**
  - Use `agg_` tables for analytical queries scanning large datasets to prevent dashboard latency.
  - Document the refresh frequency (daily, hourly, batch).
- **Examples & Applied Objects:**
  - `agg_daily_metrics`: Pre-computed daily revenue and transaction counts aggregated by transaction date.

---

## 3. Mandatory Columns in Aggregated Tables
Every `agg_` table **must** include the following standard columns:
1. **Timestamp tracking:** `updated_at` (or `created_at`) - Timestamp indicating when the aggregate snapshot was generated. Dashboards check this field to alert users of stale data (>24h old).
2. **Audit & Validation count:** `row_count` - Number of raw underlying records collapsed into the aggregated row.
3. **Time / Grain identifier:** `aggregation_date` (or `date_day`, `hour`) - Defines the temporal resolution of the record.

---

## 4. Key Benefits of a Clean Data Layer
- **No Metric Drift:** Revenue and customer metrics are calculated identically across all dashboards.
- **High Performance:** Dashboards query pre-aggregated tables in milliseconds rather than re-scanning raw tables.
- **Maintainability:** Updating a business definition requires changing SQL in a single `.sql` file in version control.
- **Self-Documenting Code:** Object prefixes (`vw_` and `agg_`) instantly communicate the data layer role to engineers and analysts.

---

## 5. Python Integration Standards
When querying the data layer from Python analytics tools (e.g., pandas, Streamlit):
- Always query `vw_` views or `agg_` tables—never query raw underlying transactional tables directly for dashboard metrics.
- Include comments in python code explaining the business purpose of each queried data layer object.