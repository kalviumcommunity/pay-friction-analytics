# SQL Optimization Follow-Up Answers

### 1. Indexing Tradeoffs
**Question:** Explain how an index on a high-cardinality column would improve performance and what the tradeoff is.
**Answer:** An index creates a structured "lookup table" (like a B-Tree) for a column. If we apply a `WHERE transaction_id = 105` filter, the database uses the index to jump instantly to that row instead of performing a "full table scan" across 100 million rows. The tradeoff is that indices consume disk space and slow down write operations (INSERT/UPDATE/DELETE), because every time new data arrives, the index tree must be recalculated and reordered.

### 2. CTE Caching
**Question:** If you reference the same intermediate result multiple times in a CTE, does the database recalculate it, or does it cache it?
**Answer:** In modern PostgreSQL (v12+), CTEs are inherently "inlined" and re-calculated by default if the query planner thinks it's faster. However, if a CTE is referenced multiple times, you can force the database to cache the intermediate result in memory by adding the keyword `MATERIALIZED` (e.g., `WITH my_cte AS MATERIALIZED (...)`). This prevents the DB from executing that block of logic multiple times, saving immense processing power.

### 3. Scaling Beyond SELECT Optimization
**Question:** If the filtered dataset is still very large (100 million rows), what query techniques beyond SELECT optimization could further improve performance?
**Answer:** 
1. **Partitioning:** Splitting the massive transaction table physically by month (e.g., `transactions_2024_01`). A query looking for January data only scans that tiny partition instead of the whole table.
2. **Materialized Views:** If the dashboard only needs daily summarized totals, create a Materialized View that pre-computes the heavy `GROUP BY` logic overnight. The dashboard queries the tiny summary table instantly, completely bypassing the 100M row raw table.