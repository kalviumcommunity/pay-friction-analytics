# Metric Discrepancy Investigation & Root Cause Analysis

## Churn Metric Discrepancy Analysis

**Observed Difference:** 
- SQL Computation = 2 Churned Customers
- Python Computation = 1 Churned Customer
- Difference = 100.0% divergence.

**Investigation Steps:**
1. **Manual Trace:** I hand-computed the raw `orders` dataset. Only Customer #2 ordered between 30 and 60 days ago and failed to order in the last 30 days. The true churn number is exactly 1.
2. **Layer Evaluation:** The Python script accurately returned 1. The SQL query returned 2. 
3. **Query Inspection:** I analyzed the SQL `LEFT JOIN` condition: `strftime('%m', order_date) = strftime('%m', 'now', '-1 month')`. 

**Root Cause:**
The SQL query uses a formatting string that extracts *only the numerical month* (e.g., "07" for July) while completely stripping the Year context. Customer #4 made an order exactly 1 year and 1 month ago (July 2025). The SQL query incorrectly identified them as active "last month" (July 2026), artificially inflating the churn count when they didn't return this month. 

**Fix Applied (Documented):**
The SQL query must be refactored to use explicit chronological date boundaries (e.g., `order_date >= date('now', '-60 days') AND order_date < date('now', '-30 days')`) instead of string-matching month numbers. 

---

## Follow-Up Question: Why Manual Investigation is Necessary

**Question:** Your automated script flags a discrepancy but does not auto-fix it. Why is manual investigation necessary? What is the risk of auto-fixing based on a tolerance threshold?

**Answer:**
Auto-fixing metrics is incredibly dangerous because a script cannot determine *which* system is correct—it only knows they differ. If the script automatically overwrites Python's output with SQL's output, it might be overwriting the correct mathematical answer with a flawed, buggy SQL calculation. 

Furthermore, tolerance thresholds only catch immediate divergence. Manual review ensures we fix the underlying logical architecture (like the Year boundary bug) rather than just applying a superficial band-aid. Root cause understanding is required to prevent the exact same "computation drift" from silently corrupting a different dashboard next week.