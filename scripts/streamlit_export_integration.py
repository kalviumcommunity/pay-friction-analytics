import streamlit as st
import pandas as pd
from datetime import datetime
from export_functions import clean_data, generate_charts, export_analysis

# -----------------------------------------------------------------------------
# TASK 3: Reusable Export Function for Streamlit App
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Analysis Dashboard", layout='wide')
st.title('📈 Sales & Churn Analysis Dashboard')

# Load Data
df = clean_data()
charts = generate_charts()
summary_text = """## Analysis Report
**Key Finding:** Support speed directly impacts retention. Customers waiting >24 hours churn at 4x the rate of customers supported within 2 hours.
**Recommendation:** Enforce a strict 2-hour SLA for Enterprise accounts."""

# Render Dashboard
st.markdown(summary_text)
st.plotly_chart(charts['Support_Impact'], use_container_width=True)

st.sidebar.header('Export Options')
st.sidebar.markdown("Stakeholders can download the exact data and charts shown on this dashboard.")

# Button to trigger full export generation
if st.sidebar.button('⚙️ Generate Export Bundle'):
    with st.spinner("Generating CSV, HTML, and PDF exports..."):
        report_dir = export_analysis(df, summary_text, charts, 'output_exports')
        st.session_state['report_dir'] = report_dir
        st.sidebar.success(f"✓ Bundle generated successfully!")

# If exports exist in session state, show download buttons
if 'report_dir' in st.session_state:
    st.sidebar.markdown("---")
    
    # 1. Provide CSV Download
    csv_bytes = df.to_csv(index=False).encode()
    st.sidebar.download_button(
        label='📊 Download Data (CSV)',
        data=csv_bytes,
        file_name=f'cleaned_data_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )
    
    # 2. Provide HTML Download
    try:
        with open(f"{st.session_state['report_dir']}/interactive_report.html", 'r', encoding='utf-8') as f:
            html_bytes = f.read()
        st.sidebar.download_button(
            label='🌐 Download Report (HTML)',
            data=html_bytes,
            file_name=f'interactive_report_{datetime.now().strftime("%Y%m%d")}.html',
            mime='text/html'
        )
    except FileNotFoundError:
        pass