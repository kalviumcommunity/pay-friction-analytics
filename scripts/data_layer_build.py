import os
import time
import pandas as pd
from sqlalchemy import create_engine

def load_sql_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def execute_sql(sql, engine):
    with engine.begin() as conn:
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            clean_lines = [line for line in stmt.splitlines() if not line.strip().startswith('--')]
            clean_stmt = '\n'.join(clean_lines).strip()
            if clean_stmt:
                conn.exec_driver_sql(clean_stmt)

def build_and_query_layer():
    print("=" * 70)
    print("SQL VIEWS & AGGREGATION LAYER DESIGN")
    print("=" * 70)
    
    engine = create_engine('sqlite:///optimization.db')

    # Seed DB if not present
    with engine.connect() as conn:
        tables_df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        existing_tables = tables_df['name'].tolist()

    if 'customers' not in existing_tables or 'transactions' not in existing_tables:
        print("\n[Database Setup] Seeding dataset...")
        from scripts.seed_optimization_db import seed_db
        seed_db()

    # Tasks 1 & 2: Create Views and Aggregation Table
    print("\n[Tasks 1 & 2] Building Views and Pre-Aggregated Tables...")
    execute_sql("DROP VIEW IF EXISTS vw_active_customers;", engine)
    execute_sql("DROP VIEW IF EXISTS vw_product_performance;", engine)
    execute_sql("DROP TABLE IF EXISTS agg_daily_metrics;", engine)
    
    execute_sql(load_sql_file('database/views/vw_active_customers.sql'), engine)
    execute_sql(load_sql_file('database/views/vw_product_performance.sql'), engine)
    execute_sql(load_sql_file('database/aggregations/agg_daily_metrics.sql'), engine)
    
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
    print("[OK] Views created and Aggregation Table populated successfully.")

    # Task 3: Query Views & Aggregated Tables from Python
    print("\n[Task 3] Simulating Dashboard Queries against Clean Data Layer...")
    
    active_cust_df = pd.read_sql("""
        SELECT customer_id, customer_name, segment, revenue_30d, days_since_order
        FROM vw_active_customers
        WHERE days_since_order <= 30
        ORDER BY revenue_30d DESC
        LIMIT 5
    """, engine)
    print("\nTop 5 Active Customers (vw_active_customers):")
    print(active_cust_df)

    product_df = pd.read_sql("""
        SELECT product_name, category, total_units_sold, lifetime_revenue
        FROM vw_product_performance
        ORDER BY lifetime_revenue DESC
        LIMIT 5
    """, engine)
    print("\nTop 5 Products by Revenue (vw_product_performance):")
    print(product_df)

    start = time.time()
    agg_result = pd.read_sql("""
        SELECT aggregation_date, metric_name, metric_value, updated_at
        FROM agg_daily_metrics
        ORDER BY aggregation_date DESC
        LIMIT 5
    """, engine)
    elapsed = (time.time() - start) * 1000
    
    print(f"\nRecent Daily Aggregations (agg_daily_metrics) - Query took {elapsed:.2f}ms:")
    print(agg_result)

    segment_summary = pd.read_sql("""
        SELECT segment, COUNT(*) as cust_count, SUM(revenue_30d) as total_rev
        FROM vw_active_customers
        GROUP BY segment
    """, engine)
    print("\nSegment Summary queried directly from View:")
    print(segment_summary)
    print("=" * 70)

if __name__ == '__main__':
    build_and_query_layer()