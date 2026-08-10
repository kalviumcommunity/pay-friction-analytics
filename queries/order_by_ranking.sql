-- Task 5: Surface top performers using ORDER BY and window ranking functions
SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as customers,
    SUM(t.amount) as total_revenue,
    ROUND(AVG(t.amount), 2) as avg_order,
    RANK() OVER (ORDER BY SUM(t.amount) DESC) as revenue_rank
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 1
ORDER BY total_revenue DESC
LIMIT 20;