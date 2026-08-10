import pandas as pd
from sqlalchemy import create_engine
import os

def load_query(filename):
    with open(f'queries/{filename}', 'r') as f:
        return f.read()

def run_tests():
    print("="*60)
    print("SQL FILTERING, GROUPING & AGGREGATION TEST RUNNER")
    print("="*60)
    
    engine = create_engine('sqlite:///analytics.db')
    
    queries = {
        "Task 1 (WHERE Filtering)": "where_filtering.sql",
        "Task 2 (GROUP BY & Aggregation)": "group_by_aggregation.sql",
        "Task 3 (HAVING Filtering)": "having_filtering.sql",
        "Task 4 (WHERE + HAVING Combined)": "where_having_combined.sql",
        "Task 5 (ORDER BY & Ranking)": "order_by_ranking.sql"
    }
    
    for task_name, filename in queries.items():
        print(f"\n--- Executing: {task_name} ---")
        sql = load_query(filename)
        df = pd.read_sql(sql, engine)
        print(df.head(5))
        print(f"Retrieved {len(df)} rows.")
        
    print("\n✓ All filtering and aggregation queries executed successfully.")
    print("="*60)

if __name__ == '__main__':
    run_tests()