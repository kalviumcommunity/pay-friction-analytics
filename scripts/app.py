import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
from alert_config import ALERT_THRESHOLDS

st.set_page_config(page_title="Active Monitoring Dashboard", layout="wide")
st.title("🚨 Active KPI Monitoring Dashboard")
st.markdown("This dashboard actively monitors operations and triggers alerts when metrics breach safe thresholds.")

# -----------------------------------------------------------------------------
# DATA GENERATION (With deliberate anomalies to trigger alerts)
# -----------------------------------------------------------------------------
@st.cache_data
def get_operational_data():
    np.random.seed(42)
    dates = [date.today() - timedelta(days=x) for x in range(30)]
    df = pd.DataFrame({
        "date": np.random.choice(dates, 1000),
        "segment": np.random.choice(["Enterprise", "Mid-Market", "SMB", "Startup"], 1000),
        "revenue": np.random.uniform(150, 1200, 1000),
        "churned": np.random.choice([0, 1], 1000, p=[0.95, 0.05]) # Default 5% churn
    })
    
    # Inject deliberate anomalies so filters trigger specific alerts
    # 1. Startups have a dangerously high churn rate (triggers critical alert)
    df.loc[df['segment'] == 'Startup', 'churned'] = np.random.choice([0, 1], len(df[df['segment'] == 'Startup']), p=[0.85, 0.15])
    
    # 2. SMBs have very low average order value (triggers warning alert)
    df.loc[df['segment'] == 'SMB', 'revenue'] = np.random.uniform(50, 250, len(df[df['segment'] == 'SMB']))
    
    # 3. Inject deliberate nulls for Data Quality alerts
    null_indices = np.random.choice(df.index, 40, replace=False)
    df.loc[null_indices, 'revenue'] = np.nan
    
    return df

df = get_operational_data()

# -----------------------------------------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 Interactive Filters")
st.sidebar.markdown("Filter the data to see alerts react dynamically.")

all_segments = sorted(df["segment"].unique().tolist())
selected_segments = st.sidebar.multiselect("Select Segments", options=all_segments, default=all_segments)

# Apply filter
filtered_df = df[df["segment"].isin(selected_segments)]

if len(filtered_df) == 0:
    st.warning("No data matches current filters. Broaden your selection.")
    st.stop()

# -----------------------------------------------------------------------------
# METRIC COMPUTATION (Task 1)
# -----------------------------------------------------------------------------
total_cells = filtered_df.shape[0] * filtered_df.shape[1]
current_metrics = {
    "churn_rate": (filtered_df["churned"].sum() / len(filtered_df)) * 100,
    "avg_order_value": filtered_df["revenue"].mean(),
    "null_percentage": (filtered_df.isnull().sum().sum() / total_cells) * 100
}

# -----------------------------------------------------------------------------
# THRESHOLD MONITORING & ALERT DISPLAY (Tasks 2, 3, 4, 5)
# -----------------------------------------------------------------------------
st.header("System Status")
active_alerts = False

for key, config in ALERT_THRESHOLDS.items():
    val = current_metrics.get(key, 0)
    
    # Check if threshold is breached
    breached = False
    if config["direction"] == "above" and val > config["threshold"]:
        breached = True
    elif config["direction"] == "below" and val < config["threshold"]:
        breached = True
        
    if breached:
        active_alerts = True
        # Construct the detailed alert message (Task 4)
        alert_msg = f"**ALERT:** {config['metric']} is **{val:.1f}** (Threshold: {config['threshold']}). {config['message']}"
        
        # Display corresponding visual severity (Task 2)
        if config["severity"] == "critical":
            st.error(alert_msg, icon="🚨")
        else:
            st.warning(alert_msg, icon="⚠️")

if not active_alerts:
    st.success("✅ All monitored systems are operating within normal parameters.", icon="✅")

st.divider()

# -----------------------------------------------------------------------------
# DASHBOARD KPIs
# -----------------------------------------------------------------------------
st.header("Current Performance Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Customer Churn Rate", f"{current_metrics['churn_rate']:.1f}%")
with col2:
    st.metric("Average Order Value", f"${current_metrics['avg_order_value']:.2f}")
with col3:
    st.metric("Data Quality (Null %)", f"{current_metrics['null_percentage']:.1f}%")

st.dataframe(filtered_df.head(10), use_container_width=True)