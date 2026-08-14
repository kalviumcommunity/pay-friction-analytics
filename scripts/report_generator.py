# scripts/report_generator.py
import pandas as pd
from datetime import datetime

def generate_report(df, report_date):
    """
    Generates a structured text report from the current analysis output.
    Contains three required sections: KPI Summary, Key Finding, and Recommended Action.
    """
    # Defensive check for empty data
    if df.empty:
        return "ERROR: No data available to generate report."

    # Metric Calculations
    revenue = df["revenue"].sum()
    customers = df["customer_id"].nunique()
    avg_order = df["revenue"].mean()

    lines = []
    lines.append("📊 WEEKLY ANALYTICS & INSIGHT REPORT")
    lines.append(f"Generated Date: {report_date}")
    lines.append("=========================================\n")
    
    # Section 1: KPI Summary
    lines.append("== 1. KPI SUMMARY ==")
    lines.append(f"Total Revenue:      ${revenue:,.2f}")
    lines.append(f"Active Customers:   {customers:,}")
    lines.append(f"Average Order:      ${avg_order:,.2f}")
    lines.append("\n")
    
    # Section 2: Key Finding
    lines.append("== 2. KEY FINDING ==")
    top_seg = df.groupby("segment")["revenue"].sum().idxmax()
    lines.append(f"Top performing customer segment: {top_seg}")
    lines.append(f"The {top_seg} segment continues to drive the highest proportion of total revenue.")
    lines.append("\n")
    
    # Section 3: Recommended Action
    lines.append("== 3. RECOMMENDED ACTION ==")
    lines.append(f"Action: Reallocate 15% of Q3 marketing budget specifically targeting the {top_seg} segment to maximize ROI and capitalize on current high-growth trends.")
    
    return "\n".join(lines)

# Built-in test block to verify output locally
if __name__ == "__main__":
    dummy_df = pd.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "segment": ["Enterprise", "SMB", "Enterprise", "Startup"],
        "revenue": [8500, 300, 12000, 1500]
    })
    print(generate_report(dummy_df, datetime.now().date()))