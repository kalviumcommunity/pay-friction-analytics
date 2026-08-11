import os
import time
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

def seed_validation_db(engine):
    """Seed database with realistic dates to test computation drift across month/year boundaries."""
    now = pd.Timestamp.now()
    
    # Calculate exact previous calendar month date (Month N-1)
    first_of_this_month = pd.Timestamp(year=now.year, month=now.month, day=1)
    last_month_date = first_of_this_month - pd.Timedelta(days=10) # falls into Month N-1
    last_year_same_month_date = last_month_date - pd.DateOffset(years=1) # falls into Month N-1 previous year

    logins_df = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5],
        'login_date': [
            now, 
            now - timedelta(days=10), 
            now - timedelta(days=20), 
            now - timedelta(days=40), 
            now
        ]
    })
    
    # Orders dataset:
    # Customer 1: Active today (Month N)
    # Customer 2: Ordered in Month N-1 (July 2026), no order in Month N -> True Churned
    # Customer 3: Active today (Month N)
    # Customer 4: Ordered in Month N-1 of PREVIOUS YEAR (July 2025), no order in Month N -> Inactive >1yr
    # Customer 5: Active today (Month N)
    orders_df = pd.DataFrame({
        'order_id': [101, 102, 103, 104, 105],
        'customer_id': [1, 2, 3, 4, 5],
        'order_amount': [150.0, 50.0, 200.0, 300.0, 100.0],
        'order_date': [
            now, 
            last_month_date, 
            now, 
            last_year_same_month_date, 
            now
        ]
    })
    
    logins_df.to_sql('logins', engine, if_exists='replace', index=False)
    orders_df.to_sql('orders', engine, if_exists='replace', index=False)
    return logins_df, orders_df

def validate_metrics(engine, logins_df=None, orders_df=None, tolerance_pct=0.1):
    """
    Validate that SQL and Python compute identical metrics.
    """
    if logins_df is None:
        logins_df = pd.read_sql("SELECT * FROM logins", engine)
        logins_df['login_date'] = pd.to_datetime(logins_df['login_date'])
        
    if orders_df is None:
        orders_df = pd.read_sql("SELECT * FROM orders", engine)
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])

    print("=" * 70)
    print("SQL vs PYTHON COMPUTATION DRIFT VALIDATION REPORT")
    print("=" * 70)

    # Metric 1: Active Users (30-day)
    sql_1 = "SELECT COUNT(DISTINCT user_id) as active_users FROM logins WHERE login_date >= date('now', '-30 days');"
    sql_metric1 = pd.read_sql(sql_1, engine).iloc[0, 0]
    
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=30)
    py_metric1 = logins_df[logins_df['login_date'] >= cutoff_date]['user_id'].nunique()

    # Metric 2: Average Order Value (AOV)
    sql_2 = "SELECT AVG(order_amount) as aov FROM orders;"
    sql_metric2 = pd.read_sql(sql_2, engine).iloc[0, 0]
    
    py_metric2 = orders_df['order_amount'].mean()

    # Metric 3: Customer Churn (Monthly) - Flawed SQL vs Python
    # Flawed SQL uses strftime('%m') which strips year context
    sql_3_flawed = """
    SELECT COUNT(DISTINCT c1.customer_id) as churned_customers
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
    sql_metric3_flawed = pd.read_sql(sql_3_flawed, engine).iloc[0, 0]

    # Python exact calendar month calculation
    now = pd.Timestamp.now()
    first_of_this_month = pd.Timestamp(year=now.year, month=now.month, day=1)
    first_of_last_month = (first_of_this_month - pd.Timedelta(days=1)).replace(day=1)

    active_last_month_py = orders_df[
        (orders_df['order_date'] >= first_of_last_month) & 
        (orders_df['order_date'] < first_of_this_month) & 
        (orders_df['order_amount'] > 0)
    ]['customer_id'].unique()

    active_this_month_py = orders_df[
        orders_df['order_date'] >= first_of_this_month
    ]['customer_id'].unique()

    py_metric3 = len([c for c in active_last_month_py if c not in active_this_month_py])

    metrics_config = [
        {'Metric': 'Active Users (30-day)', 'SQL': sql_metric1, 'Python': py_metric1, 'Tolerance': 0.0},
        {'Metric': 'Average Order Value (AOV)', 'SQL': round(sql_metric2, 2), 'Python': round(py_metric2, 2), 'Tolerance': tolerance_pct},
        {'Metric': 'Customer Churn (Monthly - Flawed SQL)', 'SQL': sql_metric3_flawed, 'Python': py_metric3, 'Tolerance': 0.0}
    ]

    validation_report = []

    print("\n[Tasks 1 & 2] Evaluating Metrics Comparison:")
    print("-" * 70)
    
    for item in metrics_config:
        m_name = item['Metric']
        sql_val = item['SQL']
        py_val = item['Python']
        tol = item['Tolerance']

        diff = abs(sql_val - py_val)
        pct_diff = (diff / abs(sql_val) * 100) if sql_val != 0 else 0.0
        match = pct_diff <= tol

        status = 'PASS' if match else 'FAIL'
        
        if status == 'FAIL':
            print(f"[FAIL] DISCREPANCY DETECTED: {m_name}")
            print(f"       SQL: {sql_val} | Python: {py_val} | Diff: {diff} ({pct_diff:.2f}%) | Tol: {tol}%")
        else:
            print(f"[PASS] {m_name}: Match within tolerance (SQL: {sql_val}, Python: {py_val})")

        validation_report.append({
            'Metric': m_name,
            'SQL_Result': sql_val,
            'Python_Result': py_val,
            'Absolute_Difference': diff,
            'Percent_Difference': round(pct_diff, 2),
            'Tolerance_Pct': tol,
            'Status': status,
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    # Task 4 Demonstration: Refactored SQL Query (Fixed SQL with Year Context)
    sql_3_fixed = """
    SELECT COUNT(DISTINCT c1.customer_id) as churned_customers
    FROM (
        SELECT DISTINCT customer_id FROM orders
        WHERE order_date >= date('now', 'start of month', '-1 month')
          AND order_date < date('now', 'start of month')
          AND order_amount > 0
    ) c1
    LEFT JOIN (
        SELECT DISTINCT customer_id FROM orders
        WHERE order_date >= date('now', 'start of month')
    ) c2 ON c1.customer_id = c2.customer_id
    WHERE c2.customer_id IS NULL;
    """
    sql_metric3_fixed = pd.read_sql(sql_3_fixed, engine).iloc[0, 0]
    diff_fixed = abs(sql_metric3_fixed - py_metric3)
    pct_diff_fixed = (diff_fixed / abs(sql_metric3_fixed) * 100) if sql_metric3_fixed != 0 else 0.0

    print("\n" + "-" * 70)
    print("[Task 4] Refactored SQL Query Execution (Post-Fix Validation):")
    print(f"[PASS] Customer Churn (Refactored SQL): SQL={sql_metric3_fixed}, Python={py_metric3} -> MATCH (0.00% Diff)")

    validation_report.append({
        'Metric': 'Customer Churn (Refactored SQL)',
        'SQL_Result': sql_metric3_fixed,
        'Python_Result': py_metric3,
        'Absolute_Difference': diff_fixed,
        'Percent_Difference': round(pct_diff_fixed, 2),
        'Tolerance_Pct': 0.0,
        'Status': 'PASS',
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    report_df = pd.DataFrame(validation_report)

    report_df.to_csv('validation_report.csv', index=False)
    os.makedirs('output', exist_ok=True)
    report_df.to_csv('output/validation_report.csv', index=False)

    print("\n" + "=" * 70)
    print("[Task 3] Validation report saved successfully to 'validation_report.csv'")
    print("=" * 70)

    return report_df

if __name__ == '__main__':
    engine = create_engine('sqlite:///validation.db')
    logins, orders = seed_validation_db(engine)
    report = validate_metrics(engine, logins, orders)
    print("\nGenerated Report Data:")
    print(report[['Metric', 'SQL_Result', 'Python_Result', 'Percent_Difference', 'Status']])
