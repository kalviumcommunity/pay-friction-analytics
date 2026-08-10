-- Monthly Active Users with Segment Breakdown (SQLite compatible)
SELECT 
    strftime('%Y-%m', t.transaction_date) AS month,
    COUNT(DISTINCT t.customer_id) AS active_users,
    COUNT(DISTINCT CASE WHEN c.customer_type = 'Enterprise' THEN t.customer_id END) AS enterprise_users,
    COUNT(DISTINCT CASE WHEN c.customer_type = 'SMB' THEN t.customer_id END) AS smb_users
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY strftime('%Y-%m', t.transaction_date)
ORDER BY month DESC;