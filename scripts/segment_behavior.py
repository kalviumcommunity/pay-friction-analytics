import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def run_behavioral_analysis():
    # Load Data
    raw_path = 'data/raw/customer_behavior.csv'
    df = pd.read_csv(raw_path)
    
    print("="*70)
    print("BEHAVIOURAL ANALYSIS & USER SEGMENTATION")
    print("="*70)
    os.makedirs('output', exist_ok=True)
    
    # ---------------------------------------------------------
    # Task 1: Define Segments and Compute Metrics
    # ---------------------------------------------------------
    print("\n[Task 1] Computing Segment Metrics...")
    segment_metrics = df.groupby('customer_type').agg({
        'lifetime_value': 'mean',
        'churn': 'mean',
        'support_tickets': 'mean',
        'retention_days': 'mean',
        'customer_id': 'count'
    })
    
    segment_metrics.columns = ['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention', 'customer_count']
    print(segment_metrics.round(2))

    # ---------------------------------------------------------
    # Task 2: Summary Statistics Table
    # ---------------------------------------------------------
    print("\n[Task 2] Summary Statistics & Rankings...")
    segment_summary = segment_metrics.copy()
    
    # Rank 1 is highest LTV, Rank 1 is lowest churn
    segment_summary['ltv_rank'] = segment_summary['avg_ltv'].rank(ascending=False).astype(int)
    segment_summary['churn_rank'] = segment_summary['churn_rate'].rank(ascending=True).astype(int)
    
    # Formatting for readability
    segment_summary['avg_ltv_formatted'] = segment_summary['avg_ltv'].apply(lambda x: f'${x:,.0f}')
    segment_summary['churn_rate_formatted'] = segment_summary['churn_rate'].apply(lambda x: f'{x:.1%}')
    
    print(segment_summary[['avg_ltv_formatted', 'ltv_rank', 'churn_rate_formatted', 'churn_rank']])

    # ---------------------------------------------------------
    # Task 3: Visual Comparison (Heatmap)
    # ---------------------------------------------------------
    print("\n[Task 3] Generating Visual Heatmap...")
    # Normalize the data column-by-column (0 to 1) so the color scale works for both huge LTVs and tiny churn rates
    heatmap_data = segment_metrics[['avg_ltv', 'churn_rate', 'avg_tickets']].copy()
    heatmap_norm = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(heatmap_norm, annot=heatmap_data, cmap='RdYlGn_r', fmt=".2f", cbar_kws={'label': 'Normalized Scale (Red=Bad, Green=Good)'})
    plt.title('Segment Comparison (Values Annotated)')
    plt.tight_layout()
    plt.savefig('output/segment_heatmap.png')
    print("✓ Saved heatmap to 'output/segment_heatmap.png'")

    # ---------------------------------------------------------
    # Task 4: Top and Bottom Performer Analysis
    # ---------------------------------------------------------
    print("\n[Task 4] Identifying Top/Bottom Performers...")
    top_segment = segment_metrics['avg_ltv'].idxmax()
    top_value = segment_metrics.loc[top_segment, 'avg_ltv']
    
    high_churn = segment_metrics['churn_rate'].idxmax()
    best_retention = segment_metrics['avg_retention'].idxmax()
    
    performer_insights = f"""
    PERFORMANCE HIGHLIGHTS:
    HIGHEST VALUE:   {top_segment} (${top_value:,.0f})
    HIGHEST CHURN:   {high_churn} ({segment_metrics.loc[high_churn, 'churn_rate']:.1%})
    BEST RETENTION:  {best_retention} ({segment_metrics.loc[best_retention, 'avg_retention']:.0f} days)
    """
    print(performer_insights)

    # ---------------------------------------------------------
    # Task 5: Business-Facing Insights
    # ---------------------------------------------------------
    print("\n[Task 5] Generating Business-Facing Insights...")
    
    total_customers = segment_metrics['customer_count'].sum()
    
    # Dynamically build insight strings
    business_summary = "SEGMENT STRATEGY SUMMARY:\n\n"
    for segment in segment_metrics.index:
        row = segment_metrics.loc[segment]
        pct_base = (row['customer_count'] / total_customers) * 100
        
        business_summary += f"{segment} ({pct_base:.0f}% of base, ${row['avg_ltv']:,.0f} LTV, {row['churn_rate']:.1%} churn):\n"
        
        if segment == 'Enterprise':
            business_summary += "- Highest value, lowest churn.\n- Action: Maintain white-glove premium support and prioritize uptime.\n\n"
        elif segment == 'SMB':
            business_summary += "- Middle value, alarming churn risk due to friction.\n- Action: Overhaul the payment pipeline to reduce failed transactions and drop support ticket volume.\n\n"
        else: # Startup
            business_summary += "- Lowest value, moderate churn.\n- Action: Push towards self-service documentation to reduce support costs.\n\n"
            
    print(business_summary)
    
    # Save the report
    with open('output/segment_strategy.txt', 'w', encoding='utf-8') as f:
        f.write(business_summary)
    print("✓ Saved business summary to 'output/segment_strategy.txt'")
    print("="*70)

if __name__ == "__main__":
    run_behavioral_analysis()