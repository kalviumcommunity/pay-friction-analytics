# Analysis Report Guide & Export Documentation

## What's Included in the Export Bundle

### 1. `cleaned_data.csv`
- **Purpose:** Raw, structured analysis data for stakeholders who wish to perform independent exploration in Excel or Tableau.
- **Columns:** `customer_id`, `date`, `segment`, `churn_risk`, `support_interactions`, `response_time_hours`
- **Use Case:** Finance and Operations can filter, sort, and build custom pivot tables.
- **Refresh Cycle:** Automatically updated daily at 5:00 PM via Python `schedule`.

### 2. `summary_report.pdf`
- **Purpose:** Non-technical executive summary suitable for email distribution and steering committee meetings.
- **Content:** Key findings, business impact, and specific ROI-backed recommendations.
- **Use Case:** A quick, 3-minute read for the CEO to approve budget requests.
- **Format:** Professional, static PDF.

### 3. `interactive_report.html`
- **Purpose:** The complete analytical narrative combined with dynamic Plotly visualizations.
- **Content:** Full summary text + all charts embedded natively.
- **Size:** Single, portable HTML file (No Python backend required to view).
- **Use Case:** Product managers can open this in any web browser, hover over data points for tooltips, and zoom into specific anomalies.

---

## How the Automation Works (Engineering Architecture)

1. **On-Demand Generation:** 
   Users can visit the Streamlit Dashboard and click the "Generate Export Bundle" button in the sidebar. This triggers the `export_analysis()` Python function, wrapping the current pandas dataframe, markdown summary, and Plotly dictionary into discrete files instantly.
2. **Scheduled Execution:**
   A background python script runs on a server utilizing the `schedule` library (`schedule.every().day.at("17:00")`). At 5 PM daily, it pulls fresh data, runs the analysis pipeline, formats the CSV/HTML/PDF bundle, and logs the execution size to ensure no silent failures occur.
3. **Email Delivery (Follow-up Question):**
   Once the scheduled `export_analysis()` function succeeds, a secondary function utilizing Python's `smtplib` attaches the PDF and CSV files directly to an email distribution list. It includes a brief HTML body summarizing the top 3 insights, ensuring insights reach executives proactively without them ever needing to remember to check a dashboard.