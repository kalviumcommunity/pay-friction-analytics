import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Ensure output directory exists for saving charts
os.makedirs('output', exist_ok=True)

# ---------------------------------------------------------
# Setup & Mock Data Generation
# ---------------------------------------------------------
st.set_page_config(page_title='PayFriction Analytics', layout='wide')

@st.cache_data
def load_data():
    """Generate mock payment friction data for the dashboard."""
    np.random.seed(42)
    dates = pd.date_range('2026-01-01', periods=180, freq='D')
    
    data = []
    for d in dates:
        for _ in range(np.random.randint(50, 150)):
            segment = np.random.choice(['Enterprise', 'SMB', 'Startup'], p=[0.2, 0.5, 0.3])
            amount = np.random.uniform(50, 5000) if segment == 'Enterprise' else np.random.uniform(10, 500)
            status = np.random.choice(['success', 'failed'], p=[0.92, 0.08])
            data.append({
                'date': d,
                'customer_segment': segment,
                'amount': amount,
                'status': status,
                'transaction_id': f"txn_{np.random.randint(10000, 99999)}"
            })
    return pd.DataFrame(data)

df = load_data()

st.title('💸 PayFriction Analytics Dashboard')
st.markdown("Monitor payment health, recover lost revenue, and identify friction bottlenecks.")

# ---------------------------------------------------------
# Task 1: Level 1 - Status (KPI Summary Cards)
# ---------------------------------------------------------
st.subheader("Level 1: Executive Status")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label='Total Processed Vol', value='$5.2M', delta='+12.5%')
with col2:
    st.metric(label='Payment Success Rate', value='94.2%', delta='+1.1%')
with col3:
    st.metric(label='Revenue at Risk (Friction)', value='$310k', delta='-5.2%', delta_color='inverse')
with col4:
    st.metric(label='Recovered via Retry', value='$125k', delta='+12.0%')
with col5:
    st.metric(label='Avg Recovery Time', value='4.2 hrs', delta='-1.5 hrs', delta_color='inverse')

st.divider()

# ---------------------------------------------------------
# Task 2: Level 2 - Trends (Time Series)
# ---------------------------------------------------------
st.subheader("Level 2: Friction Trends")
col_t1, col_t2 = st.columns(2)

# Chart 1: Revenue at Risk Trend
monthly_risk = df[df['status'] == 'failed'].set_index('date').resample('ME')['amount'].sum()
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(monthly_risk.index.strftime('%b'), monthly_risk.values / 1000, marker='o', linewidth=2, color='#d62728')
ax1.set_title('Monthly Revenue at Risk ($K)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Revenue ($K)')
ax1.axhline(y=monthly_risk.mean() / 1000, color='grey', linestyle='--', label='6-Mo Average')
ax1.legend()
ax1.grid(True, alpha=0.3)
col_t1.pyplot(fig1)
fig1.savefig('output/revenue_risk_trend.png', dpi=150)

# Chart 2: Success vs Failure Volume (Dual Line)
daily_vol = df.groupby(['date', 'status']).size().unstack(fill_value=0).resample('W').sum()
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(daily_vol.index, daily_vol['success'], label='Successful', color='#2ca02c', linewidth=2)
ax2.plot(daily_vol.index, daily_vol['failed'], label='Failed', color='#d62728', linewidth=2)
ax2.set_title('Weekly Transaction Volume (Success vs Failed)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Transaction Count')
ax2.legend()
ax2.grid(True, alpha=0.3)
col_t2.pyplot(fig2)
fig2.savefig('output/transaction_volume_trend.png', dpi=150)

st.divider()

# ---------------------------------------------------------
# Task 3: Level 3 - Segments (Comparison)
# ---------------------------------------------------------
st.subheader("Level 3: Segment Breakdown")

failed_df = df[df['status'] == 'failed']
segment_risk = failed_df.groupby('customer_segment')['amount'].sum().sort_values()

fig3, ax3 = plt.subplots(figsize=(10, 4))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
bars = ax3.barh(segment_risk.index, segment_risk.values / 1000, color=colors)
ax3.set_xlabel('Revenue at Risk ($K)')
ax3.set_title('Revenue Leakage by Customer Segment', fontsize=12, fontweight='bold')

for bar, val in zip(bars, segment_risk.values / 1000):
    ax3.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, f'${val:,.0f}K', va='center')

st.pyplot(fig3)
fig3.savefig('output/revenue_by_segment.png', dpi=150)

st.divider()

# ---------------------------------------------------------
# Task 4: Level 4 - Progressive Disclosure (Details)
# ---------------------------------------------------------
st.subheader('Level 4: Detailed Transaction Explorer')

# Sidebar Filters
st.sidebar.header('Data Filters (Level 4)')
selected_segment = st.sidebar.selectbox('Customer Segment', ['All'] + list(df['customer_segment'].unique()))
status_filter = st.sidebar.radio('Transaction Status', ['All', 'success', 'failed'])

# Apply Filters
filtered_df = df.copy()
if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['customer_segment'] == selected_segment]
if status_filter != 'All':
    filtered_df = filtered_df[filtered_df['status'] == status_filter]

st.write(f'Showing **{len(filtered_df):,}** transaction records based on current filters.')
st.dataframe(filtered_df.sort_values('date', ascending=False).head(1000), use_container_width=True)

# Export functionality
csv = filtered_df.to_csv(index=False)
st.download_button(
    label='📥 Download Filtered Data (CSV)',
    data=csv,
    file_name='payfriction_filtered_data.csv',
    mime='text/csv'
)