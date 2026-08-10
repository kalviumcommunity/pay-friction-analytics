-- Task 3: Filter GROUPS after aggregation using HAVING
SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(amount) as annual_revenue
FROM transactions
WHERE transaction_date >= '2024-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 1000                      -- HAVING filters aggregated groups
  AND COUNT(*) >= 1
ORDER BY annual_revenue DESC;