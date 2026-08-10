-- View: vw_product_performance
-- Purpose: Analyze top-performing products by category and revenue
-- Business metric: Product-level lifetime revenue and transaction volume
-- Used by: Product Managers, Operations dashboards
-- 
-- Columns:
--   product_id: Unique product identifier
--   product_name: Product display name
--   category: Product grouping (Software, Hardware, Service)
--   total_units_sold: Lifetime transaction count
--   lifetime_revenue: Total gross revenue

CREATE VIEW IF NOT EXISTS vw_product_performance AS
SELECT 
    p.id AS product_id,
    p.product_name,
    p.category,
    COUNT(t.transaction_id) AS total_units_sold,
    SUM(t.amount) AS lifetime_revenue
FROM products p
LEFT JOIN transactions t ON p.id = t.product_id
GROUP BY p.id, p.product_name, p.category;