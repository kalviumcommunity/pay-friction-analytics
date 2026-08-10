-- Revenue by Segment Metric
SELECT 
    c.customer_type,
    strftime('%Y-%m', t.transaction_date) AS month,
    COUNT(DISTINCT t.order_id) AS order_count,
    SUM(t.amount) AS monthly_revenue,
    ROUND(AVG(t.amount), 2) AS avg_order_value,
    COUNT(DISTINCT t.customer_id) AS unique_customers,
    ROUND(SUM(t.amount) / COUNT(DISTINCT t.customer_id), 2) AS revenue_per_customer
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.customer_type, strftime('%Y-%m', t.transaction_date)
ORDER BY month DESC, monthly_revenue DESC;