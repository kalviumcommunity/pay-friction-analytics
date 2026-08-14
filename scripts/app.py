import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date, timedelta
import io

# Page Configuration
st.set_page_config(
    page_title="Real-Time Executive KPI Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Real-Time Executive KPI Dashboard")
st.caption("Operational analytics dashboard powered by reactive state and cached data loading.")

# -----------------------------------------------------------------------------
# TASK 3: Apply @st.cache_data to Data Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data_from_bytes(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """
    Parses CSV or JSON file bytes into a Pandas DataFrame.
    Cached based on file content hash so re-renders are instant.
    """
    if file_name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_bytes))
    elif file_name.endswith(".json"):
        return pd.read_json(io.BytesIO(file_bytes))
    else:
        raise ValueError("Unsupported file format")

@st.cache_data
def generate_default_data() -> pd.DataFrame:
    """Generates synthetic operational data when no custom file is uploaded."""
    np.random.seed(42)
    dates = [date.today() - timedelta(days=x) for x in range(90)]
    return pd.DataFrame({
        "customer_id": [f"CUST-{1000 + i}" for i in np.random.randint(1, 150, 600)],
        "date": np.random.choice(dates, 600),
        "segment": np.random.choice(["Enterprise", "Mid-Market", "SMB", "Startup"], 600),
        "revenue": np.random.uniform(50, 5000, 600).round(2),
        "order_status": np.random.choice(["Completed", "Pending", "Cancelled"], 600, p=[0.8, 0.15, 0.05])
    })

# -----------------------------------------------------------------------------
# TASK 5: Run End-to-End Without Hardcoded Data (Upload & Dynamic Mapping)
# -----------------------------------------------------------------------------
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload custom CSV/JSON", type=["csv", "json"])

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        df = load_data_from_bytes(file_bytes, uploaded_file.name)
        st.sidebar.success(f"Loaded: `{uploaded_file.name}`")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        st.stop()
else:
    df = generate_default_data()
    st.sidebar.info("Using default operational dataset.")

# Ensure date column is standard datetime.date
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"]).dt.date

# Identify or assign column names dynamically to avoid strict hardcoding
date_col = "date" if "date" in df.columns else None
revenue_col = "revenue" if "revenue" in df.columns else (df.select_dtypes(include="number").columns[0] if len(df.select_dtypes(include="number").columns) > 0 else None)
segment_col = "segment" if "segment" in df.columns else (df.select_dtypes(include="object").columns[0] if len(df.select_dtypes(include="object").columns) > 0 else None)
customer_col = "customer_id" if "customer_id" in df.columns else df.columns[0]

if not revenue_col:
    st.error("Uploaded dataset must contain at least one numeric column for KPIs.")
    st.stop()

# -----------------------------------------------------------------------------
# FILTER CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.divider()
st.sidebar.header("🔍 Dashboard Filters")

# Reset Mechanism
if st.sidebar.button("🔄 Reset All Filters"):
    st.session_state.clear()
    st.rerun()

# 1. Date Filter
if date_col:
    min_d, max_d = df[date_col].min(), df[date_col].max()
    selected_dates = st.sidebar.date_input(
        "Date Range",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d
    )
else:
    selected_dates = None

# 2. Segment / Categorical Filter
if segment_col:
    all_segs = sorted(df[segment_col].dropna().astype(str).unique().tolist())
    selected_segs = st.sidebar.multiselect("Filter Segment", options=all_segs, default=all_segs)
else:
    selected_segs = None

# 3. Numeric Slider Filter
min_val, max_val = float(df[revenue_col].min()), float(df[revenue_col].max())
selected_range = st.sidebar.slider(
    f"{revenue_col.capitalize()} Range",
    min_value=min_val,
    max_value=max_val,
    value=(min_val, max_val)
)

# Apply Filters
filtered_df = df.copy()

if selected_dates and len(selected_dates) == 2:
    filtered_df = filtered_df[
        (filtered_df[date_col] >= selected_dates[0]) & 
        (filtered_df[date_col] <= selected_dates[1])
    ]

if selected_segs is not None:
    filtered_df = filtered_df[filtered_df[segment_col].astype(str).isin(selected_segs)]

filtered_df = filtered_df[
    (filtered_df[revenue_col] >= selected_range[0]) & 
    (filtered_df[revenue_col] <= selected_range[1])
]

# -----------------------------------------------------------------------------
# TASK 4: Handle Empty Filtered Results
# -----------------------------------------------------------------------------
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the current filter selection. Please broaden your filters or reset.")
    st.stop()

# -----------------------------------------------------------------------------
# TASK 1: Display Five Reactive KPI Metrics
# -----------------------------------------------------------------------------
total_rev = filtered_df[revenue_col].sum()
avg_val = filtered_df[revenue_col].mean()
record_count = len(filtered_df)
unique_custs = filtered_df[customer_col].nunique() if customer_col else 0

total_cells = filtered_df.shape[0] * filtered_df.shape[1]
null_cells = filtered_df.isnull().sum().sum()
data_quality = ((total_cells - null_cells) / total_cells * 100) if total_cells > 0 else 100.0

st.header("Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Revenue", f"${total_rev:,.2f}")
with col2:
    st.metric("Avg Transaction", f"${avg_val:,.2f}")
with col3:
    st.metric("Filtered Records", f"{record_count:,}")
with col4:
    st.metric("Unique Customers", f"{unique_custs:,}")
with col5:
    st.metric("Data Quality", f"{data_quality:.1f}%")

st.divider()

# -----------------------------------------------------------------------------
# TASK 2: Include Three Chart Types
# -----------------------------------------------------------------------------
st.header("Performance Visualizations")

tab1, tab2 = st.tabs(["📊 Main Overview", "🔍 Distribution Analysis"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)

    # Chart 1: Line Chart (Trend)
    with col_chart1:
        st.subheader("1. Metric Trajectory Over Time")
        if date_col:
            trend_df = filtered_df.groupby(date_col)[revenue_col].sum().reset_index()
            st.line_chart(trend_df.set_index(date_col))
        else:
            st.info("No date column detected for line chart.")

    # Chart 2: Bar Chart (Categorical Comparison)
    with col_chart2:
        st.subheader("2. Total Revenue by Segment")
        if segment_col:
            segment_df = filtered_df.groupby(segment_col)[revenue_col].sum().reset_index()
            st.bar_chart(segment_df.set_index(segment_col))
        else:
            st.info("No categorical column detected for bar chart.")

with tab2:
    # Chart 3: Plotly Histogram (Distribution)
    st.subheader("3. Transaction Value Distribution (Plotly)")
    fig = px.histogram(
        filtered_df,
        x=revenue_col,
        nbins=30,
        title=f"Distribution of {revenue_col.capitalize()} Values",
        color_discrete_sequence=["#29b5e8"]
    )
    fig.update_layout(bargap=0.1, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# Data Table View
with st.expander("📄 View Filtered Underlying Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)