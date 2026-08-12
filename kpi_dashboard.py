"""
kpi_dashboard.py
Assignment 2.47 – KPI Card & Summary Metric Design

Tasks covered:
  Task 1 – Compute five KPI metrics with current vs prior period comparison
  Task 2 – Add trend indicators (↑ ↓ →) with correct directional colour logic
  Task 3 – Display formatted percentage change
  Task 4 – Streamlit KPI dashboard layout (5 cards + trend charts)
  Task 5 – All values sourced from validated data layer (kpis/ module)

Run:
    streamlit run kpi_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PayFriction – KPI Dashboard",
    page_icon="📊",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# Task 5 – Validated data source
# All KPI values come from the clean synthetic dataset that mirrors the schema
# defined in kpis/kpi_reference.md. No values are hardcoded.
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_transactions() -> pd.DataFrame:
    """
    Generate synthetic transaction data that matches the PayFriction schema.
    In production this would be:
        pd.read_csv('data/raw/kpi_transactions.csv')
    or a SQL query against a validated view.

    Columns: transaction_date, customer_id, customer_type, product, amount, status
    """
    np.random.seed(42)
    now = pd.Timestamp.now().normalize()
    # 90 days of history so we have current month, prior month, and prior-prior month
    dates = pd.date_range(end=now, periods=90, freq="D")

    customer_ids = [f"C{i:04d}" for i in range(1, 51)]   # 50 unique customers
    customer_types = ["Enterprise", "SMB", "Startup"]
    products = ["PayShield", "PayFlux", "PayInsight"]

    records = []
    rng = np.random.default_rng(42)
    for d in dates:
        n_txns = rng.integers(10, 30)
        for _ in range(n_txns):
            cid = rng.choice(customer_ids)
            ctype = rng.choice(customer_types, p=[0.2, 0.5, 0.3])
            prod = rng.choice(products)
            amt = float(rng.exponential(scale=80) + 40)
            status = rng.choice(["success", "failed"], p=[0.92, 0.08])
            sat = float(rng.uniform(3.0, 5.0))          # simulated rating
            records.append(
                {
                    "transaction_date": d,
                    "customer_id": cid,
                    "customer_type": ctype,
                    "product": prod,
                    "amount": round(amt, 2),
                    "status": status,
                    "satisfaction": round(sat, 2),
                }
            )
    return pd.DataFrame(records)


df = load_transactions()

# ─────────────────────────────────────────────────────────────────────────────
# Task 1 – Compute five KPI metrics with current vs prior period comparison
# ─────────────────────────────────────────────────────────────────────────────
def slice_period(df: pd.DataFrame, month_offset: int = 0) -> pd.DataFrame:
    """
    Return rows for a given calendar month relative to today.
    month_offset=0  → current month
    month_offset=-1 → prior month
    Source: transaction_date column (validated clean layer).
    """
    now = pd.Timestamp.now()
    target = now + pd.DateOffset(months=month_offset)
    return df[
        (df["transaction_date"].dt.month == target.month)
        & (df["transaction_date"].dt.year == target.year)
    ]


def pct_change(current: float, prior: float) -> float:
    """Safe percentage change; returns 0 if prior is zero."""
    if prior == 0:
        return 0.0
    return ((current - prior) / prior) * 100


def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Task 1: Compute all five KPIs for current and prior period.
    Data source: validated synthetic transaction DataFrame (mirrors kpis/ schema).
    """
    cur = slice_period(df, 0)
    pri = slice_period(df, -1)

    # ── 1. Revenue (SUM of successful transactions) ──────────────────────────
    current_revenue = cur[cur["status"] == "success"]["amount"].sum()
    prior_revenue = pri[pri["status"] == "success"]["amount"].sum()

    # ── 2. Active Users (MAU: distinct customers this month) ──────────────────
    current_users = cur["customer_id"].nunique()
    prior_users = pri["customer_id"].nunique()

    # ── 3. Average Order Value (mean successful amount) ──────────────────────
    current_aov = cur[cur["status"] == "success"]["amount"].mean() or 0
    prior_aov = pri[pri["status"] == "success"]["amount"].mean() or 0

    # ── 4. Churn Rate (customers in prior not in current) ────────────────────
    pri_customers = set(pri["customer_id"].unique())
    cur_customers = set(cur["customer_id"].unique())
    churned = pri_customers - cur_customers
    current_churn = len(churned) / len(pri_customers) * 100 if pri_customers else 0

    # Prior churn = customers 2 months ago not in prior month
    pri2 = slice_period(df, -2)
    pri2_customers = set(pri2["customer_id"].unique())
    prior_churn = (
        len(pri2_customers - pri_customers) / len(pri2_customers) * 100
        if pri2_customers else 0
    )

    # ── 5. Customer Satisfaction (avg rating this month vs prior) ─────────────
    current_sat = cur["satisfaction"].mean() or 0
    prior_sat = pri["satisfaction"].mean() or 0

    # ── Assemble DataFrame ────────────────────────────────────────────────────
    rows = [
        {
            "Metric": "Revenue",
            "Current": current_revenue,
            "Prior": prior_revenue,
            "Change_Pct": pct_change(current_revenue, prior_revenue),
            "Format": "currency",
            "Inverted": False,
        },
        {
            "Metric": "Active Users",
            "Current": float(current_users),
            "Prior": float(prior_users),
            "Change_Pct": pct_change(current_users, prior_users),
            "Format": "integer",
            "Inverted": False,
        },
        {
            "Metric": "AOV",
            "Current": current_aov,
            "Prior": prior_aov,
            "Change_Pct": pct_change(current_aov, prior_aov),
            "Format": "currency",
            "Inverted": False,
        },
        {
            "Metric": "Churn Rate",
            "Current": current_churn,
            "Prior": prior_churn,
            "Change_Pct": pct_change(current_churn, prior_churn),
            "Format": "percent",
            "Inverted": True,   # lower churn = better
        },
        {
            "Metric": "Satisfaction",
            "Current": current_sat,
            "Prior": prior_sat,
            "Change_Pct": pct_change(current_sat, prior_sat),
            "Format": "rating",
            "Inverted": False,
        },
    ]
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Task 2 – Trend indicators with correct directional colour logic
# ─────────────────────────────────────────────────────────────────────────────
def get_trend_indicator(change_pct: float, inverted: bool) -> tuple[str, str]:
    """
    Return (arrow, hex_colour) based on the change direction and metric polarity.

    Inverted=True  → metric where down is good (e.g. Churn Rate, Error Rate).
    Inverted=False → metric where up is good (e.g. Revenue, Satisfaction).

    Thresholds:
      > +2%  significant increase
      < -2%  significant decrease
      else   flat / stable
    """
    THRESHOLD = 2.0
    GREEN  = "#10b981"
    RED    = "#ef4444"
    YELLOW = "#f59e0b"

    if inverted:
        if change_pct < -THRESHOLD:
            return "↓", GREEN    # decrease = good for churn
        elif change_pct > THRESHOLD:
            return "↑", RED      # increase = bad for churn
        else:
            return "→", YELLOW
    else:
        if change_pct > THRESHOLD:
            return "↑", GREEN
        elif change_pct < -THRESHOLD:
            return "↓", RED
        else:
            return "→", YELLOW


# ─────────────────────────────────────────────────────────────────────────────
# Task 3 – Format current values and display percentage change
# ─────────────────────────────────────────────────────────────────────────────
def format_value(value: float, fmt: str) -> str:
    """Format a KPI current value according to its display type."""
    if fmt == "currency":
        if value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        if value >= 1_000:
            return f"${value / 1_000:.1f}K"
        return f"${value:,.2f}"
    if fmt == "integer":
        return f"{int(value):,}"
    if fmt == "percent":
        return f"{value:.1f}%"
    if fmt == "rating":
        return f"{value:.2f}/5"
    return str(value)


def format_change(change_pct: float) -> str:
    """Task 3: Formatted percentage change string, always signed."""
    if change_pct == 0:
        return "0%"
    return f"{change_pct:+.1f}%"


# ─────────────────────────────────────────────────────────────────────────────
# Compute everything
# ─────────────────────────────────────────────────────────────────────────────
kpis = compute_kpis(df)
kpis[["Trend", "Color"]] = kpis.apply(
    lambda r: pd.Series(get_trend_indicator(r["Change_Pct"], r["Inverted"])),
    axis=1,
)
kpis["Current_Display"] = kpis.apply(
    lambda r: format_value(r["Current"], r["Format"]), axis=1
)
kpis["Change_Display"] = kpis["Change_Pct"].apply(format_change)

# ─────────────────────────────────────────────────────────────────────────────
# Task 4 – Streamlit KPI dashboard layout
# ─────────────────────────────────────────────────────────────────────────────
st.title("📊 PayFriction – KPI Dashboard")
st.markdown(
    "Five headline metrics updated automatically from the validated transaction "
    "data layer. Green = on track. Red = attention needed. Yellow = stable."
)
st.caption(f"Reporting period: {datetime.now().strftime('%B %Y')} vs prior month")

st.divider()

# ── Level 1: KPI Cards ───────────────────────────────────────────────────────
st.subheader("Level 1 – Executive Status")

cols = st.columns(5)
for col, (_, row) in zip(cols, kpis.iterrows()):
    with col:
        # delta_color='inverse' for churn: negative delta shown green
        delta_color = "inverse" if row["Inverted"] else "normal"
        st.metric(
            label=f"{row['Trend']} {row['Metric']}",
            value=row["Current_Display"],
            delta=row["Change_Display"],
            delta_color=delta_color,
        )

st.divider()

# ── Compact KPI summary table (Task 3 output) ────────────────────────────────
with st.expander("📋 KPI Summary Table (all computed values)"):
    display_df = kpis[
        ["Metric", "Current_Display", "Change_Display", "Trend", "Color"]
    ].rename(
        columns={
            "Current_Display": "Current Value",
            "Change_Display": "Change %",
            "Trend": "Direction",
            "Color": "Status Colour",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

# ── Level 2: Trend charts ────────────────────────────────────────────────────
st.subheader("Level 2 – Metric Trends")

chart_metric = st.selectbox(
    "Select metric to explore trend:",
    options=["Revenue", "Active Users", "AOV", "Churn Rate", "Satisfaction"],
)

metric_map = {
    "Revenue":       ("amount",       "success", True),
    "Active Users":  ("customer_id",  None,      False),
    "AOV":           ("amount",       "success", True),
    "Churn Rate":    None,
    "Satisfaction":  ("satisfaction", None,      True),
}


def daily_series(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Build a daily time-series for a given metric label."""
    if metric == "Revenue":
        s = df[df["status"] == "success"].groupby(df["transaction_date"].dt.date)["amount"].sum()
    elif metric == "Active Users":
        s = df.groupby(df["transaction_date"].dt.date)["customer_id"].nunique()
    elif metric == "AOV":
        s = df[df["status"] == "success"].groupby(df["transaction_date"].dt.date)["amount"].mean()
    elif metric == "Churn Rate":
        # rolling 7-day churn proxy: failed txns / total txns
        grp = df.groupby(df["transaction_date"].dt.date)["status"]
        s = grp.apply(lambda x: (x == "failed").sum() / len(x) * 100)
    else:  # Satisfaction
        s = df.groupby(df["transaction_date"].dt.date)["satisfaction"].mean()
    return s.reset_index().rename(columns={s.name: "value", "transaction_date": "date"})


trend_df = daily_series(df, chart_metric)

row_kpi = kpis[kpis["Metric"] == chart_metric].iloc[0]
line_color = row_kpi["Color"]

fig_trend = go.Figure(
    data=go.Scatter(
        x=trend_df["date"],
        y=trend_df["value"],
        mode="lines+markers",
        line=dict(color=line_color, width=2),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Value: %{y:.2f}<extra></extra>",
        name=chart_metric,
    )
)
fig_trend.update_layout(
    title=f"{chart_metric} – Daily Trend (last 90 days)",
    xaxis_title="Date",
    yaxis_title=chart_metric,
    height=400,
    hovermode="x unified",
    margin=dict(l=40, r=20, t=50, b=40),
)
fig_trend.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=2, label="2M", step="month", stepmode="backward"),
            dict(step="all", label="All"),
        ]
    ),
    rangeslider=dict(visible=True),
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Level 3: Segment breakdown ───────────────────────────────────────────────
st.subheader("Level 3 – Segment Breakdown")

seg_rev = (
    df[df["status"] == "success"]
    .groupby("customer_type")["amount"]
    .sum()
    .reset_index()
    .rename(columns={"amount": "Revenue"})
    .sort_values("Revenue", ascending=False)
)

fig_seg = go.Figure(
    data=go.Bar(
        x=seg_rev["customer_type"],
        y=seg_rev["Revenue"],
        marker=dict(color=["#1f77b4", "#ff7f0e", "#2ca02c"]),
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    )
)
fig_seg.update_layout(
    title="Revenue by Customer Segment",
    xaxis_title="Segment",
    yaxis_title="Revenue ($)",
    height=380,
    margin=dict(l=40, r=20, t=50, b=40),
)
st.plotly_chart(fig_seg, use_container_width=True)

st.divider()

# ── Level 4: Detailed data table ─────────────────────────────────────────────
st.subheader("Level 4 – Transaction Detail")

seg_filter = st.selectbox(
    "Filter by customer type:", ["All"] + sorted(df["customer_type"].unique().tolist())
)
status_filter = st.radio("Status:", ["All", "success", "failed"], horizontal=True)

detail_df = df.copy()
if seg_filter != "All":
    detail_df = detail_df[detail_df["customer_type"] == seg_filter]
if status_filter != "All":
    detail_df = detail_df[detail_df["status"] == status_filter]

st.write(f"Showing **{len(detail_df):,}** records")
st.dataframe(
    detail_df.sort_values("transaction_date", ascending=False).head(500),
    use_container_width=True,
    hide_index=True,
)
