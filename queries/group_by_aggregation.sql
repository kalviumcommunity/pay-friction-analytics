-- Task 2: Group by multiple dimensions with multiple aggregate functions
SELECT 
    c.customer_type,
    strftime('%Y-%m', t.transaction_date) as month,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    COUNT(*) as transaction_count,
    SUM(t.amount) as monthly_revenue,
    AVG(t.amount) as avg_transaction
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'  -- WHERE filters rows first
GROUP BY c.customer_type, strftime('%Y-%m', t.transaction_date)
ORDER BY month DESC;