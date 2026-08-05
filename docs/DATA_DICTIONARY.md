# PayFrictionIQ — Data Dictionary

## Dataset Overview
This dataset contains customer transaction records, payment retry logs, and bank response codes. It is used to separate temporary payment friction from permanently lost revenue.
* **Last Updated:** 2026-08-05
* **Maintained By:** Data Engineering Team

---

## Columns (Business Context)

### customer_id
* **Type:** Integer
* **Business Meaning:** Unique customer identifier from the CRM system.
* **Example:** `12456`
* **Null Handling:** Never null (primary key).
* **Related KPI:** Customer tracking, lifetime value.

### trnx_amt  
* **Type:** Float
* **Business Meaning:** Intended revenue from a single transaction.
* **Example:** `150.99`
* **Null Handling:** Very rare - investigate if found.
* **Related KPI:** Monthly revenue, average transaction value.

### cust_segment
* **Type:** String
* **Business Meaning:** Customer market segment (B2B, B2C, SMB). Determines risk and pricing strategy.
* **Example:** `B2B`
* **Null Handling:** If null, classify as `UNKNOWN`.
* **Related KPI:** Segment revenue, segment churn rate.

### flag_churn
* **Type:** Integer
* **Business Meaning:** Indicator of whether the customer abandoned the platform entirely following a transaction failure.
* **Example:** `1`
* **Related KPI:** True Churn Rate vs. Payment Friction.

### retry_count
* **Type:** Integer
* **Business Meaning:** Number of times a payment was re-attempted before success or final failure.
* **Example:** `3`
* **Related KPI:** Payment friction rate, recovery success.

---

## Column to KPI Mapping

### 1. Monthly Revenue
* **Formula:** `SUM(trnx_amt)` where payment is successful
* **Related Columns:** `trnx_amt`, `purchase_date`
* **Why It Matters:** Tracks total realized company revenue vs intended revenue.

### 2. Segment Profitability
* **Formula:** `SUM(trnx_amt)` grouped by `cust_segment`
* **Related Columns:** `trnx_amt`, `cust_segment`
* **Why It Matters:** Identifies the most profitable market segments to focus recovery efforts on.

### 3. Payment Friction Rate
* **Formula:** `AVG(retry_count)` per successful transaction
* **Related Columns:** `retry_count`, `purchase_date`
* **Why It Matters:** Measures how hard it is for customers to give us money. High friction leads to eventual churn.

### 4. True Churn Rate
* **Formula:** `SUM(flag_churn) / COUNT(customer_id)`
* **Related Columns:** `flag_churn`, `customer_id`
* **Why It Matters:** Critical retention metric.

### 5. Revenue Lost to Friction
* **Formula:** `SUM(trnx_amt)` where `retry_count > 0` and `flag_churn = 1`
* **Related Columns:** `trnx_amt`, `retry_count`, `flag_churn`
* **Why It Matters:** The core business problem: money left on the table strictly due to technical payment failures.

---

## Ambiguous Columns & Resolutions

### Column: `flag_churn`
* **Original Ambiguity:** Does it mean the user canceled their subscription voluntarily, or did their card fail and they were locked out?
* **Resolved Meaning:** Binary indicator of involuntary churn (locked out due to payment failure after 3+ retries).
* **Proposed Rename:** `involuntary_churn_flag`
* **Risk If Misunderstood:** Marketing might send "We miss you!" emails to users who are actively angry that the platform won't accept their valid credit card.

### Column: `cust_segment`
* **Original Ambiguity:** Is this market size (SMB/Enterprise) or product tier (Basic/Premium)?
* **Resolved Meaning:** Customer market size segment.
* **Proposed Rename:** `market_segment`
* **Risk If Misunderstood:** Revenue analysis by the wrong dimension produces misleading performance reports.

---

## Column Relationships

### Churn vs. Payment Friction
* **Definition:** `SUM(flag_churn)` grouped by `retry_count` buckets.
* **How It Matters:** Proves the hypothesis that higher payment friction (more retries) directly correlates with higher permanent churn.
* **Related Columns:** `flag_churn`, `retry_count`

### Revenue at Risk by Segment
* **Definition:** `SUM(trnx_amt)` for failed payments grouped by `cust_segment`.
* **How It Matters:** Highlights which segments experience the most payment failures, allowing targeted engineering fixes (e.g., alternative payment methods for B2B).
* **Related Columns:** `trnx_amt`, `cust_segment`, `bank_response_code`