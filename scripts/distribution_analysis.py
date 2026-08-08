import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

def run_distribution_analysis():
    # Load Data
    raw_path = 'data/raw/revenue_data.csv'
    df = pd.read_csv(raw_path)
    
    print("="*60)
    print("DISTRIBUTION ANALYSIS FOR BUSINESS TRENDS")
    print("="*60)
    
    os.makedirs('output', exist_ok=True)
    
    # ---------------------------------------------------------
    # Task 1: Distribution Plots (Histogram & KDE)
    # ---------------------------------------------------------
    print("\n[Task 1] Generating Distribution Plots...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(df['revenue'], bins=15, edgecolor='black', color='skyblue')
    axes[0].set_title('Revenue Distribution (Histogram)')
    axes[0].set_xlabel('Revenue ($)')
    axes[0].set_ylabel('Count')

    # KDE
    df['revenue'].plot(kind='density', ax=axes[1], color='darkblue')
    axes[1].set_title('Revenue Distribution (KDE)')
    axes[1].set_xlabel('Revenue ($)')

    plt.tight_layout()
    plt.savefig('output/revenue_distribution.png')
    print("✓ Saved distribution plots to 'output/revenue_distribution.png'")

    # ---------------------------------------------------------
    # Task 2: Compute Skewness and Kurtosis
    # ---------------------------------------------------------
    print("\n[Task 2] Computing Skewness & Kurtosis...")
    skewness = stats.skew(df['revenue'])
    kurtosis = stats.kurtosis(df['revenue'])

    print(f"Skewness: {skewness:.2f}")
    print(f"Kurtosis: {kurtosis:.2f}")

    if abs(skewness) > 1:
        print("-> Highly skewed - use median not mean for typical customer analysis.")
    if kurtosis > 3:
        print("-> Heavy tails - expect extreme outliers.")

    # ---------------------------------------------------------
    # Task 3: Identify Abnormal Patterns (Percentiles)
    # ---------------------------------------------------------
    print("\n[Task 3] Percentile Analysis for Hidden Segments...")
    percentiles = df['revenue'].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    print(percentiles)
    
    gap = percentiles[0.9] - percentiles[0.75]
    if gap > percentiles[0.75]:
        print("-> Massive gap between 75th and 90th percentile detected. Strong indicator of multiple distinct customer tiers.")

    # ---------------------------------------------------------
    # Task 4: Compare Segment Distributions
    # ---------------------------------------------------------
    print("\n[Task 4] Segment Comparison (High vs Low Value)...")
    q75 = df['revenue'].quantile(0.75)
    q25 = df['revenue'].quantile(0.25)
    
    high_value = df[df['revenue'] > q75]
    low_value = df[df['revenue'] < q25]

    print(f"High-value (Top 25%): mean=${high_value['revenue'].mean():.0f}, median=${high_value['revenue'].median():.0f}")
    print(f"Low-value (Bottom 25%): mean=${low_value['revenue'].mean():.0f}, median=${low_value['revenue'].median():.0f}")

    # Plot Segment Comparison
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.hist(high_value['revenue'], bins=10, alpha=0.7, label='High-Value', color='orange')
    ax2.hist(low_value['revenue'], bins=10, alpha=0.7, label='Low-Value', color='blue')
    ax2.legend()
    ax2.set_title('Revenue: High vs Low Value Customers')
    ax2.set_xlabel('Revenue ($)')
    ax2.set_ylabel('Count')
    plt.tight_layout()
    plt.savefig('output/segment_comparison.png')
    print("✓ Saved segment comparison plot to 'output/segment_comparison.png'")

    # ---------------------------------------------------------
    # Task 5: Business Interpretation
    # ---------------------------------------------------------
    print("\n[Task 5] Business Interpretation...")
    interpretation = f"""
    ============================================================
    REVENUE DISTRIBUTION REPORT
    ============================================================
    Skewness: {skewness:.2f} → {"Highly right-skewed" if skewness > 1 else "Moderate/Normal"}
    Mean:   ${df['revenue'].mean():.0f}
    Median: ${df['revenue'].median():.0f}
    
    Insight: {'The mean is heavily distorted by outliers. Most customers are small; few are huge enterprise accounts.' if skewness > 1 else 'The distribution is relatively balanced.'}

    Kurtosis: {kurtosis:.2f} → {"Fat tails (extreme outliers present)" if kurtosis > 3 else "Normal tail behavior"}
    Max:    ${df['revenue'].max():.0f}
    Top 1%: ${df['revenue'].quantile(0.99):.0f}

    Business Action: {'Segment the user base into Small/SMB vs. Enterprise to prevent forecasting errors. Standard marketing should target the median ($' + str(int(df['revenue'].median())) + '), while account executives should handle the high-tier segment.' if skewness > 1 else 'A uniform go-to-market strategy is viable.'}
    ============================================================
    """
    print(interpretation)
    
    # Save the report
    with open('output/distribution_report.txt', 'w', encoding='utf-8') as f:
        f.write(interpretation)

if __name__ == "__main__":
    run_distribution_analysis()