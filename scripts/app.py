import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Data Ingestion & Profiling", layout="wide")
st.title("Dataset Upload & Dynamic Preview")
st.markdown("Upload your CSV or JSON data to instantly profile columns, check for nulls, and preview statistics without writing any code.")

# -----------------------------------------------------------------------------
# TASK 1 & 4: Implement File Upload & Handle Invalid Uploads Gracefully
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader("Drop your dataset here", type=["csv", "json"])

if uploaded_file is None:
    st.info("👆 Please upload a CSV or JSON file to begin analysis.")
else:
    # Safely attempt to read the file
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a CSV or JSON file.")
            st.stop()

        # Check for empty files
        if len(df) == 0:
            st.warning("The uploaded file contains headers but no data rows. Please upload a populated dataset.")
            st.stop()

    except Exception as e:
        st.error(f"Failed to read the file. Please ensure it is correctly formatted. \nError details: {e}")
        st.stop()

    st.success(f"Successfully loaded: **{uploaded_file.name}**")
    st.divider()

    # -----------------------------------------------------------------------------
    # TASK 2: Display Automatic Preview (Metadata, Rows, Summary)
    # -----------------------------------------------------------------------------
    st.header("1. Dataset Architecture")
    
    # Top-level metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", str(len(df.columns)))
    with col3:
        total_cells = df.shape[0] * df.shape[1]
        null_pct = (df.isnull().sum().sum() / total_cells) * 100
        st.metric("Global Null %", f"{null_pct:.1f}%", delta_color="inverse")

    # Dataframe preview
    st.subheader("Data Preview (First 10 Rows)")
    st.dataframe(df.head(10), use_container_width=True)

    # Column level profiling
    st.subheader("Column Profiling")
    summary = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Populated (Non-Null)": df.notnull().sum().values,
        "Missing (Null)": df.isnull().sum().values,
        "Null %": (df.isnull().sum() / len(df) * 100).round(1).values
    })
    st.dataframe(summary, use_container_width=True)
    st.divider()

    # -----------------------------------------------------------------------------
    # TASK 3: Display Basic Statistics
    # -----------------------------------------------------------------------------
    st.header("2. Descriptive Statistics")
    
    # Isolate numeric columns for describe() to prevent warnings
    numeric_df = df.select_dtypes(include="number")
    
    if not numeric_df.empty:
        st.dataframe(numeric_df.describe(), use_container_width=True)
    else:
        st.info("No numeric columns found in this dataset to generate statistics.")
    
    st.divider()

    # -----------------------------------------------------------------------------
    # TASK 5: Downstream Usage Demonstration
    # -----------------------------------------------------------------------------
    st.header("3. Quick Visual Exploration")
    st.markdown("Select any numeric column below to instantly visualize its distribution across the dataset.")
    
    if not numeric_df.empty:
        selected_col = st.selectbox("Select a metric to visualize:", numeric_df.columns.tolist())
        # We plot the top 20 most frequent values as a quick bar chart
        chart_data = df[selected_col].value_counts().head(20)
        st.bar_chart(chart_data)
    else:
        # Fallback to categorical if no numbers exist
        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()
        if categorical_cols:
            selected_col = st.selectbox("Select a category to visualize:", categorical_cols)
            st.bar_chart(df[selected_col].value_counts().head(20))