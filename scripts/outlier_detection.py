import pandas as pd
import numpy as np
from scipy import stats
import os

def detect_and_handle_outliers():
    # Load Data
    raw_path = 'data/raw/customer_revenue.csv'
    df = pd.read_csv(raw_path)
    
    print("="*60)
    print("OUTLIER DETECTION & HANDLING PIPELINE")
    print("="*60)
    
    # ---------------------------------------------------------
    # Task 1: Z-Score Outlier Detection (Age)
    # ---------------------------------------------------------
    print("\n[Task 1] Z-Score Detection on 'age'...")
    # Calculate Z-scores and find outliers (> 3 std dev)
    df['age_zscore'] = np.abs(stats.zscore(df['age']))
    z_outliers = df[df['age_zscore'] > 3]
    print(f"Z-score outliers found in age: {len(z_outliers)}")
    
    # ---------------------------------------------------------
    # Task 2: IQR Outlier Detection (Revenue)
    # ---------------------------------------------------------
    print("\n[Task 2] IQR Detection on 'revenue'...")
    Q1 = df['revenue'].quantile(0.25)
    Q3 = df['revenue'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df['is_outlier_iqr'] = (df['revenue'] < lower_bound) | (df['revenue'] > upper_bound)
    print(f"IQR boundaries for revenue: Lower={lower_bound:.2f}, Upper={upper_bound:.2f}")
    print(f"IQR outliers found in revenue: {df['is_outlier_iqr'].sum()}")
    
    # ---------------------------------------------------------
    # Task 3: Cap Outliers at Boundaries
    # ---------------------------------------------------------
    print("\n[Task 3] Capping Revenue Outliers...")
    print(f"Before capping: min={df['revenue'].min()}, max={df['revenue'].max()}")
    
    df['revenue_capped'] = df['revenue'].clip(lower=lower_bound, upper=upper_bound)
    
    print(f"After capping:  min={df['revenue_capped'].min():.2f}, max={df['revenue_capped'].max():.2f}")
    
    # ---------------------------------------------------------
    # Task 4: Flag Outliers with Binary Column
    # ---------------------------------------------------------
    print("\n[Task 4] Flagging Anomalies...")
    # Combine both Z-score and IQR flags into one master anomaly flag
    df['is_outlier'] = (df['is_outlier_iqr']) | (df['age_zscore'] > 3)
    
    normal = df[~df['is_outlier']]
    anomalies = df[df['is_outlier']]
    
    print(f"Normal records: {len(normal)}")
    print(f"Anomalies flagged: {len(anomalies)}")
    
    # ---------------------------------------------------------
    # Task 5: Create Cleaning Log
    # ---------------------------------------------------------
    print("\n[Task 5] Generating Audit Log...")
    cleaning_log = [
        {
            'column': 'revenue',
            'method': 'IQR',
            'action': 'cap',
            'threshold_lower': lower_bound,
            'threshold_upper': upper_bound,
            'affected_rows': int(df['is_outlier_iqr'].sum()),
            'date': pd.Timestamp.now()
        },
        {
            'column': 'age',
            'method': 'Z-Score (>3)',
            'action': 'flag',
            'threshold_lower': None,
            'threshold_upper': None,
            'affected_rows': int((df['age_zscore'] > 3).sum()),
            'date': pd.Timestamp.now()
        }
    ]
    
    os.makedirs('output', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    log_df = pd.DataFrame(cleaning_log)
    log_df.to_csv('output/cleaning_log.csv', index=False)
    
    # Save the processed dataset
    df.to_csv('data/processed/outliers_handled.csv', index=False)
    
    print("✓ Audit log saved to 'output/cleaning_log.csv'")
    print("✓ Processed data saved to 'data/processed/outliers_handled.csv'")
    print("="*60)

if __name__ == "__main__":
    detect_and_handle_outliers()