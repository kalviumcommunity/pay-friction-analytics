import pandas as pd
import os

def run_segment_analysis():
    # Load Data
    raw_path = 'data/raw/customer_segments.csv'
    df = pd.read_csv(raw_path)
    
    print("="*70)
    print("GROUPBY AGGREGATION & SEGMENT INSIGHTS")
    print("="*70)
    
    os.makedirs('output', exist_ok=True)
    
    # ---------------------------------------------------------
    # Task 1: Single-Level GroupBy with Multiple Aggregations
    # ---------------------------------------------------------
    print("\n[Task 1] Single-Level Segment Metrics...")
    segment_metrics = df.groupby('customer_type').agg({
        'churn': 'mean',
        'revenue': 'sum',
        'customer_id': 'count',
        'support_tickets': 'mean'
    })
    
    segment_metrics.columns = ['churn_rate', 'total_revenue', 'customer_count', 'avg_support_tickets']
    print(segment_metrics.round(2))

    # ---------------------------------------------------------
    # Task 2: Multi-Level GroupBy
    # ---------------------------------------------------------
    print("\n[Task 2] Multi-Level GroupBy (Customer Type & Product)...")
    product_segment = df.groupby(['customer_type', 'product']).agg({
        'revenue': 'sum',
        'customer_id': 'count'
    })
    
    product_segment.columns = ['total_revenue', 'customer_count']
    
    # Unstack for a cleaner, matrix-like view
    product_segment_pivot = product_segment.unstack(fill_value=0)
    print(product_segment_pivot)

    # ---------------------------------------------------------
    # Task 3: Pivot Table
    # ---------------------------------------------------------
    print("\n[Task 3] Generating Pivot Table...")
    pivot = pd.pivot_table(
        df,
        values='revenue',
        index='customer_type',
        columns='product',
        aggfunc='sum',
        fill_value=0
    )
    print(pivot)

    # ---------------------------------------------------------
    # Task 4: Rank and Identify Top/Bottom Performers
    # ---------------------------------------------------------
    print("\n[Task 4] Ranking Segments...")
    # Rank segments by churn (1 = Lowest Churn)
    segment_metrics['churn_rank'] = segment_metrics['churn_rate'].rank()
    
    worst_first = segment_metrics.sort_values('churn_rate', ascending=False)
    print("\nSegments Sorted by Churn Rate (Worst First):")
    print(worst_first[['churn_rate', 'churn_rank']])
    
    # Profit/revenue contribution percentage
    segment_metrics['revenue_contribution'] = (segment_metrics['total_revenue'] / segment_metrics['total_revenue'].sum() * 100)
    print("\nRevenue Contribution by Segment:")
    print(segment_metrics[['revenue_contribution', 'churn_rate']].round(2))

    # ---------------------------------------------------------
    # Task 5: Surface Actionable Segment Insights
    # ---------------------------------------------------------
    print("\n[Task 5] Generating Actionable Insights Report...")
    insights = []
    
    for segment in segment_metrics.index:
        row = segment_metrics.loc[segment]
        
        insight = {
            'segment': segment,
            'customer_count': int(row['customer_count']),
            'churn_rate': f"{row['churn_rate']:.1%}",
            'total_revenue': f"${row['total_revenue']:,.0f}",
            'revenue_contribution': f"{row['revenue_contribution']:.1f}%",
            'action': ''
        }
        
        # Business logic for actionable interventions
        if row['churn_rate'] > 0.10:
            insight['action'] = 'HIGH PRIORITY: Churn > 10%. Investigate friction points.'
        elif row['churn_rate'] <= 0.02:
            insight['action'] = 'Healthy segment. Maintain current service level.'
        else:
            insight['action'] = 'Monitor. No immediate action needed.'
        
        insights.append(insight)
    
    insights_df = pd.DataFrame(insights)
    print("\n" + insights_df.to_string(index=False))
    
    # Export report
    insights_df.to_csv('output/segment_insights.csv', index=False)
    print("\n✓ Saved actionable insights to 'output/segment_insights.csv'")
    print("="*70)

if __name__ == "__main__":
    run_segment_analysis()