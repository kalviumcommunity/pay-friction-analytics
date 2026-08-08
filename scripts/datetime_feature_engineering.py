import pandas as pd
import matplotlib.pyplot as plt
import os

def run_datetime_pipeline():
    # Load raw data
    raw_path = 'data/raw/transactions_time.csv'
    df = pd.read_csv(raw_path)
    
    print("="*60)
    print("DATE & TIME TRANSFORMATION PIPELINE")
    print("="*60)
    
    # ---------------------------------------------------------
    # Task 1: Parse Timestamp Strings with Explicit Format
    # ---------------------------------------------------------
    print("\n[Task 1] Parsing Timestamps...")
    df['transaction_date'] = pd.to_datetime(
        df['transaction_date'],
        format='%Y-%m-%d %H:%M:%S'
    )
    print(f"✓ Converted transaction_date to: {df['transaction_date'].dtype}")
    
    # ---------------------------------------------------------
    # Task 2: Extract Day-of-Week and Hour-of-Day
    # ---------------------------------------------------------
    print("\n[Task 2] Extracting Time Features...")
    df['day_of_week'] = df['transaction_date'].dt.day_name()
    df['hour'] = df['transaction_date'].dt.hour
    
    hourly_volume = df.groupby('hour').size()
    print("\nHourly Transaction Volume:")
    print(hourly_volume)
    
    # Plot and save histogram
    os.makedirs('output', exist_ok=True)
    plt.figure(figsize=(8, 4))
    hourly_volume.plot(kind='bar', color='skyblue')
    plt.title('Transaction Volume by Hour of Day')
    plt.xlabel('Hour (0-23)')
    plt.ylabel('Transaction Count')
    plt.tight_layout()
    plt.savefig('output/hourly_distribution.png')
    print("✓ Saved hourly distribution plot to output/hourly_distribution.png")

    # ---------------------------------------------------------
    # Task 3: Compute Week Number and Resample Data
    # ---------------------------------------------------------
    print("\n[Task 3] Computing Week Number & Resampling...")
    df['week_num'] = df['transaction_date'].dt.isocalendar().week
    
    # Set datetime as index for .resample()
    df_ts = df.set_index('transaction_date')
    weekly_revenue = df_ts['amount'].resample('W').sum()
    print("\nWeekly Revenue Trend:")
    print(weekly_revenue)

    # ---------------------------------------------------------
    # Task 4: Compute Days-Since-Event Metric
    # ---------------------------------------------------------
    print("\n[Task 4] Computing Recency (Days Since Last Purchase)...")
    today = pd.Timestamp.now()
    
    # Find the max (latest) purchase date per customer
    customer_last_purchase = df.groupby('customer_id')['transaction_date'].max().reset_index()
    customer_last_purchase.columns = ['customer_id', 'last_purchase_date']
    
    # Datetime arithmetic to get days
    customer_last_purchase['days_since_last_purchase'] = (today - customer_last_purchase['last_purchase_date']).dt.days
    
    # Merge back into main dataframe
    df = df.merge(customer_last_purchase[['customer_id', 'days_since_last_purchase']], on='customer_id')
    print(f"✓ Calculated recency based on current system date ({today.strftime('%Y-%m-%d')})")
    print("\nRecency Distribution:")
    print(df['days_since_last_purchase'].describe())

    # ---------------------------------------------------------
    # Task 5: Build Time-Indexed Aggregation
    # ---------------------------------------------------------
    print("\n[Task 5] Multi-dimensional Aggregations...")
    hourly_daily = df.groupby(['day_of_week', 'hour']).agg({
        'amount': ['sum', 'count', 'mean']
    })
    
    pivot_table = pd.pivot_table(
        df,
        values='amount',
        index='hour',
        columns='day_of_week',
        aggfunc='sum',
        fill_value=0
    )
    
    print("\nHeatmap Pivot Table (Hour x Day of Week - Sum of Amount):")
    print(pivot_table)

    # Export final dataset
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/processed/datetime_features.csv', index=False)
    print("\n✓ Processed data saved to data/processed/datetime_features.csv")
    
    # Testing Output Requirements
    print("\n--- PIPELINE TESTS ---")
    print(f"Min date: {df['transaction_date'].min()}")
    print(f"Max date: {df['transaction_date'].max()}")
    print(f"Days in dataset: {(df['transaction_date'].max() - df['transaction_date'].min()).days}")
    print(f"Hours with data: {sorted(df['hour'].unique())}")
    print(f"Weeks in dataset: {df['week_num'].nunique()}")

if __name__ == "__main__":
    run_datetime_pipeline()