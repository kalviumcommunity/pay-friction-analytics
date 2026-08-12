"""
streamlit_app.py
Task 4: Integrate Plotly Charts into a Streamlit Dashboard.
Run with:  streamlit run streamlit_app.py
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Interactive Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

# ─────────────────────────────────────────────
# Synthetic Data
# ─────────────────────────────────────────────
@st.cache_data
def load_orders():
    """Generate synthetic order data for demonstration."""
    np.random.seed(42)
    products = ["Product A", "Product B", "Product C", "Product D"]
    dates = pd.date_range(end=pd.Timestamp.today(), periods=180, freq="D")
    records = []
    for d in dates:
        for prod in products:
            n = np.random.randint(5, 20)
            for _ in range(n):
                amt = round(np.random.exponential(scale=4000) + 1500, 2)
                records.append(
                    {
                        "order_date": d,
                        "product_line": prod,
                        "amount": amt,
                        "customer_id": f"C{np.random.randint(1000, 9999)}",
                    }
                )
    return pd.DataFrame(records)


df = load_orders()

# ─────────────────────────────────────────────
# Sidebar Filters
# ─────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

min_amount = st.sidebar.slider(
    "Min Order Amount ($)",
    min_value=0,
    max_value=int(df["amount"].max()),
    value=0,
    step=100,
)

product_options = ["All"] + sorted(df["product_line"].unique().tolist())
selected_product = st.sidebar.selectbox("Product Line", product_options)

date_range = st.sidebar.date_input(
    "Date Range",
    value=[df["order_date"].min().date(), df["order_date"].max().date()],
)

# ─────────────────────────────────────────────
# Apply Filters
# ─────────────────────────────────────────────
filtered = df[df["amount"] >= min_amount].copy()
if selected_product != "All":
    filtered = filtered[filtered["product_line"] == selected_product]
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = filtered[
        (filtered["order_date"] >= start) & (filtered["order_date"] <= end)
    ]

# ─────────────────────────────────────────────
# Page Title
# ─────────────────────────────────────────────
st.title("📊 Interactive Sales Dashboard")
st.markdown(
    "Explore revenue trends, product performance, and individual orders using "
    "interactive Plotly charts. All charts support **hover**, **zoom**, **pan**, and **reset**."
)

# ─────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────
total_revenue = filtered["amount"].sum()
total_orders = len(filtered)
avg_order = filtered["amount"].mean() if total_orders else 0
unique_customers = filtered["customer_id"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
k2.metric("🛒 Total Orders", f"{total_orders:,}")
k3.metric("📦 Avg Order Value", f"${avg_order:,.2f}")
k4.metric("👥 Unique Customers", f"{unique_customers:,}")

st.divider()

# ─────────────────────────────────────────────
# Chart 1 – Revenue Trend (Line + Hover)
# ─────────────────────────────────────────────
st.subheader("📈 Daily Revenue Trend")
st.caption("Hover over any point to see exact date, revenue, and order count.")

daily = (
    filtered.groupby(filtered["order_date"].dt.date)["amount"]
    .agg(["sum", "count"])
    .reset_index()
    .rename(columns={"sum": "revenue", "count": "order_count"})
)

fig_trend = go.Figure(
    data=go.Scatter(
        x=daily["order_date"],
        y=daily["revenue"],
        mode="lines+markers",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue: $%{y:,.0f}<br>"
            "Orders: %{customdata[0]:,}<extra></extra>"
        ),
        customdata=daily[["order_count"]].values,
        line=dict(color="#1f77b4", width=2),
        marker=dict(size=6),
        name="Revenue",
    )
)
fig_trend.update_layout(
    title="Daily Revenue Trend",
    xaxis_title="Date",
    yaxis_title="Revenue ($)",
    hovermode="x unified",
    height=450,
    margin=dict(l=40, r=20, t=50, b=40),
)
fig_trend.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(step="all", label="All"),
        ]
    ),
    rangeslider=dict(visible=True),
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# Chart 2 – Product Performance Dropdown
# ─────────────────────────────────────────────
st.subheader("🛍️ Product Performance (Dropdown Filter)")
st.caption("Use the dropdown above the chart to switch between Revenue, Profit, and Order Count.")

prod_stats = (
    filtered.groupby("product_line")["amount"]
    .agg(["sum", "count", "mean"])
    .reset_index()
    .rename(columns={"sum": "revenue", "count": "order_count", "mean": "avg_order"})
)
products_list = prod_stats["product_line"].tolist()
revenue_vals = prod_stats["revenue"].tolist()
profit_vals = (prod_stats["revenue"] * 0.28).tolist()
order_vals = prod_stats["order_count"].tolist()

fig_dropdown = go.Figure()
fig_dropdown.add_trace(
    go.Bar(
        x=products_list, y=revenue_vals, name="Revenue",
        marker=dict(color="#1f77b4"), visible=True,
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    )
)
fig_dropdown.add_trace(
    go.Bar(
        x=products_list, y=profit_vals, name="Profit",
        marker=dict(color="#ff7f0e"), visible=False,
        hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>",
    )
)
fig_dropdown.add_trace(
    go.Bar(
        x=products_list, y=order_vals, name="Order Count",
        marker=dict(color="#2ca02c"), visible=False,
        hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
    )
)
fig_dropdown.update_layout(
    updatemenus=[
        dict(
            active=0,
            x=0.0, xanchor="left",
            y=1.18, yanchor="top",
            buttons=[
                dict(label="Revenue", method="update",
                     args=[{"visible": [True, False, False]}, {"title": "Revenue by Product"}]),
                dict(label="Profit", method="update",
                     args=[{"visible": [False, True, False]}, {"title": "Profit by Product"}]),
                dict(label="Order Count", method="update",
                     args=[{"visible": [False, False, True]}, {"title": "Order Count by Product"}]),
            ],
        )
    ],
    title="Revenue by Product",
    xaxis_title="Product",
    yaxis_title="Value",
    height=450,
    margin=dict(l=40, r=20, t=80, b=40),
)
st.plotly_chart(fig_dropdown, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# Chart 3 – Scatter with Zoom / Pan
# ─────────────────────────────────────────────
st.subheader("🔍 Order Amount Explorer (Zoom & Pan)")
st.caption(
    "**Click & drag** to zoom → **double-click** to reset → **shift+drag** to pan → "
    "**box/lasso** select to highlight individual orders."
)

scatter_fig = go.Figure(
    data=go.Scatter(
        x=filtered["order_date"],
        y=filtered["amount"],
        mode="markers",
        marker=dict(
            size=5,
            color=filtered["amount"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Amount ($)"),
        ),
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "Order: $%{y:,.2f}<extra></extra>"
        ),
        name="Orders",
    )
)
scatter_fig.update_layout(
    title="Orders Over Time – Interactive Exploration",
    xaxis_title="Date",
    yaxis_title="Order Amount ($)",
    dragmode="zoom",
    hovermode="closest",
    height=500,
    margin=dict(l=40, r=20, t=50, b=40),
)
st.plotly_chart(scatter_fig, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# Raw Data Table
# ─────────────────────────────────────────────
st.subheader("📋 Filtered Transaction Data")
st.write(f"Showing **{len(filtered):,}** orders ≥ ${min_amount:,}")
st.dataframe(
    filtered.sort_values("order_date", ascending=False)
    .head(500)
    .reset_index(drop=True),
    use_container_width=True,
)

csv = filtered.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=csv,
    file_name="filtered_orders.csv",
    mime="text/csv",
)
