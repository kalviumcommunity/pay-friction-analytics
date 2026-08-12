# interactive_charts/generate_interactive_charts.py
"""Generate interactive Plotly charts for the assignment.
Creates four HTML files in an adjacent `output` folder:
- chart1_revenue_trend.html (line with hover)
- chart2_product_performance.html (bar with multi‑field hover)
- chart3_metric_selector.html (dropdown to toggle metrics)
- chart4_interactive.html (zoom/pan/selection example)
All charts use a consistent colour palette and synthetic data.
"""

import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

np.random.seed(123)
products = ["Product A", "Product B", "Product C", "Product D"]
dates = pd.date_range(end=pd.Timestamp.today(), periods=180, freq='D')
records = []
for d in dates:
    for prod in products:
        n = np.random.randint(5, 20)
        for _ in range(n):
            amt = np.random.exponential(scale=5000) + 2000
            records.append({"order_date": d, "product_line": prod, "amount": amt})
orders_df = pd.DataFrame(records)

# Chart 1
rev_daily = (
    orders_df.groupby(orders_df['order_date'].dt.date)['amount']
    .agg(['sum', 'count'])
    .reset_index()
    .rename(columns={'sum': 'revenue', 'count': 'order_count'})
)
fig1 = go.Figure(data=go.Scatter(
    x=rev_daily['order_date'],
    y=rev_daily['revenue'],
    mode='lines+markers',
    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Revenue: $%{y:,.0f}<br>Orders: %{customdata[0]:,}<extra></extra>',
    customdata=rev_daily[['order_count']].values,
    line=dict(color='#1f77b4', width=2),
    marker=dict(size=6)
))
fig1.update_layout(title='Daily Revenue Trend', xaxis_title='Date', yaxis_title='Revenue ($)', hovermode='x unified', height=500)
fig1.write_html(os.path.join(OUTPUT_DIR, 'chart1_revenue_trend.html'))

# Chart 2
prod_stats = (
    orders_df.groupby('product_line')['amount']
    .agg(['sum', 'count', 'mean'])
    .reset_index()
    .rename(columns={'sum': 'revenue', 'count': 'order_count', 'mean': 'avg_order'})
)
fig2 = go.Figure(data=go.Bar(
    x=prod_stats['product_line'],
    y=prod_stats['revenue'],
    hovertemplate='Product: %{x}<br>Revenue: $%{y:,.0f}<br>Orders: %{customdata[0]:,}<br>Avg Order: $%{customdata[1]:,.2f}<extra></extra>',
    customdata=prod_stats[['order_count', 'avg_order']].values,
    marker=dict(color='#ff7f0e')
))
fig2.update_layout(title='Revenue by Product', xaxis_title='Product', yaxis_title='Revenue ($)', height=500)
fig2.write_html(os.path.join(OUTPUT_DIR, 'chart2_product_performance.html'))

# Chart 3 – Dropdown
revenue_data = prod_stats['revenue'].tolist()
profit_data = (prod_stats['revenue'] * 0.30).tolist()
order_counts = prod_stats['order_count'].tolist()
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=products, y=revenue_data, name='Revenue', marker=dict(color='#1f77b4'), visible=True))
fig3.add_trace(go.Bar(x=products, y=profit_data, name='Profit', marker=dict(color='#ff7f0e'), visible=False))
fig3.add_trace(go.Bar(x=products, y=order_counts, name='Order Count', marker=dict(color='#2ca02c'), visible=False))
fig3.update_layout(
    updatemenus=[{
        'active': 0,
        'x': 0,
        'y': 1.15,
        'xanchor': 'left',
        'yanchor': 'top',
        'buttons': [
            {'label': 'Revenue', 'method': 'update', 'args': [{'visible': [True, False, False]}, {'title': 'Revenue by Product'}]},
            {'label': 'Profit', 'method': 'update', 'args': [{'visible': [False, True, False]}, {'title': 'Profit by Product'}]},
            {'label': 'Order Count', 'method': 'update', 'args': [{'visible': [False, False, True]}, {'title': 'Order Count by Product'}]},
        ]
    }]
)
fig3.update_layout(title='Revenue by Product', height=500)
fig3.write_html(os.path.join(OUTPUT_DIR, 'chart3_metric_selector.html'))

# Chart 4 – Zoom / Pan
scatter_df = orders_df.copy()
scatter_df['day_index'] = (scatter_df['order_date'] - scatter_df['order_date'].min()).dt.days
fig4 = go.Figure(data=go.Scatter(
    x=scatter_df['day_index'],
    y=scatter_df['amount'],
    mode='markers',
    marker=dict(size=5, color='#2ca02c'),
    hovertemplate='Day %{x}<br>Amount: $%{y:,.0f}<extra></extra>'
))
fig4.update_layout(title='Order Amounts Over Time (Interactive)', xaxis_title='Day Index', yaxis_title='Amount ($)', dragmode='zoom', hovermode='closest', height=600)
fig4.write_html(os.path.join(OUTPUT_DIR, 'chart4_interactive.html'))

print('Generated interactive Plotly charts in', OUTPUT_DIR)
