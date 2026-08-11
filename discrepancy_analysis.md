# Metric Discrepancy Investigation & Root Cause Analysis

## Overview
This document presents the computational drift audit and cross-validation analysis between SQL and Python calculation layers for key business metrics (Active Users, AOV, Customer Churn).

---

## 1. Task 1 & Task 2: Metric Comparison & Discrepancy Report

| Metric Name | SQL Result | Python Result | Absolute Difference | Percent Difference | Tolerance | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Active Users (30-day)** | `4` | `4` | `0` | `0.00%` | `0.0%` | **PASS** |
| **Average Order Value (AOV)** | `$160.00` | `$160.00` | `$0.00` | `0.00%` | `0.1%` | **PASS** |
| **Customer Churn (Monthly - Flawed SQL)** | `2` | `1` | `1` | `50.00%` | `0.0%` | **FAIL** |
| **Customer Churn (Refactored SQL)** | `1` | `1` | `0` | `0.00%` | `0.0%` | **PASS** |

---

## 2. Task 3: Automated Validation Script Architecture
The automated validation script ([validation_script.py](file:///c:/Users/iamsh/Music/teamrrs/validation_script.py)) programmatically executes metric calculations across both SQL (via SQLAlchemy database engine) and Python (via pandas DataFrame operations).

- **Tolerance Configuration:**
  - Discrete counts (Active Users, Churn): `0.0%` tolerance.
  - Floating-point calculations (AOV): `0.1%` tolerance.
- **Output Artifact:** Generates `validation_report.csv` daily with timestamps, diff metrics, and pass/fail indicators.

---

## 3. Task 4: Churn Metric Root Cause Analysis & Investigation

### Observed Discrepancy
- **SQL Calculation (Flawed):** `2` Churned Customers
- **Python Calculation:** `1` Churned Customer
- **Divergence:** `50.00%` percentage difference (`FAIL`).

### Investigation Steps:
1. **Manual Trace & Hand Calculation:**
   - Examined the raw order logs:
     - Customer #1: Ordered today ($150, Month N) -> Active.
     - Customer #2: Ordered in Month N-1 ($50, July 2026) and had $0 orders in Month N -> **True Churned Customer**.
     - Customer #3: Ordered today ($200, Month N) -> Active.
     - Customer #4: Ordered in Month N-1 of Previous Year ($300, July 2025) -> Inactive for >12 months.
     - Customer #5: Ordered today ($100, Month N) -> Active.
   - **Hand-Computed Truth:** Exactly **1** customer (#2) churned between Month N-1 and Month N.
2. **Layer Evaluation:**
   - Python evaluated 1 customer correctly by applying explicit calendar month boundaries.
   - SQL evaluated 2 customers (incorrectly including Customer #4).
3. **Query Inspection:**
   - Analyzed the initial SQL `LEFT JOIN` logic:
     ```sql
     WHERE strftime('%m', order_date) = strftime('%m', 'now', '-1 month')
     ```

### Root Cause Identification:
The initial SQL query used `strftime('%m')` (or `MONTH()`), which extracts **only the numerical month index** (e.g., `"07"` for July) while completely discarding the **Year** context. Customer #4 ordered in July of the previous year. Because the month index matched `"07"`, the SQL query misclassified Customer #4 as active in month N-1, artificially inflating the churn count.

### Fix Applied & Refactored SQL:
Refactored the SQL query to use explicit chronological calendar date boundaries instead of month index strings:
```sql
SELECT COUNT(DISTINCT c1.customer_id) as churned_customers
FROM (
    SELECT DISTINCT customer_id FROM orders
    WHERE order_date >= date('now', 'start of month', '-1 month')
      AND order_date < date('now', 'start of month')
      AND order_amount > 0
) c1
LEFT JOIN (
    SELECT DISTINCT customer_id FROM orders
    WHERE order_date >= date('now', 'start of month')
) c2 ON c1.customer_id = c2.customer_id
WHERE c2.customer_id IS NULL;
```

### Post-Fix Validation:
After applying the refactored SQL query, both SQL and Python returned **1** churned customer (`0.00%` difference).

---

## 4. Task 5: Why Manual Review is Necessary & Risks of Auto-Fixing

### Follow-Up Question:
*You have a validation script that runs daily and catches metrics drift automatically. However, it flags a discrepancy but does not auto-fix it - someone must investigate. Why is manual investigation necessary? What would be the risk of auto-fixing based on a tolerance threshold alone?*

### In-Depth Response:

1. **Tolerance Thresholds Catch Divergence, Not Mathematical Correctness:**
   - A validation script only measures *whether* two numbers differ; it cannot determine *which* number is correct.
   - If an automated routine defaults to overwriting Python with SQL (or vice versa), it risks overwriting a mathematically sound Python model with a buggy SQL query (like the `strftime('%m')` year-stripping bug discovered above).

2. **The Danger of Silent Creeping Drift:**
   - Minor discrepancies below a tolerance threshold (e.g., 0.05% difference due to timezone offsets or NULL handling) can compound over time into massive financial errors.
   - Relying solely on automated pass/fail thresholds without investigating underlying causes allows "creeping drift" to infect production reports unnoticed.

3. **Architectural Resolution vs. Superficial Patching:**
   - Auto-fixing only masks the symptom for a single execution run.
   - Manual investigation is essential to diagnose **why** the logic drifted (e.g., missing year boundary filters, differing `NULL` vs `NaN` handling, string casing differences). Resolving the root cause in version control prevents the exact same logic error from silently corrupting other downstream dashboards and ML features.