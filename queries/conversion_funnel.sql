-- Funnel Conversion Metric
SELECT 
    date(u.created_at) AS signup_date,
    COUNT(*) AS signups,
    COUNT(CASE WHEN u.email_verified_at IS NOT NULL THEN 1 END) AS email_verified,
    COUNT(CASE WHEN u.first_purchase_at IS NOT NULL THEN 1 END) AS first_purchase,
    ROUND(100.0 * COUNT(CASE WHEN u.first_purchase_at IS NOT NULL THEN 1 END) / COUNT(*), 1) AS conversion_pct
FROM users u
GROUP BY date(u.created_at)
ORDER BY signup_date DESC;