# PayFriction Analytics: Dashboard Design Documentation

## Information Hierarchy Applied
1. **Level 1 (Status):** 5 Executive KPI cards. 
   - *Why:* The Finance Exec needs to know immediately if Payment Success Rate is dropping or if Revenue at Risk is spiking.
2. **Level 2 (Trends):** Monthly Revenue at Risk and Weekly Transaction Volumes.
   - *Why:* Reveals if a spike in failed payments is a one-day anomaly or a worsening systemic trend.
3. **Level 3 (Segments):** Revenue Leakage by Customer Segment (Enterprise, SMB, Startup).
   - *Why:* Directs engineering resources. If SMBs account for 80% of revenue leakage, the fix must target the SMB checkout flow.
4. **Level 4 (Detail):** Sidebar filters, paginated raw data table, and CSV export.
   - *Why:* Allows Payment Ops analysts to download the exact failed transaction IDs to investigate specific bank error codes.

## Design Principles Applied
1. **Progressive Disclosure:** Executives never have to see the raw data table unless they actively interact with the sidebar filters. The summary is visible immediately.
2. **Spatial Organization:** The most critical metric (`Total Processed Vol` and `Payment Success Rate`) sits in the top-left corner, aligning with western reading patterns.
3. **Consistent Metaphor:** Green indicates positive business outcomes (higher success, recovered revenue), while Red indicates danger (failed payments, revenue at risk). We use `delta_color='inverse'` for metrics like Churn/Risk where a "lower number" is actually a positive outcome.
4. **Context Over Numbers:** The Monthly Risk trend chart includes a dashed 6-month average line, giving instant context to whether the current month is exceptionally bad.

## Colour Palette
- **Primary:** `#1f77b4` (Blue) - Standard informational bars.
- **Success:** `#2ca02c` (Green) - Successful payments, upward positive trends.
- **Danger:** `#d62728` (Red) - Failed payments, revenue leakage.
- **Secondary:** `#ff7f0e` (Orange) - Mid-tier segments.

## Target Audience & Usage
- **Primary (Finance Exec):** Daily 30-second glance at Level 1 (KPIs) to ensure targets are met.
- **Secondary (RevOps Manager):** Weekly review of Level 2 and 3 to track retry strategy effectiveness and segment friction.
- **Tertiary (Payment Ops Analyst):** Daily heavy usage of Level 4 to filter, export, and investigate raw failed transactions.

## Data Sources
- Simulated time-series transaction data encompassing Date, Customer Segment, Transaction Amount, and Payment Status (Success/Fail).