-- View: vw_active_customers
-- Purpose: Identify customers with recent activity (last 30 days)
-- Business metric: Customers active in rolling 30-day window
-- Used by: Customer engagement dashboard, retention analysis
-- 
-- Columns:
--   customer_id: Unique customer identifier
--   customer_name: Customer display name
--   segment: Customer segment classification
--   order_count_30d: Number of orders in last 30 days
--   revenue_30d: Total revenue from last 30 days
--   last_order_date: Most recent order date
--   days_since_order: Days elapsed since last order

CREATE VIEW IF NOT EXISTS vw_active_customers AS
SELECT 
    c.id AS customer_id,
    c.customer_name,
    c.customer_segment AS segment,
    COUNT(DISTINCT t.transaction_id) AS order_count_30d,
    SUM(t.amount) AS revenue_30d,
    MAX(t.transaction_date) AS last_order_date,
    CAST(JULIANDAY('2023-12-31') - JULIANDAY(MAX(t.transaction_date)) AS INTEGER) AS days_since_order
FROM customers c
LEFT JOIN transactions t ON c.id = t.customer_id
    AND t.transaction_date >= date('2023-12-31', '-30 days')
GROUP BY c.id, c.customer_name, c.customer_segment;