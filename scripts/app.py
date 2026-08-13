import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Executive Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.title(" Navigation")
page = st.sidebar.radio(
    "Select Section",
    ["Overview", "Trends", "Data Explorer"]
)

st.sidebar.divider()
st.sidebar.info("💡 **Tip:** Use sidebar controls to switch views instantly without reloading the browser.")

# -----------------------------------------------------------------------------
# PAGE 1: OVERVIEW
# -----------------------------------------------------------------------------
if page == "Overview":
    st.title("Business Overview")
    st.caption("Real-time executive health check and primary business performance metrics.")

    # Task 5: Content Above the Fold - KPI Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Total Revenue", value="$5.2M", delta="+12.5%")
    with col2:
        st.metric(label="Active Users", value="2,500", delta="+5.2%")
    with col3:
        st.metric(label="Avg Order Value", value="$45", delta="+2.1%")
    with col4:
        st.metric(label="Customer Churn", value="5.2%", delta="-2.8%", delta_color="inverse")
    with col5:
        st.metric(label="Net Promoter Score", value="72", delta="+4")

    st.divider()

    # Main Section Header
    st.header("Executive Summary")
    st.subheader("Key Performance Highlights")

    col_left, col_right = st.columns(2)
    with col_left:
        st.info("📈 **Revenue Growth:** Q4 revenue exceeded targets by 12.5%, driven by high retention in Enterprise accounts.")
    with col_right:
        st.warning("⚠️ **Churn Focus:** While churn dropped by 2.8%, support response time remains the leading risk factor.")

    # Task 2: Progressive Disclosure using Expander
    with st.expander("About These Metrics & Calculation Methodology"):
        st.write("""
        - **Total Revenue:** Sum of all completed order transactions in the current trailing 30-day window.
        - **Active Users:** Unique accounts with at least one login or transaction in the past 30 days.
        - **Customer Churn:** Percentage of paid accounts that canceled or failed to renew within the last 30 days.
        - **Delta Indicators:** Compared against the previous month's baseline.
        """)

# -----------------------------------------------------------------------------
# PAGE 2: TRENDS
# -----------------------------------------------------------------------------
elif page == "Trends":
    st.title("Trend Analysis")
    st.caption("Historical performance tracking across monthly and quarterly dimensions.")

    st.header("Revenue Trends")
    st.subheader("Monthly Revenue Trajectory (Last 12 Months)")
    
    # Placeholder layout for charts
    col_chart, col_stats = st.columns([3, 1])
    with col_chart:
        st.success("📈 *[Time-Series Plotly Chart Placeholder]* — Steady upward slope with Q4 seasonal spike.")
    with col_stats:
        st.metric("Peak Month", "December", "$620K")
        st.metric("Lowest Month", "August", "$310K")

    st.divider()

    st.header("Customer Metrics")
    st.subheader("Active Customer Growth vs Churn Rate")
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("👥 *[User Growth Chart Placeholder]* — Active user trajectory.")
    with c2:
        st.error("📉 *[Churn Trend Chart Placeholder]* — Response delay correlation.")

    with st.expander("View Seasonality Notes"):
        st.write("August revenue drop was caused by a temporary supply chain bottleneck in Electronics, since fully resolved.")

# -----------------------------------------------------------------------------
# PAGE 3: DATA EXPLORER
# -----------------------------------------------------------------------------
elif page == "Data Explorer":
    st.title("Data Explorer")
    st.caption("Filter, inspect raw data records, and download export packages.")

    st.header("Dataset Filters")
    st.subheader("Interactive Query Parameters")

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        st.selectbox("Product Line", ["All Products", "Electronics", "Home & Kitchen", "Apparel"])
    with filter_col2:
        st.selectbox("Customer Segment", ["All Segments", "Enterprise", "Mid-Market", "SMB"])
    with filter_col3:
        st.slider("Minimum Order Value ($)", 0, 1000, 100)

    st.divider()

    st.header("Raw Dataset Inspection")
    st.subheader("Filtered Output Table")

    # Mock Dataframe
    dummy_data = pd.DataFrame({
        "Order ID": [1001, 1002, 1003, 1004],
        "Product": ["Laptop Pro", "Wireless Mouse", "4K Monitor", "Mechanical Keyboard"],
        "Segment": ["Enterprise", "SMB", "Enterprise", "Mid-Market"],
        "Amount": ["$1,200", "$45", "$450", "$120"],
        "Status": ["Completed", "Completed", "Pending", "Completed"]
    })

    st.dataframe(dummy_data, use_container_width=True)

    with st.expander("Export & Download Options"):
        st.download_button(
            label="📥 Download Filtered CSV",
            data=dummy_data.to_csv(index=False),
            file_name="filtered_orders.csv",
            mime="text/csv"
        )