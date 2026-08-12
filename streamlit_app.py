import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="Interactive Sales Dashboard", layout='wide')
st.title('📈 Interactive Sales Dashboard')

# Generate Mock Data (Cached so it doesn't regenerate on every slider move)
@st.cache_data
def load_data():
    np.random.seed(10)
    dates = [datetime.today() - timedelta(days=x) for x in range(365)]
    return pd.DataFrame({
        'order_date': dates,
        'amount': np.random.normal(500, 150, 365).clip(min=50).round(2),
        'customer_id': np.random.randint(1000, 5000, 365)
    })

df = load_data()

# -----------------------------------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------------------------------
st.sidebar.header('Dashboard Filters')
min_amount = st.sidebar.slider('Minimum Order Amount ($)', min_value=0, max_value=1000, value=0, step=50)

# Apply Filter
filtered_df = df[df['amount'] >= min_amount]

# -----------------------------------------------------------------------------
# TASK 4: Streamlit & Plotly Integration
# -----------------------------------------------------------------------------
st.subheader(f"Showing {len(filtered_df)} orders with value >= ${min_amount}")

# Create Interactive Plotly Figure
fig = go.Figure(data=go.Scatter(
    x=filtered_df['order_date'],
    y=filtered_df['amount'],
    mode='markers',
    marker=dict(size=8, color='#ff7f0e', opacity=0.8),
    hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Order:</b> $%{y:,.2f}<extra></extra>'
))

fig.update_layout(
    title='Orders Over Time (Interact to Zoom/Pan)',
    xaxis_title='Date',
    yaxis_title='Order Amount ($)',
    height=450,
    margin=dict(l=0, r=0, t=40, b=0)
)

# Render Plotly in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Show raw data
with st.expander("View Raw Data Table"):
    st.dataframe(filtered_df.sort_values('order_date', ascending=False), use_container_width=True)

# -----------------------------------------------------------------------------
# TASK 5: Assignment Follow-Up Question Answer
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📝 Task 5: Follow-Up Question")
st.info("**Question:** How do you add a date range slider/selector to a time-series Plotly chart so users can select which weeks to view?")

st.markdown("""
To allow users to filter time-series data directly inside a Plotly chart, we use **`rangeselector`** (for quick-select buttons like "1 Month" or "YTD") and **`rangeslider`** (for visual drag-and-drop filtering).

### 1. The Code Implementation
You apply these directly to the X-axis layout configuration like this:

```python
fig.update_xaxes(
    # 1. Add quick-select buttons (1 Month, 3 Months, Year-to-Date, All)
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(step="all", label="All")
        ])
    ),
    # 2. Add the visual drag-to-select bar at the bottom
    rangeslider=dict(visible=True),
    type="date"
) At auto tendance meaning of CIRS automated X in our provide, let's say you are billing and north lication you are billing and nodes applicated let's say when you run on local machine your code works""")