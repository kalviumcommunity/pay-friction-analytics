# PayFrictionIQ KPI Reference Document

### 1. Monthly Active Users (MAU)
*   **Definition:** Distinct customers with at least one transaction attempt in the last 30 days.
*   **Formula:** `COUNT(DISTINCT customer_id) WHERE transaction_date >= TODAY() - 30 days`
*   **Data Source:** `kpi_transactions.csv`
*   **Target Range:** 4 - 10
*   **Owner:** Product Manager

### 2. Revenue Per Customer (RPC)
*   **Definition:** Average successful revenue generated per unique active customer.
*   **Formula:** `SUM(amount WHERE status='success') / COUNT(DISTINCT customer_id)`
*   **Data Source:** `kpi_transactions.csv`
*   **Target Range:** $90 - $150
*   **Owner:** Finance Lead

### 3. Payment Success Rate (PSR)
*   **Definition:** Percentage of all transaction attempts that succeed.
*   **Formula:** `COUNT(status='success') / COUNT(all transactions)`
*   **Data Source:** `kpi_transactions.csv`
*   **Target Range:** 90% - 100% (0.90 - 1.0)
*   **Owner:** Engineering Lead

### 4. Failed Payment Ratio (FPR)
*   **Definition:** Percentage of transaction attempts that fail (inverse of PSR).
*   **Formula:** `COUNT(status='failed') / COUNT(all transactions)`
*   **Data Source:** `kpi_transactions.csv`
*   **Target Range:** 0% - 10% (0.0 - 0.10)
*   **Owner:** Engineering Lead

### 5. Involuntary Churn Rate
*   **Definition:** Percentage of customers active 30-60 days ago who have zero activity in the last 30 days.
*   **Formula:** `[Active(T-60 to T-30) NOT IN Active(T-30 to T-0)] / Active(T-60 to T-30)`
*   **Data Source:** `kpi_transactions.csv`
*   **Target Range:** 0% - 5% (0.0 - 0.05)
*   **Owner:** Customer Success