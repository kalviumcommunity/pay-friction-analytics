import pandas as pd
import numpy as np
import time
import os

def run_vectorization_workflow():
    print("="*60)
    print("NUMPY VECTORISED COMPUTATION WORKFLOW")
    print("="*60)

    # ---------------------------------------------------------
    # Setup: Generate 1 Million Rows Dynamically
    # ---------------------------------------------------------
    print("\n[Setup] Generating 1,000,000 synthetic transaction records...")
    np.random.seed(42)
    df = pd.DataFrame({
        'customer_id': np.arange(1, 1000001),
        'revenue': np.random.uniform(10.0, 5000.0, 1000000)
    })
    print(f"Dataset shape: {df.shape}")

    # ---------------------------------------------------------
    # Task 1 & 4: Replace Loop & Time Performance Comparison
    # ---------------------------------------------------------
    print("\n[Task 1 & 4] Time Performance Comparison: Min-Max Normalization")
    
    # SLOW: Python Loop
    print("Running Python loop (this will take a few seconds)...")
    start_loop = time.time()
    rev_min = df['revenue'].min()
    rev_max = df['revenue'].max()
    normalized_loop = []
    
    for val in df['revenue']:
        normalized_loop.append((val - rev_min) / (rev_max - rev_min))
        
    loop_time = time.time() - start_loop

    # FAST: NumPy Vectorization
    print("Running NumPy vectorization...")
    start_np = time.time()
    revenue_array = df['revenue'].values
    
    normalized_np = (revenue_array - revenue_array.min()) / (revenue_array.max() - revenue_array.min())
    np_time = time.time() - start_np

    # Print Comparison
    print(f"  Loop Time:  {loop_time:.4f}s")
    print(f"  NumPy Time: {np_time:.4f}s")
    if np_time > 0:
        print(f"  Speedup:    {loop_time/np_time:.0f}x faster")

    # ---------------------------------------------------------
    # Task 2: Z-Score Normalization
    # ---------------------------------------------------------
    print("\n[Task 2] Computing Z-Score Normalization (NumPy)...")
    z_scores = (revenue_array - revenue_array.mean()) / revenue_array.std()

    # ---------------------------------------------------------
    # Task 3: Bulk Ranking/Scoring
    # ---------------------------------------------------------
    print("\n[Task 3] Computing Bulk Rankings (NumPy)...")
    # np.argsort returns the indices that would sort the array. 
    # Negative sign ensures descending order (highest revenue = Rank 1)
    rankings = np.argsort(-revenue_array)
    revenue_rank = np.empty_like(rankings)
    revenue_rank[rankings] = np.arange(1, len(rankings) + 1)

    # ---------------------------------------------------------
    # Task 5: Integrate Back to DataFrame
    # ---------------------------------------------------------
    print("\n[Task 5] Integrating Results into DataFrame...")
    df['revenue_normalized'] = normalized_np
    df['revenue_zscore'] = z_scores
    df['revenue_rank'] = revenue_rank

    print(f"\nFinal Shape: {df.shape}")
    print(f"Data Types:\n{df.dtypes}")
    
    print("\nSample Output (Top 3 customers by revenue):")
    print(df.sort_values('revenue_rank').head(3))

    # Export a small sample so we don't push a massive 1M row file to GitHub
    os.makedirs('data/processed', exist_ok=True)
    df.head(1000).to_csv('data/processed/vectorized_sample.csv', index=False)
    print("\n✓ Top 1000 records saved to data/processed/vectorized_sample.csv (for GitHub PR)")
    print("="*60)

if __name__ == "__main__":
    run_vectorization_workflow()