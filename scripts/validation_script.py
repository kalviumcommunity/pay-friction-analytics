import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import os

def seed_validation_db(engine):
    """Seed the database with intentional cross-year dates to trigger computation drift."""
    now = pd.Timestamp.now()
    
    logins_df = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5],
        'login_date': [now, now - timedelta(days=10), now - timedelta(days=20), now - timedelta(days=40), now]
    })
    
    orders_df = pd.DataFrame({
        'order_id': [101, 102, 103, 104, 105],
        'customer_id': [1, 2, 3, 4, 5],
        'order_amount': [150.0, 50.0, 200.0, 300.0, 100.0],
        # Customer 4 ordered EXACTLY 1 year and 1 month ago.
        # Customer 2 ordered 45 days ago (N-1 month).
        'order_date': [now, now - timedelta(days=45), now, now - timedelta(days=395), now]
    })
    
    logins_df.to_sql('logins', engine, if_exists='replace', index=False)
    orders_df.to_sql('orders', engine, if_exists='replace', index=False)
    return logins_df, orders_df

def validate_metrics(engine, logins_df, orders_df, tolerance_pct=0.1):
    """Automated Validation Script comparing SQL and Python outputs."""
    
    print("\n[Task 1 & 2] Computing Metrics and Identifying Discrepancies...")
    
    # ---------------------------------------------------------
    # Metric 1: Active Users (Last 30 Days)
    # ---------------------------------------------------------
    sql_1 = "SELECT COUNT(DISTINCT user_id) FROM logins WHERE login_date >= date('now', '-30 days')"
    sql_metric1 = pd.read_sql(sql_1, engine).iloc[0, 0]
    
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=30)
    py_metric1 = logins_df[logins_df['login_date'] >= cutoff_date]['user_id'].nunique()

    # ---------------------------------------------------------
    # Metric 2: Average Order Value (AOV)
    # ---------------------------------------------------------
    sql_2 = "SELECT AVG(order_amount) FROM orders"
    sql_metric2 = pd.read_sql(sql_2, engine).iloc[0, 0]
    
    py_metric2 = orders_df['order_amount'].mean()

    # ---------------------------------------------------------
    # Metric 3: Customer Churn (Monthly) - INTENTIONAL SQL DRIFT
    # SQL uses flawed month-string matching. Python uses strict rolling days.
    # ---------------------------------------------------------
    sql_3 = """
    SELECT COUNT(DISTINCT c1.customer_id) as churned
    FROM (
        SELECT DISTINCT customer_id FROM orders
        WHERE strftime('%m', order_date) = strftime('%m', 'now', '-1 month')
          AND order_amount > 0
    ) c1
    LEFT JOIN (
        SELECT DISTINCT customer_id FROM orders
        WHERE strftime('%m', order_date) = strftime('%m', 'now')
    ) c2 ON c1.customer_id = c2.customer_id
    WHERE c2.customer_id IS NULL;
    """
    sql_metric3 = pd.read_sql(sql_3, engine).iloc[0, 0]
    
    # Python Correct Calculation: 30-60 days ago vs Last 30 days
    now = pd.Timestamp.now()
    p1_start = now - pd.Timedelta(days=60)
    p1_end = now - pd.Timedelta(days=30)
    
    active_p1 = orders_df[(orders_df['order_date'] >= p1_start) & 
                          (orders_df['order_date'] < p1_end) & 
                          (orders_df['order_amount'] > 0)]['customer_id'].unique()
                          
    active_p2 = orders_df[orders_df['order_date'] >= p1_end]['customer_id'].unique()
    
    py_metric3 = len([c for c in active_p1 if c not in active_p2])

    # ---------------------------------------------------------
    # Task 3: Build Automated Validation Report
    # ---------------------------------------------------------
    validation_report = []
    
    metrics_config = {
        'Active Users': {'sql': sql_metric1, 'py': py_metric1, 'tol': 0},
        'Avg Order Value': {'sql': sql_metric2, 'py': py_metric2, 'tol': 0.1},
        'Customer Churn': {'sql': sql_metric3, 'py': py_metric3, 'tol': 0}
    }
    
    print("="*60)
    print("SQL vs PYTHON COMPUTATION DRIFT REPORT")
    print("="*60)
    
    for metric_name, data in metrics_config.items():
        diff = abs(data['sql'] - data['py'])
        pct_diff = (diff / abs(data['sql']) * 100) if data['sql'] != 0 else 0
        match = pct_diff <= data['tol']
        
        status = 'PASS' if match else 'FAIL'
        if status == 'FAIL':
            print(f"⚠️ DISCREPANCY: {metric_name} differs by {pct_diff:.2f}% (SQL: {data['sql']}, PY: {data['py']})")
        else:
            print(f"✓ {metric_name}: Match within tolerance.")
            
        validation_report.append({
            'Metric': metric_name,
            'SQL_Result': data['sql'],
            'Python_Result': data['py'],
            'Absolute_Diff': diff,
            'Pct_Difference': pct_diff,
            'Tolerance': data['tol'],
            'Status': status,
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    report_df = pd.DataFrame(validation_report)
    
    os.makedirs('output', exist_ok=True)
    report_df.to_csv('output/validation_report.csv', index=False)
    print("\n✓ Automated validation report saved to 'output/validation_report.csv'")
    print("="*60)

if __name__ == '__main__':
    engine = create_engine('sqlite:///validation.db')
    logins, orders = seed_validation_db(engine)
    validate_metrics(engine, logins, orders)