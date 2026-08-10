-- Task 1: Filter data quality issues BEFORE grouping
SELECT 
    customer_id,
    SUM(amount) as annual_revenue,
    COUNT(*) as transaction_count
FROM transactions
WHERE transaction_date >= '2024-01-01'  -- Date range filter
  AND amount > 0                              -- Remove refunds/invalid values
GROUP BY customer_id
ORDER BY annual_revenue DESC;