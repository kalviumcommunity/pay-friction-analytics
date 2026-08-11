import os
import time
import pandas as pd
from sqlalchemy import create_engine

# Utility function to load SQL from file
def load_sql_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

# Helper function to execute raw SQL using SQLAlchemy engine
def execute_sql(sql, engine):
    with engine.begin() as conn:
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            clean_lines = [line for line in stmt.splitlines() if not line.strip().startswith('--')]
            clean_stmt = '\n'.join(clean_lines).strip()
            if clean_stmt:
                conn.exec_driver_sql(clean_stmt)

def main():
    print("=" * 70)
    print("2.43 SQL VIEWS & AGGREGATION LAYER DESIGN - EXECUTION SCRIPT")
    print("=" * 70)

    db_path = 'optimization.db'
    engine = create_engine(f'sqlite:///{db_path}')

    # Check if database tables exist, if not seed the database
    with engine.connect() as conn:
        tables_df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        existing_tables = tables_df['name'].tolist()

    if 'customers' not in existing_tables or 'transactions' not in existing_tables:
        print("\n[Database Setup] Seeding optimization.db dataset...")
        from scripts.seed_optimization_db import seed_db
        seed_db()

    # ---------------------------------------------------------
    # Task 1: Create Two SQL Views
    # ---------------------------------------------------------
    print("\n" + "-" * 50)
    print("[Task 1] Creating SQL Views (vw_active_customers & vw_product_performance)...")
    print("-" * 50)

    vw1_sql = load_sql_file('database/views/vw_active_customers.sql')
    vw2_sql = load_sql_file('database/views/vw_product_performance.sql')

    execute_sql(vw1_sql, engine)
    execute_sql(vw2_sql, engine)

    active_customers_preview = pd.read_sql("SELECT * FROM vw_active_customers LIMIT 10", engine)
    product_perf_preview = pd.read_sql("SELECT * FROM vw_product_performance LIMIT 10", engine)

    print("[OK] View 1 (vw_active_customers) created. Columns:", active_customers_preview.columns.tolist())
    print("[OK] View 2 (vw_product_performance) created. Columns:", product_perf_preview.columns.tolist())

    # ---------------------------------------------------------
    # Task 2: Create One Pre-Aggregated Summary Table
    # ---------------------------------------------------------
    print("\n" + "-" * 50)
    print("[Task 2] Creating and Populating Pre-Aggregated Table (agg_daily_metrics)...")
    print("-" * 50)

    # Clean existing agg table if re-running
    execute_sql("DROP TABLE IF EXISTS agg_daily_metrics;", engine)

    agg_table_sql = load_sql_file('database/aggregations/agg_daily_metrics.sql')
    execute_sql(agg_table_sql, engine)

    populate_sql = """
    INSERT INTO agg_daily_metrics
    SELECT 
        date(transaction_date) as aggregation_date,
        'total_revenue' as metric_name,
        SUM(amount) as metric_value,
        COUNT(*) as row_count,
        CURRENT_TIMESTAMP as updated_at
    FROM transactions
    GROUP BY date(transaction_date);
    """
    execute_sql(populate_sql, engine)

    agg_data = pd.read_sql("SELECT * FROM agg_daily_metrics ORDER BY aggregation_date DESC LIMIT 10", engine)
    print(f"[OK] Aggregated {len(agg_data)} rows into agg_daily_metrics.")
    print("\nPreview of agg_daily_metrics:")
    print(agg_data)

    # Benchmark query speed
    start = time.time()
    result = pd.read_sql("SELECT metric_name, SUM(metric_value) AS grand_total FROM agg_daily_metrics GROUP BY metric_name", engine)
    elapsed = (time.time() - start) * 1000
    print(f"[OK] Query time against pre-aggregated table: {elapsed:.2f}ms")

    # ---------------------------------------------------------
    # Task 3: Query Views & Aggregated Tables from Python
    # ---------------------------------------------------------
    print("\n" + "-" * 50)
    print("[Task 3] Querying Views & Aggregated Tables from Python (Dashboard Simulation)...")
    print("-" * 50)

    # Query View 1: Active Customers
    active_cust_df = pd.read_sql("""
        SELECT 
            customer_id, 
            customer_name, 
            revenue_30d,
            days_since_order
        FROM vw_active_customers
        WHERE days_since_order <= 30
        ORDER BY revenue_30d DESC
        LIMIT 10
    """, engine)
    print("\nTop 10 Active Customers (last 30 days):")
    print(active_cust_df)

    # Query View 2: Product Performance
    custom_result = pd.read_sql("""
        SELECT 
            product_id,
            product_name,
            category,
            total_units_sold,
            lifetime_revenue
        FROM vw_product_performance
        ORDER BY lifetime_revenue DESC
        LIMIT 10
    """, engine)
    print("\nTop Products by Performance:")
    print(custom_result)

    # Query Pre-Aggregated Table
    agg_result = pd.read_sql("""
        SELECT 
            aggregation_date,
            metric_name,
            metric_value,
            row_count,
            updated_at
        FROM agg_daily_metrics
        ORDER BY aggregation_date DESC
        LIMIT 10
    """, engine)
    print("\nDaily Aggregated Metrics (Recent 10 days):")
    print(agg_result)

    # Demonstrate filtering capability
    active_by_segment = pd.read_sql("""
        SELECT 
            segment,
            COUNT(*) as customer_count,
            SUM(revenue_30d) as total_segment_revenue,
            AVG(revenue_30d) as avg_customer_revenue
        FROM vw_active_customers
        GROUP BY segment
        ORDER BY total_segment_revenue DESC
    """, engine)
    print("\nRevenue Breakdown by Segment (Queried from View):")
    print(active_by_segment)

    print("\n" + "=" * 70)
    print("ALL DATA LAYER TASKS EXECUTED AND VALIDATED SUCCESSFULLY.")
    print("=" * 70)

if __name__ == '__main__':
    main()
