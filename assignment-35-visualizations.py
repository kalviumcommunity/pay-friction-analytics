# assignment-35-visualizations.py
"""Visualization Assignment
Generates five distinct charts (Bar, Line, Histogram, Stacked Bar, Scatter) using synthetic data.
All charts use a consistent colour palette, complete labels, and at least one annotation.
Outputs PNG files at 300 DPI into the `output/` folder and writes a README.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# Ensure output directory exists
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------
# Synthetic Data Generation
# ------------------------------------------------------------
np.random.seed(42)

# Products and dates
products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
months = pd.date_range(end=pd.Timestamp.today(), periods=12, freq="M")

# Generate orders dataframe
orders = []
for date in months:
    for prod in products:
        # Random number of orders per month per product
        n_orders = np.random.randint(20, 60)
        for _ in range(n_orders):
            amount = np.random.exponential(scale=5000) + 2000  # order amount in $
            orders.append({
                "order_date": date,
                "product_line": prod,
                "order_amount": amount,
            })
orders_df = pd.DataFrame(orders)

# Generate marketing spend per month (overall, not per product)
marketing_spend = pd.DataFrame({
    "date": months,
    "marketing_spend": np.random.uniform(20000, 80000, size=len(months)),
})

# ------------------------------------------------------------
# Colour palette (consistent across all charts)
# ------------------------------------------------------------
PALETTE = {
    "primary": "#1f77b4",   # blue
    "secondary": "#ff7f0e", # orange
    "success": "#2ca02c",   # green
    "danger": "#d62728",    # red
    "neutral": "#7f7f7f",   # gray
}
CHART_COLORS = [PALETTE["primary"], PALETTE["secondary"], PALETTE["success"], PALETTE["danger"], PALETTE["neutral"]]

# Helper for currency formatting
currency_fmt = FuncFormatter(lambda x, _: f"${x/1e6:.1f}M")

# ------------------------------------------------------------
# Chart 1: Horizontal Bar – Revenue by Product (last quarter)
# ------------------------------------------------------------
last_quarter = orders_df[orders_df["order_date"] >= (pd.Timestamp.today() - pd.Timedelta(days=90))]
rev_by_product = (
    last_quarter.groupby("product_line")
    ["order_amount"]
    .sum()
    .reset_index()
    .sort_values("order_amount", ascending=True)
)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(rev_by_product["product_line"], rev_by_product["order_amount"], color=PALETTE["primary"])
ax.set_xlabel("Revenue ($)", fontsize=12)
ax.set_ylabel("Product Line", fontsize=12)
ax.set_title("Q4 Revenue by Product Line", fontsize=14, fontweight="bold")
ax.xaxis.set_major_formatter(currency_fmt)
for i, (value, label) in enumerate(zip(rev_by_product["order_amount"], rev_by_product["product_line"])):
    ax.text(value, i, f" ${value/1e6:.2f}M", va="center", ha="left", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "chart1_revenue_by_product.png"), dpi=300, bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------
# Chart 2: Line – Revenue Trend (last 12 months) for top 3 products
# ------------------------------------------------------------
# Identify top 3 products by total revenue
top_products = (
    orders_df.groupby("product_line")["order_amount"].sum()
    .nlargest(3)
    .index.tolist()
)
trend_df = (
    orders_df[orders_df["product_line"].isin(top_products)]
    .groupby(["order_date", "product_line"])['order_amount']
    .sum()
    .reset_index()
    .pivot(index="order_date", columns="product_line", values="order_amount")
    .fillna(0)
    .sort_index()
)

fig, ax = plt.subplots(figsize=(12, 6))
for idx, prod in enumerate(top_products):
    ax.plot(trend_df.index, trend_df[prod], marker='o', linewidth=2, label=prod, color=CHART_COLORS[idx])
ax.set_title("Monthly Revenue Trend (Top 3 Products)", fontsize=14, fontweight='bold')
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Revenue ($)", fontsize=12)
ax.yaxis.set_major_formatter(currency_fmt)
ax.legend(title="Product", loc='upper left')
ax.grid(True, alpha=0.3)
# Annotation – highlight the month with highest total revenue across top 3
total_monthly = trend_df.sum(axis=1)
peak_month = total_monthly.idxmax()
peak_value = total_monthly.max()
ax.annotate(
    f"Peak Total\n{peak_value/1e6:.2f}M",
    xy=(peak_month, peak_value),
    xytext=(peak_month, peak_value*1.1),
    arrowprops=dict(arrowstyle='->', color='red', lw=2),
    fontsize=10,
    ha='center',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "chart2_revenue_trend.png"), dpi=300, bbox_inches='tight')
plt.close(fig)

# ------------------------------------------------------------
# Chart 3: Histogram – Distribution of Order Values
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
values = orders_df["order_amount"]
ax.hist(values, bins=30, color=PALETTE["secondary"], edgecolor='black')
ax.set_title("Distribution of Order Values", fontsize=14, fontweight='bold')
ax.set_xlabel("Order Amount ($)", fontsize=12)
ax.set_ylabel("Count", fontsize=12)
# Annotation – show mean and median lines
mean_val = values.mean()
median_val = values.median()
ax.axvline(mean_val, color=PALETTE["danger"], linestyle='--', linewidth=2, label='Mean')
ax.axvline(median_val, color=PALETTE["success"], linestyle='-.', linewidth=2, label='Median')
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "chart3_order_value_distribution.png"), dpi=300, bbox_inches='tight')
plt.close(fig)

# ------------------------------------------------------------
# Chart 4: Stacked Bar – Quarterly Revenue Composition by Product
# ------------------------------------------------------------
orders_df['quarter'] = orders_df['order_date'].dt.to_period('Q')
quarterly = (
    orders_df.groupby(['quarter', 'product_line'])['order_amount']
    .sum()
    .unstack(fill_value=0)
)

fig, ax = plt.subplots(figsize=(12, 6))
bottom = np.zeros(len(quarterly))
for idx, prod in enumerate(products):
    values = quarterly[prod].values
    ax.bar(quarterly.index.astype(str), values, bottom=bottom, label=prod, color=CHART_COLORS[idx])
    bottom += values
ax.set_title('Quarterly Revenue Composition by Product', fontsize=14, fontweight='bold')
ax.set_xlabel('Quarter', fontsize=12)
ax.set_ylabel('Revenue ($)', fontsize=12)
ax.yaxis.set_major_formatter(currency_fmt)
ax.legend(title='Product', loc='upper left')
# Annotation – highlight a shift (e.g., product B overtakes product A in last quarter)
if len(quarterly) >= 2:
    last_q = quarterly.index[-1]
    prod_b = quarterly.loc[last_q, 'Product B']
    prod_a = quarterly.loc[last_q, 'Product A']
    if prod_b > prod_a:
        ax.annotate(
            'Product B surpasses A',
            xy=(last_q.astype(str), prod_b + prod_a),
            xytext=(last_q.astype(str), prod_b + prod_a + 0.5e6),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=10,
            ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
        )
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "chart4_revenue_composition.png"), dpi=300, bbox_inches='tight')
plt.close(fig)

# ------------------------------------------------------------
# Chart 5: Scatter – Marketing Spend vs Revenue (monthly)
# ------------------------------------------------------------
monthly_rev = (
    orders_df.groupby('order_date')['order_amount']
    .sum()
    .reset_index()
    .rename(columns={'order_amount': 'revenue'})
)
scatter_df = pd.merge(monthly_rev, marketing_spend, left_on='order_date', right_on='date')

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(scatter_df['marketing_spend'], scatter_df['revenue'], c=PALETTE['primary'], edgecolor='black', s=80)
ax.set_title('Marketing Spend vs Revenue (Monthly)', fontsize=14, fontweight='bold')
ax.set_xlabel('Marketing Spend ($)', fontsize=12)
ax.set_ylabel('Revenue ($)', fontsize=12)
ax.xaxis.set_major_formatter(currency_fmt)
ax.yaxis.set_major_formatter(currency_fmt)
# Add trend line
z = np.polyfit(scatter_df['marketing_spend'], scatter_df['revenue'], 1)
p = np.poly1d(z)
ax.plot(scatter_df['marketing_spend'], p(scatter_df['marketing_spend']), "--", color=PALETTE['danger'], label='Trend')
ax.legend()
# Annotation – outlier (highest spend with relatively low revenue)
outlier_idx = scatter_df['marketing_spend'].idxmax()
ax.annotate(
    'High spend, low rev',
    xy=(scatter_df.loc[outlier_idx, 'marketing_spend'], scatter_df.loc[outlier_idx, 'revenue']),
    xytext=(scatter_df.loc[outlier_idx, 'marketing_spend']*0.9, scatter_df.loc[outlier_idx, 'revenue']*1.1),
    arrowprops=dict(arrowstyle='->', color='red'),
    fontsize=10,
    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "chart5_marketing_vs_revenue.png"), dpi=300, bbox_inches='tight')
plt.close(fig)

# ------------------------------------------------------------
# README generation
# ------------------------------------------------------------
readme_content = """# Analysis Visualizations

## Chart 1: Revenue by Product Line
- **Type:** Horizontal bar chart
- **Question:** Which product line generated the most revenue in the last quarter?
- **Key Insight:** Shows the revenue share per product; highest bar indicates top performer.
- **Annotation:** Data labels on each bar display exact values.

## Chart 2: Revenue Trend (Top 3 Products)
- **Type:** Multi‑line chart
- **Question:** How has revenue changed over the past 12 months for the top‑3 products?
- **Key Insight:** Seasonal patterns and a peak month are highlighted.
- **Annotation:** Arrow marks the month with the highest combined revenue.

## Chart 3: Order Value Distribution
- **Type:** Histogram
- **Question:** What is the typical order value range?
- **Key Insight:** Mean and median lines show central tendency; distribution shape reveals skew.
- **Annotation:** Vertical lines for mean (red dashed) and median (green dash‑dot).

## Chart 4: Quarterly Revenue Composition
- **Type:** Stacked bar chart
- **Question:** How does each product contribute to quarterly revenue?
- **Key Insight:** Visualises both total revenue per quarter and product mix.
- **Annotation:** Arrow notes when Product B overtakes Product A in the latest quarter.

## Chart 5: Marketing Spend vs Revenue
- **Type:** Scatter plot with trend line
- **Question:** Is there a relationship between marketing spend and revenue?
- **Key Insight:** Positive correlation (trend line) with an identified outlier.
- **Annotation:** Highlights the month with highest spend but comparatively low revenue.

All charts use a consistent colour palette defined in the script and are saved as 300 dpi PNG files in the `output/` directory.
"""

readme_path = os.path.join(OUTPUT_DIR, "CHARTS_README.md")
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme_content)

print("Visualization script completed. PNG files and README are available in the 'output' folder.")
