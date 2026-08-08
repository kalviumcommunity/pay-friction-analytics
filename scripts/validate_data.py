import pandas as pd
import os

def run_validation_pipeline():
    # Load raw data
    raw_path = 'data/raw/unvalidated_customers.csv'
    df = pd.read_csv(raw_path)
    
    print("="*60)
    print("DATA VALIDATION PIPELINE")
    print("="*60)
    
    # Pre-requisite: Convert date columns to datetime objects for accurate comparison
    df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
    df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')

    # ---------------------------------------------------------
    # Task 1: Range Checks
    # ---------------------------------------------------------
    df['valid_age'] = (df['age'] >= 0) & (df['age'] <= 150)
    df['valid_price'] = df['price'] >= 0
    df['valid_date'] = (df['birth_date'] >= pd.Timestamp('1920-01-01')) & (df['birth_date'] <= pd.Timestamp.now())
    
    print(f"Invalid ages: {(~df['valid_age']).sum()}")
    print(f"Invalid prices: {(~df['valid_price']).sum()}")
    print(f"Invalid birth dates: {(~df['valid_date']).sum()}")

    # ---------------------------------------------------------
    # Task 2: Null Constraints
    # ---------------------------------------------------------
    df['valid_customer_id'] = df['customer_id'].notna()
    df['valid_email'] = df['email'].notna()
    
    print(f"Missing customer IDs: {(~df['valid_customer_id']).sum()}")
    print(f"Missing emails: {(~df['valid_email']).sum()}")

    # ---------------------------------------------------------
    # Task 3: Format Pattern Validation
    # ---------------------------------------------------------
    df['valid_email_format'] = df['email'].str.contains('@', na=False)
    df['valid_phone'] = df['phone'].astype(str).str.match(r'^\d{10}$', na=False)
    
    print(f"Invalid email formats: {(~df['valid_email_format']).sum()}")
    print(f"Invalid phone formats: {(~df['valid_phone']).sum()}")

    # ---------------------------------------------------------
    # Task 4: Business Rule Validation
    # ---------------------------------------------------------
    # End date must be on or after the start date
    df['valid_date_order'] = df['end_date'] >= df['start_date']
    
    print(f"Invalid date ranges: {(~df['valid_date_order']).sum()}")

    # ---------------------------------------------------------
    # Task 5: Validation Report & Isolation
    # ---------------------------------------------------------
    validation_cols = [
        'valid_age', 'valid_price', 'valid_date', 
        'valid_customer_id', 'valid_email', 'valid_email_format', 
        'valid_phone', 'valid_date_order'
    ]
    
    # A record must pass ALL checks to proceed
    df['passes_all_checks'] = df[validation_cols].all(axis=1)
    
    # Isolate failures
    failures = df[~df['passes_all_checks']]
    
    os.makedirs('output', exist_ok=True)
    failures.to_csv('output/validation_failures.csv', index=False)
    
    print("\n" + "="*60)
    print("VALIDATION REPORT SUMMARY")
    print("="*60)
    print(f"Total Records Evaluated: {len(df)}")
    print(f"Records Passed (Clean):  {df['passes_all_checks'].sum()}")
    print(f"Records Failed (Quarantine): {(~df['passes_all_checks']).sum()}")
    
    # Proceed with clean data only
    df_clean = df[df['passes_all_checks']].drop(columns=validation_cols + ['passes_all_checks'])
    
    os.makedirs('data/processed', exist_ok=True)
    df_clean.to_csv('data/processed/validated_clean_data.csv', index=False)
    
    print("\n✓ Failed records isolated to output/validation_failures.csv")
    print("✓ Clean records saved to data/processed/validated_clean_data.csv")

if __name__ == "__main__":
    run_validation_pipeline()