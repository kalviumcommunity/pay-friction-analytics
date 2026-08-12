# KPI Data Sources & Lineage Documentation
**Assignment 2.47 – Task 5**

All KPI values displayed on the dashboard are computed dynamically from the
validated transaction data layer. No values are hardcoded. Every metric uses
date-relative windows so the dashboard refreshes automatically when new data
is loaded.

---

## KPI 1 – Revenue

| Field | Detail |
|---|---|
| **Business Question** | Is this month's successful payment volume growing? |
| **Data Source** | `data/raw/kpi_transactions.csv` → `transaction_date`, `amount`, `status` |
| **Equivalent SQL View** | `database/views/vw_daily_revenue.sql` |
| **Query Logic** | `SUM(amount) WHERE status = 'success' AND MONTH(transaction_date) = current_month` |
| **Prior Period** | Same query with `MONTH = current_month - 1` |
| **Comparison** | `((current - prior) / prior) * 100` |
| **Direction** | ↑ is good (green) |
| **Cross-Validation** | Python pandas `.sum()` matches SQL aggregation output |

---

## KPI 2 – Active Users (MAU)

| Field | Detail |
|---|---|
| **Business Question** | How many unique customers transacted this month? |
| **Data Source** | `data/raw/kpi_transactions.csv` → `transaction_date`, `customer_id` |
| **Equivalent SQL View** | `database/views/vw_active_customers.sql` |
| **Query Logic** | `COUNT(DISTINCT customer_id) WHERE MONTH(transaction_date) = current_month` |
| **Prior Period** | Same with `MONTH = current_month - 1` |
| **Comparison** | `((current - prior) / prior) * 100` |
| **Direction** | ↑ is good (green) |
| **Cross-Validation** | `kpis/kpi_functions.py::calculate_mau()` |

---

## KPI 3 – Average Order Value (AOV)

| Field | Detail |
|---|---|
| **Business Question** | Is the average transaction size growing or shrinking? |
| **Data Source** | `data/raw/kpi_transactions.csv` → `transaction_date`, `amount`, `status` |
| **Equivalent SQL View** | `database/aggregations/agg_daily_metrics.sql` |
| **Query Logic** | `AVG(amount) WHERE status = 'success' AND MONTH(transaction_date) = current_month` |
| **Prior Period** | Same with `MONTH = current_month - 1` |
| **Comparison** | `((current - prior) / prior) * 100` |
| **Direction** | ↑ is good (green) |
| **Cross-Validation** | `kpis/kpi_functions.py::calculate_rpc()` (related metric) |

---

## KPI 4 – Churn Rate ⚠️ Inverted Metric

| Field | Detail |
|---|---|
| **Business Question** | What % of last month's customers did not return this month? |
| **Data Source** | `data/raw/kpi_transactions.csv` → `transaction_date`, `customer_id` |
| **Equivalent SQL View** | `database/views/vw_active_customers.sql` (set difference) |
| **Query Logic** | `(customers active in prior month NOT IN current month) / prior_month_customers * 100` |
| **Prior Period** | Same logic shifted back one additional month |
| **Comparison** | `((current_churn - prior_churn) / prior_churn) * 100` |
| **Direction** | ↓ is good (green) — `delta_color='inverse'` in Streamlit |
| **Validation Target** | 0 – 5% per `kpis/kpi_validation_targets.json` |
| **Cross-Validation** | `kpis/kpi_functions.py::calculate_churn_rate()` |

> [!WARNING]
> Churn uses **inverted colour logic**. A negative delta must render **green**.
> Streamlit: `st.metric(delta_color='inverse')`.
> Custom indicator: `get_trend_indicator(change_pct, inverted=True)`.

---

## KPI 5 – Customer Satisfaction

| Field | Detail |
|---|---|
| **Business Question** | Is the average customer satisfaction rating stable or improving? |
| **Data Source** | `data/raw/kpi_transactions.csv` → `transaction_date`, `satisfaction` |
| **Equivalent SQL View** | Would map to a `vw_satisfaction_monthly` view |
| **Query Logic** | `AVG(satisfaction) WHERE MONTH(transaction_date) = current_month` |
| **Prior Period** | Same with `MONTH = current_month - 1` |
| **Comparison** | `((current - prior) / prior) * 100` |
| **Direction** | ↑ is good (green); flat (< ±2%) = yellow |
| **Cross-Validation** | Python `.mean()` on satisfaction column |

---

## Automatic Refresh Design (Bonus)

> [!TIP]
> **Question:** When a new dataset is uploaded, how do KPI values update without code changes?

The dashboard is designed for zero-touch refresh:

1. **Date-relative windows** — all queries use `current_month` / `current_month - 1` computed at runtime, never hardcoded date strings.
2. **`@st.cache_data` with TTL** — adding `@st.cache_data(ttl=3600)` causes Streamlit to re-read the source file every hour automatically.
3. **View-based queries** — in production, replace the CSV load with a query against validated SQL views (`vw_daily_revenue`, `vw_active_customers`). When the view's underlying table gets new rows, the KPI card automatically reflects them on next load.
4. **Scheduled pipeline** — a daily cron job (or Airflow DAG) appends new transactions to `kpi_transactions.csv`; Streamlit re-reads it on the next request.
5. **No hardcoded values** — every number in the dashboard is the output of a Python/SQL computation, not a string literal.

---

## Validation Targets Reference

Sourced from `kpis/kpi_validation_targets.json`:

| KPI | Min | Max | Unit |
|---|---|---|---|
| MAU | 4 | 10 | customers |
| Revenue per Customer | $90 | $150 | dollars |
| Payment Success Rate | 90% | 100% | percent |
| Failed Payment Ratio | 0% | 10% | percent |
| Involuntary Churn Rate | 0% | 5% | percent |
