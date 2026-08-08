import pandas as pd
import json
import os

def validate_and_merge():
    # Load Data
    df_customers = pd.read_csv('data/raw/customers.csv')
    df_orders = pd.read_csv('data/raw/orders.csv')
    
    print("="*60)
    print("MULTI-SOURCE MERGING & JOIN VALIDATION")
    print("="*60)
    
    # ---------------------------------------------------------
    # Task 1: Explicit Join with Row Count Validation
    # ---------------------------------------------------------
    print("\n[Task 1] Row Count Validation (Left Join)...")
    print(f"Left table (customers): {len(df_customers)} rows")
    print(f"Right table (orders): {len(df_orders)} rows")
    
    # Performing a Left Join
    df_merged = pd.merge(df_customers, df_orders, on='customer_id', how='left')
    
    print(f"Merged result: {len(df_merged)} rows")
    print(f"Change from left table: {len(df_merged) - len(df_customers)} rows (Expected if 1 customer has multiple orders)")
    
    # ---------------------------------------------------------
    # Task 2: Detect Unmatched Keys
    # ---------------------------------------------------------
    print("\n[Task 2] Detecting Unmatched Keys...")
    unmatched_customers = df_customers[~df_customers['customer_id'].isin(df_orders['customer_id'])]
    unmatched_orders = df_orders[~df_orders['customer_id'].isin(df_customers['customer_id'])]
    
    print(f"Customers without orders (Orphaned Left): {len(unmatched_customers)}")
    print(f"Orders without customers (Orphaned Right): {len(unmatched_orders)}")
    
    os.makedirs('output', exist_ok=True)
    unmatched_customers.to_csv('output/unmatched_customers.csv', index=False)
    unmatched_orders.to_csv('output/unmatched_orders.csv', index=False)
    print("✓ Saved unmatched records to 'output/' for investigation.")

    # ---------------------------------------------------------
    # Task 3: Compare Join Types
    # ---------------------------------------------------------
    print("\n[Task 3] Comparing Join Types...")
    inner = pd.merge(df_customers, df_orders, on='customer_id', how='inner')
    left = pd.merge(df_customers, df_orders, on='customer_id', how='left')
    outer = pd.merge(df_customers, df_orders, on='customer_id', how='outer')
    
    print(f"Inner Join Rows: {len(inner)} (Only matched)")
    print(f"Left Join Rows:  {len(left)}  (All customers + matched orders)")
    print(f"Outer Join Rows: {len(outer)} (Everything from both)")

    # ---------------------------------------------------------
    # Task 4: Validate No Unexpected Duplication
    # ---------------------------------------------------------
    print("\n[Task 4] Duplication & Key Validation...")
    print(f"Columns in merged dataset: {list(df_merged.columns)}")
    
    key_counts = df_merged['customer_id'].value_counts()
    print(f"Max orders per customer: {key_counts.max()}")
    print("If this number is unexpectedly massive, a Cartesian product (many-to-many explosion) may have occurred.")

    # ---------------------------------------------------------
    # Task 5: Document Join Decision
    # ---------------------------------------------------------
    print("\n[Task 5] Generating Join Decision Report...")
    join_report = {
        'join_type': 'left',
        'left_table': 'customers',
        'right_table': 'orders',
        'join_key': 'customer_id',
        'left_rows': len(df_customers),
        'right_rows': len(df_orders),
        'result_rows': len(df_merged),
        'unmatched_left': len(unmatched_customers),
        'unmatched_right': len(unmatched_orders),
        'reasoning': 'Left join was chosen to preserve all customer records, allowing us to identify zero-order customers. Orphaned orders (missing customer_id) are dropped from analysis but logged for data engineering to investigate.'
    }
    
    with open('output/join_report.json', 'w') as f:
        json.dump(join_report, f, indent=2)
        
    print(json.dumps(join_report, indent=2))
    
    # Save the finalized merged dataset
    os.makedirs('data/processed', exist_ok=True)
    df_merged.to_csv('data/processed/customer_orders_merged.csv', index=False)
    print("\n✓ Validated merge dataset saved to 'data/processed/customer_orders_merged.csv'")
    print("="*60)

if __name__ == "__main__":
    validate_and_merge()