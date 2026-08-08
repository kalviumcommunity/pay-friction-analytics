import pandas as pd
import os

def build_features():
    # Load raw data
    raw_path = 'data/raw/customer_metrics.csv'
    df = pd.read_csv(raw_path)
    
    print("="*60)
    print("FEATURE ENGINEERING & DERIVED COLUMNS")
    print("="*60)
    
    # ---------------------------------------------------------
    # Task 1: Compute Ratio Features
    # ---------------------------------------------------------
    print("\n[Task 1] Computing Ratio Features...")
    df['transactions_per_month'] = df['total_transactions'] / (df['days_as_customer'] / 30)
    df['avg_spend_per_transaction'] = df['total_spent'] / df['total_transactions']
    df['lifetime_value_per_month'] = df['total_spent'] / (df['days_as_customer'] / 30)
    
    print("Descriptive stats for new ratio features:")
    print(df[['transactions_per_month', 'avg_spend_per_transaction']].describe().round(2))

    # ---------------------------------------------------------
    # Task 2: Binning with Equal-Width Bins (cut)
    # ---------------------------------------------------------
    print("\n[Task 2] Creating Engagement Tiers (pd.cut)...")
    df['engagement_tier'] = pd.cut(
        df['transactions_per_month'],
        bins=[0, 2, 10, float('inf')],
        labels=['low', 'medium', 'high']
    )
    print("Engagement Tier Distribution:")
    print(df['engagement_tier'].value_counts())

    # ---------------------------------------------------------
    # Task 3: Binning with Quantiles (qcut)
    # ---------------------------------------------------------
    print("\n[Task 3] Creating Spend Quartiles (pd.qcut)...")
    df['spend_quartile'] = pd.qcut(
        df['total_spent'],
        q=4,
        labels=['Q1', 'Q2', 'Q3', 'Q4']
    )
    print("Spend Quartile Distribution:")
    print(df['spend_quartile'].value_counts())

    # ---------------------------------------------------------
    # Task 4: Composite Score (RFM)
    # ---------------------------------------------------------
    print("\n[Task 4] Building RFM Composite Score...")
    # Recency: Lower days = higher score (5 is best)
    df['recency_score'] = pd.qcut(df['days_since_last_purchase'], q=5, labels=[5, 4, 3, 2, 1])
    
    # Frequency: Higher count = higher score
    df['frequency_score'] = pd.qcut(df['purchase_count'], q=5, labels=[1, 2, 3, 4, 5])
    
    # Monetary: Higher spend = higher score
    df['monetary_score'] = pd.qcut(df['total_spent'], q=5, labels=[1, 2, 3, 4, 5])

    # Combine into a single health score
    df['rfm_score'] = (
        df['recency_score'].astype(int) + 
        df['frequency_score'].astype(int) + 
        df['monetary_score'].astype(int)
    )
    print("RFM Scores Calculated successfully.")

    # ---------------------------------------------------------
    # Task 5: Feature Validation
    # ---------------------------------------------------------
    print("\n[Task 5] Feature Validation...")
    print(f"RFM score range: {df['rfm_score'].min()} (Lowest) to {df['rfm_score'].max()} (Highest)")
    
    # Ensure no NaNs were introduced by the binning edges
    missing_vals = df[['engagement_tier', 'spend_quartile', 'rfm_score']].isna().sum()
    print(f"\nMissing values check:\n{missing_vals}")
    
    # Preview the engineered dataset
    print("\nSample of engineered business features:")
    print(df[['customer_id', 'transactions_per_month', 'engagement_tier', 'spend_quartile', 'rfm_score']].head(3))

    # Save output
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/processed/engineered_features.csv', index=False)
    print("\n✓ Engineered features saved to data/processed/engineered_features.csv")
    print("="*60)

if __name__ == "__main__":
    build_features()