-- Task 4: Combine WHERE (row-level) and HAVING (group-level) in one query
SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as segment_customers,
    SUM(t.amount) as segment_revenue,
    ROUND(AVG(t.amount), 2) as avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'      -- WHERE: data quality & date bounds
  AND t.amount > 0                                 -- WHERE: logical validity
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 1       -- HAVING: segment size threshold
  AND SUM(t.amount) > 100                          -- HAVING: business revenue threshold
ORDER BY segment_revenue DESC;