import pandas as pd
from sqlalchemy import create_engine
import os

def load_query(query_name):
    """Load SQL query from file."""
    path = f'queries/{query_name}.sql'
    if not os.path.exists(path):
        raise FileNotFoundError(f"Query file not found at {path}")
    with open(path, 'r') as f:
        return f.read()

def validate_metrics(mau_df, revenue_df, funnel_df):
    """Validate metric computation logic and constraints."""
    
    # Check for nulls
    assert mau_df.isnull().sum().sum() == 0, "MAU DataFrame has nulls"
    assert revenue_df.isnull().sum().sum() == 0, "Revenue DataFrame has nulls"
    
    # Check value ranges
    assert (revenue_df['monthly_revenue'] > 0).all(), "Revenue must be > 0"
    assert (funnel_df['conversion_pct'] >= 0).all() and (funnel_df['conversion_pct'] <= 100).all(), "Conversion % out of range"
    
    # Check consistency
    for idx, row in revenue_df.iterrows():
        assert row['order_count'] > 0, "Zero orders detected"
        assert row['monthly_revenue'] > 0, "Zero revenue detected"
    
    print("✓ All metrics passed validation checks successfully.")
    return True

def main():
    print("="*60)
    print("SQL BUSINESS METRICS QUERY EXECUTION")
    print("="*60)
    
    engine = create_engine('sqlite:///analytics.db')
    
    # Task 4: Load and Execute Queries from Python
    print("\n[Task 4] Executing SQL queries from .sql files...")
    
    mau_query = load_query('monthly_active_users')
    mau = pd.read_sql(mau_query, engine)
    print("\nMonthly Active Users Result:")
    print(mau)

    revenue_query = load_query('revenue_by_segment')
    revenue = pd.read_sql(revenue_query, engine)
    print("\nRevenue by Segment Result:")
    print(revenue)

    funnel_query = load_query('conversion_funnel')
    funnel = pd.read_sql(funnel_query, engine)
    print("\nConversion Funnel Result:")
    print(funnel)

    # Task 5: Validate Query Results
    print("\n[Task 5] Running Metric Validations...")
    validate_metrics(mau, revenue, funnel)
    print("="*60)

if __name__ == '__main__':
    main()