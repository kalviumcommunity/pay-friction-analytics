import pandas as pd
from sqlalchemy import create_engine, inspect, text
import os

# ---------------------------------------------------------
# Task 5: Make Loading Repeatable (Wraps Task 1 & 2)
# ---------------------------------------------------------
def load_cleaned_data_to_database(df, table_name, database_path='analytics.db'):
    """Load cleaned DataFrame to database - repeatable function."""
    
    # Task 1: Setup Database Connection
    engine = create_engine(f'sqlite:///{database_path}')
    
    with engine.connect() as conn:
        print("✓ Database connection successful")
    
    # Task 2: Load Cleaned DataFrame as Table
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    
    # Verify table created using modern SQLAlchemy Inspector
    inspector = inspect(engine)
    print(f"Tables in database: {inspector.get_table_names()}")
    
    # Check row count
    count_df = pd.read_sql(f"SELECT COUNT(*) as row_count FROM {table_name}", engine)
    rows_loaded = count_df.iloc[0]['row_count']
    
    print(f"✓ Loaded {rows_loaded} rows to '{table_name}' table")
    return engine


def run_database_workflow():
    print("="*60)
    print("SQL ENVIRONMENT & DATABASE INTEGRATION")
    print("="*60)
    
    os.makedirs('output', exist_ok=True)
    db_path = 'output/payfriction_analytics.db'
    
    # Load sample CSV and ensure proper datetime types before loading to SQL
    df_clean = pd.read_csv('data/processed/customers_cleaned.csv')
    df_clean['signup_date'] = pd.to_datetime(df_clean['signup_date'])
    
    print("\n[Tasks 1, 2, & 5] Connecting and Loading Data...")
    engine = load_cleaned_data_to_database(df_clean, 'customers_cleaned', db_path)

    # ---------------------------------------------------------
    # Task 3: Validate Schema
    # ---------------------------------------------------------
    print("\n[Task 3] Validating Schema...")
    inspector = inspect(engine)
    columns = inspector.get_columns('customers_cleaned')
    
    print("TABLE SCHEMA:")
    for col in columns:
        print(f"  {col['name']:15} {str(col['type']):12} {'NOT NULL' if col['nullable']==False else ''}")

    print("\nDATATYPE VALIDATION:")
    expected_types = {
        'customer_id': 'BIGINT',  # Pandas ints map to BIGINT in SQLite
        'email': 'TEXT',          # Pandas strings map to TEXT
        'signup_date': 'DATETIME' # Parsed dates map to DATETIME
    }

    for col_name, expected_type in expected_types.items():
        actual = [c['type'] for c in columns if c['name'] == col_name][0]
        # Check if expected type is in the actual string (e.g., 'BIGINT' inside 'BIGINT')
        status = '✓' if expected_type in str(actual).upper() else '✗'
        print(f"{status} {col_name}: {actual} (Expected: {expected_type})")

    # ---------------------------------------------------------
    # Task 4: Query and Return Results
    # ---------------------------------------------------------
    print("\n[Task 4] Querying and Returning Results...")
    
    # Simple query
    query = "SELECT * FROM customers_cleaned WHERE customer_type = 'Enterprise'"
    results = pd.read_sql(query, engine)
    print(f"Retrieved {len(results)} rows for Enterprise customers:")
    print(results[['customer_id', 'email', 'lifetime_value']])

    # More complex aggregation query
    query_agg = """
    SELECT 
        customer_type,
        COUNT(*) as count,
        AVG(lifetime_value) as avg_ltv
    FROM customers_cleaned
    GROUP BY customer_type
    ORDER BY avg_ltv DESC
    """
    
    summary = pd.read_sql(query_agg, engine)
    print("\nSummary by segment (Executed via SQL Engine):")
    print(summary)
    
    print("="*60)

if __name__ == "__main__":
    run_database_workflow()