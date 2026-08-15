import streamlit as st
import pandas as pd
import numpy as np
import requests
from alert_config import ALERT_THRESHOLDS

st.set_page_config(page_title="Active Monitoring Dashboard", layout="wide")
st.title("🚨 Active KPI Monitoring Dashboard")
st.markdown("This dashboard actively monitors operations and triggers alerts when metrics breach safe thresholds.")

# -----------------------------------------------------------------------------
# DATA FETCHING (Live from NestJS API)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60) # Caches data for 60 seconds so filters don't spam the API
def get_operational_data():
    try:
        # Fetch live transaction data from your backend
        response = requests.get("http://127.0.0.1:3000/api/orders")
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return pd.DataFrame()
            
        # json_normalize flattens nested objects (like customer and merchant)
        df = pd.json_normalize(data)
        
        # Map your PayFriction database schema to the dashboard's expected columns
        if 'customer.customerSegment' in df.columns:
            df['segment'] = df['customer.customerSegment']
        else:
            df['segment'] = 'Unknown'
            
        if 'amount' in df.columns:
            df['revenue'] = pd.to_numeric(df['amount'], errors='coerce')
            
        # Map payment 'FAILED' status to the 'churned' metric to keep your alerts working
        if 'status' in df.columns:
            df['churned'] = df['status'].apply(lambda x: 1 if x == 'FAILED' else 0)
            
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend API: {e}")
        return pd.DataFrame()

df = get_operational_data()

# Failsafe if the database is empty or the API is offline
if df.empty:
    st.warning("No data returned from the API. Please ensure the NestJS server is running and data is seeded.")
    st.stop()

# -----------------------------------------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 Interactive Filters")
st.sidebar.markdown("Filter the data to see alerts react dynamically.")

# Ensure we drop any NaNs before creating the multiselect options
all_segments = sorted([str(seg) for seg in df["segment"].dropna().unique().tolist()])
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
    # churn_rate now represents your Transaction Failure Rate
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

# Updated the metric labels to better fit PayFriction's context
with col1:
    st.metric("Transaction Failure Rate", f"{current_metrics['churn_rate']:.1f}%")
with col2:
    st.metric("Average Transaction Value", f"${current_metrics['avg_order_value']:.2f}")
with col3:
    st.metric("Data Quality (Null %)", f"{current_metrics['null_percentage']:.1f}%")

# Select a clean subset of columns for the table preview
display_columns = ['id', 'status', 'revenue', 'segment', 'customer.email', 'merchant.name']
available_cols = [col for col in display_columns if col in filtered_df.columns]
st.dataframe(filtered_df[available_cols].head(10), use_container_width=True)