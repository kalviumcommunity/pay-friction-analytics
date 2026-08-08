import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
import os

def run_correlation_analysis():
    # Load Data
    raw_path = 'data/raw/customer_churn_features.csv'
    df = pd.read_csv(raw_path).drop(columns=['customer_id']) # Drop ID as it shouldn't be correlated
    
    print("="*60)
    print("CORRELATION & RELATIONSHIP ANALYSIS")
    print("="*60)
    
    os.makedirs('output', exist_ok=True)
    
    # ---------------------------------------------------------
    # Task 1: Compute Pearson and Spearman Correlation
    # ---------------------------------------------------------
    print("\n[Task 1] Computing Pearson & Spearman Correlations...")
    pearson_corr = df.corr(method='pearson')
    spearman_corr = df.corr(method='spearman')
    
    comparison = pd.DataFrame({
        'Pearson (Linear)': pearson_corr['churn'],
        'Spearman (Rank/Monotonic)': spearman_corr['churn']
    }).round(3)
    
    print("\nCorrelation with Churn:")
    print(comparison)

    # ---------------------------------------------------------
    # Task 2: Visualize Correlation Heatmap
    # ---------------------------------------------------------
    print("\n[Task 2] Generating Correlation Heatmap...")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pearson_corr, annot=True, cmap='coolwarm', center=0, ax=ax, fmt=".2f", linewidths=0.5)
    ax.set_title('Feature Correlation Matrix (Pearson)')
    plt.tight_layout()
    plt.savefig('output/correlation_heatmap.png')
    print("✓ Saved heatmap to 'output/correlation_heatmap.png'")

    # ---------------------------------------------------------
    # Task 3: Identify Strongly Correlated Pairs
    # ---------------------------------------------------------
    print("\n[Task 3] Identifying Strong Relationships (|r| > 0.7)...")
    corr_flat = pearson_corr.unstack()
    strong = corr_flat[corr_flat.abs() > 0.7].sort_values(ascending=False)
    
    # Exclude self-correlation (where r == 1.0) and drop duplicates
    strong_pairs = strong[strong < 1.0].drop_duplicates().head(10)
    print("\nStrongly Correlated Pairs:")
    for (var1, var2), corr in strong_pairs.items():
        print(f"  {var1} <-> {var2}: {corr:.2f}")

    # ---------------------------------------------------------
    # Task 4: Business Interpretation (Causation vs Correlation)
    # ---------------------------------------------------------
    print("\n[Task 4] Generating Business Interpretation...")
    analysis = {
        'support_tickets <-> churn': {
            'correlation': round(pearson_corr.loc['support_tickets', 'churn'], 2),
            'possible_directions': [
                'support_tickets -> churn (customer gets frustrated by support process and leaves)',
                'churn -> support_tickets (angry customers complain right before canceling)',
                'payment_friction -> both (underlying transaction failures cause the ticket AND the churn)'
            ],
            'data_indicates': 'Likely payment_friction is the confounder; tickets are a symptom, not the root cause.',
            'action': 'Do not hide the support button. Fix the payment pipeline to reduce the underlying pain.'
        }
    }
    
    with open('output/correlation_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    print("✓ Saved business interpretation to 'output/correlation_analysis.json'")
    print(json.dumps(analysis, indent=2))

    # ---------------------------------------------------------
    # Task 5: Feature Selection Based on Correlation
    # ---------------------------------------------------------
    print("\n[Task 5] Feature Selection (Removing Redundancy)...")
    # transactions_per_month and engagement_score are almost perfectly correlated (> 0.99)
    # We drop 'engagement_score' because 'transactions_per_month' is more interpretable and actionable.
    
    print("Features before selection:", list(df.columns))
    df_features = df.drop('engagement_score', axis=1)
    print("Features after dropping redundant 'engagement_score':", list(df_features.columns))
    
    os.makedirs('data/processed', exist_ok=True)
    df_features.to_csv('data/processed/selected_features.csv', index=False)
    print("✓ Saved optimized feature set to 'data/processed/selected_features.csv'")
    print("="*60)

if __name__ == "__main__":
    run_correlation_analysis()