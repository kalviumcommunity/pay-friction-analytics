import pandas as pd
import json
import os

# ---------------------------------------------------------
# REUSABLE KPI COMPUTATION FUNCTIONS
# ---------------------------------------------------------

def calculate_mau(df, days=30):
    """Monthly Active Users: distinct customers active in last N days."""
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    return df[df['transaction_date'] >= cutoff]['customer_id'].nunique()

def calculate_rpc(df):
    """Average revenue per unique customer (successful transactions only)."""
    success_df = df[df['status'] == 'success']
    if success_df['customer_id'].nunique() == 0: return 0
    return success_df['amount'].sum() / success_df['customer_id'].nunique()

def calculate_payment_success_rate(df):
    """Percentage of transaction attempts that succeed."""
    if len(df) == 0: return 0
    return len(df[df['status'] == 'success']) / len(df)

def calculate_failed_payment_ratio(df):
    """Percentage of transaction attempts that fail."""
    if len(df) == 0: return 0
    return len(df[df['status'] == 'failed']) / len(df)

def calculate_churn_rate(df, period_days=30):
    """Customers who had activity in period 1 (30-60 days ago) but none in period 2 (last 30 days)."""
    now = pd.Timestamp.now()
    p1_start = now - pd.Timedelta(days=period_days * 2)
    p1_end = now - pd.Timedelta(days=period_days)
    
    active_p1 = df[(df['transaction_date'] >= p1_start) & (df['transaction_date'] < p1_end)]['customer_id'].unique()
    active_p2 = df[(df['transaction_date'] >= p1_end) & (df['transaction_date'] <= now)]['customer_id'].unique()
    
    churned = [x for x in active_p1 if x not in active_p2]
    return len(churned) / len(active_p1) if len(active_p1) > 0 else 0

# ---------------------------------------------------------
# EXECUTION & REPORTING BLOCK
# ---------------------------------------------------------
if __name__ == '__main__':
    # Load Data
    df = pd.read_csv('data/raw/kpi_transactions.csv')
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # We will spoof the current date so our test data falls perfectly into the "last 30 days"
    # In production, you would remove this line and rely on pd.Timestamp.now() inside the functions
    fake_today = pd.Timestamp('2026-08-15')
    
    # Custom versions of the functions for this test script to use the spoofed date
    mau = df[df['transaction_date'] >= (fake_today - pd.Timedelta(days=30))]['customer_id'].nunique()
    rpc = calculate_rpc(df)
    psr = calculate_payment_success_rate(df)
    fpr = calculate_failed_payment_ratio(df)
    
    p1_active = df[(df['transaction_date'] >= (fake_today - pd.Timedelta(days=60))) & (df['transaction_date'] < (fake_today - pd.Timedelta(days=30)))]['customer_id'].unique()
    p2_active = df[(df['transaction_date'] >= (fake_today - pd.Timedelta(days=30))) & (df['transaction_date'] <= fake_today)]['customer_id'].unique()
    churn = len([x for x in p1_active if x not in p2_active]) / len(p1_active) if len(p1_active) > 0 else 0

    print("="*60)
    print("KPI DASHBOARD & VALIDATION REPORT")
    print("="*60)
    print(f"MAU: {mau}")
    print(f"Revenue per Customer: ${rpc:.2f}")
    print(f"Payment Success Rate: {psr:.1%}")
    print(f"Failed Payment Ratio: {fpr:.1%}")
    print(f"Involuntary Churn Rate: {churn:.1%}")
    
    # Task 3: Validate Against Targets
    print("\n[Validating against kpi_validation_targets.json]")
    with open('kpis/kpi_validation_targets.json', 'r') as f:
        targets = json.load(f)
        
    current_kpis = {
        'mau': mau,
        'rpc': rpc,
        'payment_success_rate': psr,
        'failed_payment_ratio': fpr,
        'involuntary_churn_rate': churn
    }
    
    validation_report = []
    for kpi_name, target_range in targets.items():
        actual = current_kpis[kpi_name]
        min_val, max_val = target_range['min'], target_range['max']
        status = 'PASS' if min_val <= actual <= max_val else 'ALERT'
        validation_report.append({'kpi': kpi_name, 'actual': actual, 'target_min': min_val, 'target_max': max_val, 'status': status})
        
    val_df = pd.DataFrame(validation_report)
    print(val_df.to_string(index=False))
    
    failures = val_df[val_df['status'] == 'ALERT']
    if len(failures) > 0:
        print(f"\n⚠️ {len(failures)} KPIs out of target range - REVIEW REQUIRED")
    else:
        print(f"\n✓ All {len(val_df)} KPIs within target range")

    # Task 4: KPI Decomposition
    print("\n" + "="*60)
    print("KPI DECOMPOSITION: Total Processed Revenue (Successful)")
    print("="*60)
    
    success_df = df[df['status'] == 'success']
    total_rev = success_df['amount'].sum()
    rev_by_segment = success_df.groupby('customer_type')['amount'].sum()
    rev_by_product = success_df.groupby(['customer_type', 'product'])['amount'].sum().reset_index()
    
    print(f"Level 1 (Top-level): ${total_rev:,.0f}")
    print("\nLevel 2 (By Segment):")
    for segment, amount in rev_by_segment.items():
        print(f"  {segment}: ${amount:,.0f}")
        
    print("\nLevel 3 (By Product within Segment):")
    for _, row in rev_by_product.iterrows():
        print(f"  {row['customer_type']} - {row['product']}: ${row['amount']:,.0f}")