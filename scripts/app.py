import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta

# Page Configuration
st.set_page_config(page_title="Interactive Data Explorer", layout="wide")
st.title("Interactive Data Explorer")
st.markdown("Use the sidebar widgets to filter the dataset. The charts and tables will update instantly.")

# -----------------------------------------------------------------------------
# DATA GENERATION (Cached to prevent regeneration on every filter click)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    np.random.seed(42)
    dates = [date.today() - timedelta(days=x) for x in range(100)]
    
    # Generate 500 rows of dummy data
    data = {
        "date": np.random.choice(dates, 500),
        "segment": np.random.choice(["Enterprise", "Mid-Market", "SMB", "Startup"], 500),
        "product": np.random.choice(["SaaS Basic", "SaaS Pro", "API Access"], 500),
        "revenue": np.random.uniform(100, 10000, 500).round(2)
    }
    return pd.DataFrame(data)

df = load_data()

# Convert date column to actual datetime.date for easy filtering
df["date"] = pd.to_datetime(df["date"]).dt.date

# -----------------------------------------------------------------------------
# TASK 5: Implement Filter Reset Mechanism
# -----------------------------------------------------------------------------
# We clear the session state to wipe out widget memory, then rerun the app
if st.sidebar.button("🔄 Reset Filters"):
    st.session_state.clear()
    st.rerun()

st.sidebar.header("📊 Interactive Filters")

# -----------------------------------------------------------------------------
# TASK 1 & 3: Implement 3 Widget Types with Meaningful Defaults
# -----------------------------------------------------------------------------

# Widget 1: Date Range Picker (Default: Full range)
min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="date_filter"
)

# Widget 2: Multi-select (Default: All options selected)
all_segments = sorted(df["segment"].unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Select Customer Segments",
    options=all_segments,
    default=all_segments,
    key="segment_filter"
)

# Widget 3: Slider (Default: Full revenue range)
min_rev = float(df["revenue"].min())
max_rev = float(df["revenue"].max())
selected_rev = st.sidebar.slider(
    "Revenue Range ($)",
    min_value=min_rev,
    max_value=max_rev,
    value=(min_rev, max_rev),
    step=100.0,
    key="rev_filter"
)

# -----------------------------------------------------------------------------
# TASK 2: Wire Widgets to Filter the DataFrame
# -----------------------------------------------------------------------------
# Handle the date_range tuple (it can temporarily have 1 item while user is clicking)
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date_range[0], date_range[0]

# Apply the filter chain
filtered_df = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date) &
    (df["segment"].isin(selected_segments)) &
    (df["revenue"] >= selected_rev[0]) &
    (df["revenue"] <= selected_rev[1])
]

# -----------------------------------------------------------------------------
# TASK 4: Handle Empty Filter Combinations Gracefully
# -----------------------------------------------------------------------------
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the current filter combination. Please broaden your selection or click 'Reset Filters'.")
    st.stop()

# -----------------------------------------------------------------------------
# Downstream Reactive Content
# -----------------------------------------------------------------------------
# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Records Found", f"{len(filtered_df):,} / {len(df):,}")
with col2:
    st.metric("Total Filtered Revenue", f"${filtered_df['revenue'].sum():,.2f}")
with col3:
    st.metric("Average Deal Size", f"${filtered_df['revenue'].mean():,.2f}")

st.divider()

# Reactive Charts & Tables
col_chart, col_table = st.columns([1, 1])

with col_chart:
    st.subheader("Revenue by Segment")
    # Group by segment for a reactive bar chart
    segment_rev = filtered_df.groupby("segment")["revenue"].sum()
    st.bar_chart(segment_rev)

with col_table:
    st.subheader("Filtered Dataset Preview")
    st.dataframe(filtered_df.head(15), use_container_width=True)