# Data Layer Architecture Lesson

Hey Data Layer Architect!

Welcome. You have optimized queries. Now comes the next challenge: making those optimized queries reusable. Right now every dashboard, every notebook, every script re-computes metrics independently. Revenue is calculated three different ways on three different dashboards. Customer activity means one thing in SQL and another in Python. This lesson teaches you to build a clean data layer - SQL views that define metrics once and pre-aggregated tables that serve dashboards efficiently.

Every data team that scaled beyond two people discovered the same problem: metrics computed in multiple places diverge silently. Revenue on Dashboard A does not match Dashboard B. Nobody knows which is right. Trust erodes. Meetings derail into arguments about numbers instead of decisions about strategy. The root cause: no single source of truth. This lesson fixes that by teaching you to build SQL views and aggregation tables that define every metric exactly once.

## The Real Scenario

### The Problem

A company has three dashboards: one for sales, one for customer success, one for operations. Each dashboard computes "monthly revenue" independently. Sales calculates gross revenue including refunds. Customer success calculates net revenue after refunds. Operations calculates revenue only for shipped orders. The CEO asks "what was our revenue last month?" and receives three different numbers. Nobody can answer confidently. The real problem is not the math - it is that revenue was never defined in one place.

### The Solution

Build SQL views that define each metric once. A view named `vw_monthly_revenue` encapsulates the official revenue calculation. Every dashboard queries the view instead of writing its own calculation. When the definition changes (e.g., "revenue now excludes refunds"), you update one view and every dashboard automatically uses the new definition. Pre-aggregated tables store expensive computations so dashboards load instantly.

## What SQL Views Are and Why They Matter

### A Named Query That Becomes Your Single Source of Truth

#### What is a SQL view

A SQL view is a saved query that behaves like a table. You define the query once with `CREATE VIEW` and then `SELECT` from it like any table. The database executes the underlying query every time you query the view. Views do not store data - they store logic. This means the view always returns fresh results based on current data. Think of a view as a function in programming: you define it once and call it everywhere.

#### Why views prevent metric drift

Without views, every dashboard writes its own revenue query. Over time, queries diverge. One analyst adds a filter for refunds, another does not. With a view, the revenue calculation exists in exactly one place. If the business decides to exclude refunds from revenue, you update the view definition. Every dashboard, notebook, and report that queries the view automatically gets the updated logic. Zero duplication. Zero drift.

#### Creating a view - syntax

```sql
CREATE VIEW vw_active_customers AS
SELECT 
  c.customer_id,
  c.customer_name,
  c.segment,
  COUNT(DISTINCT o.order_id) AS order_count_30d,
  SUM(o.order_amount) AS revenue_30d,
  MAX(o.order_date) AS last_order_date,
  DATEDIFF(CURRENT_DATE, MAX(o.order_date)) AS days_since_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
  AND o.order_date >= CURRENT_DATE - INTERVAL 30 DAY
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.customer_name, c.segment;
```

Now any dashboard queries `SELECT * FROM vw_active_customers` instead of re-implementing this logic. One definition serves the entire team.

**You just learned** what SQL views are and how they prevent metric drift across dashboards. Now you will learn how to design views with clear naming conventions that your entire team can follow.

## View Naming Conventions and Design Patterns

### Naming Is Not Cosmetic - It Is How Teams Navigate Data

#### Prefix pattern: `vw_` for views

Prefix every view with `vw_`. This tells anyone reading the SQL that the object is a view, not a raw table. Pattern: `vw_entity_metric`
Examples: `vw_active_customers`, `vw_monthly_revenue`, `vw_product_performance`. When a new team member sees `vw_`, they immediately know: this is a defined metric layer, not raw data.

#### Design pattern: one view per business concept

Do not pack every metric into one massive view. Create focused views: one for active customers, one for monthly revenue, one for product performance. Each view answers one family of business questions. Dashboards compose by querying multiple views. This keeps views maintainable - when the revenue definition changes, you only touch `vw_monthly_revenue`, not a monolithic view containing everything.

##### Anti-pattern

One view called `vw_everything` that joins 10 tables and returns 50 columns. Slow. Hard to maintain. Nobody knows which columns matter. Changes break multiple dashboards.

##### Correct pattern

Focused views: `vw_active_customers` (7 columns), `vw_monthly_revenue` (5 columns), `vw_product_performance` (6 columns). Each is fast, focused, and independently maintainable.

**You just learned** naming conventions and design patterns for SQL views. Now you will learn when views are not enough and you need pre-aggregated tables for dashboard performance.

## Pre-Aggregated Tables for Dashboard Performance

### When Views Are Too Slow, Pre-Compute the Answer

#### The performance limitation of views

Views re-execute their underlying query every time you `SELECT` from them. If a view joins 5 tables and scans 100 million rows, every dashboard refresh re-runs that expensive computation. For small datasets, views are fine. For large datasets powering dashboards that refresh every minute, views become a performance bottleneck. The solution: pre-aggregate results into a physical table that dashboards query directly.

#### Creating a pre-aggregated table

```sql
CREATE TABLE agg_daily_revenue (
  aggregation_date DATE,
  product_line VARCHAR(100),
  total_revenue NUMERIC(12,2),
  order_count INTEGER,
  avg_order_value NUMERIC(10,2),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO agg_daily_revenue
SELECT 
  DATE(o.order_date) AS aggregation_date,
  p.product_line,
  SUM(o.order_amount) AS total_revenue,
  COUNT(DISTINCT o.order_id) AS order_count,
  AVG(o.order_amount) AS avg_order_value,
  CURRENT_TIMESTAMP AS updated_at
FROM orders o
JOIN products p ON o.product_id = p.id
GROUP BY DATE(o.order_date), p.product_line;
```

Dashboards query `agg_daily_revenue` directly. Result: instant load times regardless of raw table size.

#### Naming convention: `agg_` prefix

Prefix aggregated tables with `agg_`. Pattern: `agg_[grain]_[subject]`. Examples: `agg_daily_revenue`, `agg_hourly_metrics`, `agg_monthly_churn`. The prefix tells everyone: this is pre-computed data, not raw data, and it needs periodic refresh.

#### Always include `updated_at` in aggregated tables

The `updated_at` timestamp tells consumers how stale the data is. If `agg_daily_revenue` was last updated 3 days ago, the dashboard should display a warning. Without this column, users assume data is current when it may not be. Stale data presented as current data is worse than no data at all.

**You just learned** when and how to build pre-aggregated tables for dashboard performance. Now you will learn how to refresh these tables and version-control your view definitions as code.

## Refresh Strategy and Version Control

### Treating SQL Definitions as Code

#### Refresh patterns for aggregated tables

Aggregated tables must be refreshed on a schedule. Common patterns: (1) Full refresh - truncate and reload. Simple but slow for large tables. Best for daily aggregations. (2) Incremental refresh - only insert or update rows for dates not yet aggregated. Faster but more complex. Best for hourly or real-time aggregations. (3) Append-only - insert new rows without touching historical data. Fastest but requires careful de-duplication. Choose based on data volume and freshness requirements.

#### Save view definitions as `.sql` files in version control

Every view and aggregation query should be saved as a `.sql` file in your repository. Structure: `database/views/vw_active_customers.sql` and `database/aggregations/agg_daily_revenue.sql`. Include comments at the top of each file explaining purpose, business metric, who uses it, and column descriptions. Version-controlled SQL means: you can see who changed a metric definition, when, and why. Rollback is possible. Code review catches errors before they reach production.

### Clean data layer checklist

- Every shared metric defined as a SQL view with `vw_` prefix
- Expensive computations pre-aggregated in `agg_` tables with `updated_at`
- Dashboards query views and aggregated tables - never raw tables directly
- All SQL definitions saved as .sql files in version control with comments
- Refresh schedule documented and automated
- Naming conventions documented in a team conventions file

**You just learned** how to build a complete clean data layer with SQL views, pre-aggregated tables, naming conventions, and version control. This layer is the foundation that prevents metric drift and keeps dashboards fast and trustworthy.

## Bonus Resources

- [dbt (Data Build Tool) - the industry standard for managing SQL transformations and view definitions as version-controlled code](https://www.getdbt.com/)
- [Materialized Views - database-native pre-computation that refreshes automatically on some platforms](https://en.wikipedia.org/wiki/Materialized_view)
- [Data Mesh Principles - organizing data ownership and metric definitions across teams at scale](https://martinfowler.com/articles/data-mesh-principles.html)
- [SQL Style Guide - consistent formatting and naming conventions for SQL across teams](https://www.sqlstyle.guide/)
