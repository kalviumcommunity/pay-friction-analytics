import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Create output directory for the HTML files
os.makedirs("interactive_charts", exist_ok=True)

print("Generating Chart 1: Revenue Trend...")
dates = [datetime.today() - timedelta(days=x) for x in range(30)]
dates.reverse()
trend_df = pd.DataFrame({
    'date': dates,
    'revenue': np.random.normal(5000, 1000, 30).round(0)
})

fig1 = go.Figure(data=go.Scatter(
    x=trend_df['date'],
    y=trend_df['revenue'],
    mode='lines+markers',
    hovertemplate=(
        '<b>%{x|%Y-%m-%d}</b><br>'
        'Revenue: $%{y:,.0f}<br>'
        '<extra></extra>' # Hides the secondary trace box
    ),
    line=dict(color='#1f77b4', width=2),
    marker=dict(size=8)
))

fig1.update_layout(
    title='Daily Revenue Trend (30 Days)',
    xaxis_title='Date',
    yaxis_title='Revenue ($)',
    hovermode='x unified', # Shows a vertical line connecting points
    height=500
)
fig1.write_html('interactive_charts/chart1_revenue_trend.html')


print("Generating Chart 2: Multi-Column Hover...")
prod_df = pd.DataFrame({
    'Product': ['Laptop Pro', 'Wireless Mouse', 'Mechanical Keyboard', '4K Monitor'],
    'Revenue': [125000, 15000, 45000, 85000],
    'OrderCount': [125, 600, 300, 212],
    'AOV': [1000, 25, 150, 400]
})

fig2 = go.Figure(data=go.Bar(
    x=prod_df['Product'],
    y=prod_df['Revenue'],
    marker_color='#2ca02c',
    # customdata allows us to pass extra columns to the hovertemplate
    customdata=np.stack((prod_df['OrderCount'], prod_df['AOV']), axis=-1),
    hovertemplate=(
        '<b>%{x}</b><br>'
        'Total Revenue: $%{y:,.0f}<br>'
        'Orders: %{customdata[0]:,}<br>'
        'Avg Order Value (AOV): $%{customdata[1]:,.2f}'
        '<extra></extra>'
    )
))

fig2.update_layout(title='Product Performance with Deep Insights', height=500)
fig2.write_html('interactive_charts/chart2_product_hover.html')


print("Generating Chart 3: Dropdown Filter...")
products = ['Product A', 'Product B', 'Product C', 'Product D']
revenue_data = [50000, 75000, 120000, 45000]
profit_data = [15000, 22000, 35000, 10000]
order_count = [1000, 1500, 2500, 800]

fig3 = go.Figure()

# Add all 3 traces. Only the first one is visible by default.
fig3.add_trace(go.Bar(x=products, y=revenue_data, name='Revenue', marker=dict(color='#1f77b4'), visible=True))
fig3.add_trace(go.Bar(x=products, y=profit_data, name='Profit', marker=dict(color='#ff7f0e'), visible=False))
fig3.add_trace(go.Bar(x=products, y=order_count, name='Order Count', marker=dict(color='#2ca02c'), visible=False))

fig3.update_layout(
    updatemenus=[dict(
        active=0,
        x=0.01, xanchor='left',
        y=1.15, yanchor='top',
        buttons=[
            dict(label='Revenue', method='update', args=[{'visible': [True, False, False]}, {'title': 'Revenue by Product'}]),
            dict(label='Profit', method='update', args=[{'visible': [False, True, False]}, {'title': 'Profit by Product'}]),
            dict(label='Order Count', method='update', args=[{'visible': [False, False, True]}, {'title': 'Order Count by Product'}])
        ]
    )],
    title='Revenue by Product',
    height=500
)
fig3.write_html('interactive_charts/chart3_metric_selector.html')


print("Generating Chart 4: Interactive Scatter Plot...")
np.random.seed(42)
scatter_df = pd.DataFrame({
    'Marketing_Spend': np.random.uniform(100, 5000, 200),
    'Revenue_Generated': np.random.uniform(200, 15000, 200)
})

fig4 = go.Figure(data=go.Scatter(
    x=scatter_df['Marketing_Spend'],
    y=scatter_df['Revenue_Generated'],
    mode='markers',
    marker=dict(size=10, color='#9467bd', opacity=0.7, line=dict(width=1, color='white')),
    hovertemplate='Spend: $%{x:,.0f}<br>Revenue: $%{y:,.0f}<extra></extra>'
))

# Explicitly setting dragmode to 'zoom' (though it is the default)
fig4.update_layout(
    title='Campaign ROI (Click & Drag to Zoom, Double-Click to Reset, Shift+Drag to Pan)',
    xaxis_title='Marketing Spend ($)',
    yaxis_title='Revenue Generated ($)',
    dragmode='zoom', 
    hovermode='closest',
    height=600
)
fig4.write_html('interactive_charts/chart4_interactive.html')

print("✅ All standalone HTML charts generated successfully in 'interactive_charts/'!")