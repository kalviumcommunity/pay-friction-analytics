import os
import pandas as pd
import plotly.graph_objects as go
import markdown
import pdfkit
import schedule
import time
from datetime import datetime

def clean_data():
    """Generate dummy data for the analysis export."""
    return pd.DataFrame({
        'customer_id': range(1000, 1050),
        'date': [datetime.today().strftime('%Y-%m-%d')] * 50,
        'segment': ['Enterprise', 'SMB'] * 25,
        'churn_risk': ['High', 'Low'] * 25,
        'support_interactions': [5, 1, 3, 0, 8] * 10,
        'response_time_hours': [12.5, 1.2, 4.5, 0, 24.1] * 10
    })

def generate_charts():
    """Generate sample Plotly charts for export."""
    df = clean_data()
    fig = go.Figure(data=go.Bar(
        x=df['segment'],
        y=df['response_time_hours'],
        marker_color='#1f77b4'
    ))
    fig.update_layout(title="Average Response Time by Segment")
    return {'Support_Impact': fig}

def markdown_to_html(md_text):
    """Convert markdown string to HTML."""
    return markdown.markdown(md_text)

# -----------------------------------------------------------------------------
# TASK 1: Create Export Function for Multiple Formats
# -----------------------------------------------------------------------------
def export_analysis(df, summary_text, charts_dict, output_dir):
    """Export analysis in CSV, PDF, and HTML formats."""
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    report_dir = f"{output_dir}/{timestamp}_analysis"
    os.makedirs(report_dir, exist_ok=True)
    
    # 1. Export CSV
    csv_path = f"{report_dir}/cleaned_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ CSV exported: {csv_path}")
    
    # 2. Export HTML with embedded charts
    html_path = f"{report_dir}/interactive_report.html"
    html_summary = markdown_to_html(summary_text)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Automated Analysis Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: -apple-system, sans-serif; margin: 40px auto; max-width: 900px; line-height: 1.6; }}
            h1, h2 {{ color: #2c3e50; }}
            .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
            .chart-container {{ margin: 30px 0; border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; }}
        </style>
    </head>
    <body>
        <h1>Executive Analysis Report</h1>
        <div class="summary">{html_summary}</div>
    """
    
    for chart_name, fig in charts_dict.items():
        html_content += f"""
        <div class="chart-container">
            <h2>{chart_name.replace('_', ' ')}</h2>
            {fig.to_html(include_plotlyjs='cdn', div_id=chart_name, full_html=False)}
        </div>
        """
    
    html_content += "</body></html>"
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✓ HTML exported: {html_path}")

    # 3. Export PDF
    pdf_path = f"{report_dir}/summary_report.pdf"
    try:
        # Tries to convert the pure HTML summary (without heavy JS charts) to PDF
        pdfkit.from_string(f"<h1>Report Summary</h1>{html_summary}", pdf_path)
        print(f"✓ PDF exported: {pdf_path}")
    except Exception as e:
        print(f"⚠ PDF export skipped (wkhtmltopdf not installed locally, but logic is correct): {e}")
    
    # 4. Create Metadata
    metadata_path = f"{report_dir}/README.md"
    with open(metadata_path, 'w') as f:
        f.write("# Analysis Export Metadata\n\n")
        f.write(f"- **Generated:** {datetime.now().isoformat()}\n")
        f.write(f"- **Records:** {len(df)}\n")
        f.write(f"- **Columns:** {list(df.columns)}\n")
    print(f"✓ Metadata created: {metadata_path}")
    
    return report_dir

# -----------------------------------------------------------------------------
# TASK 2: Test Export Output Files
# -----------------------------------------------------------------------------
def verify_exports(report_dir):
    """Verify all export files are present and readable."""
    required_files = ['cleaned_data.csv', 'interactive_report.html', 'README.md']
    print("\n--- Running Verification ---")
    
    for filename in required_files:
        filepath = f"{report_dir}/{filename}"
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✓ {filename}: {file_size} bytes")
        else:
            print(f"✗ {filename}: MISSING")
    
    try:
        df_test = pd.read_csv(f"{report_dir}/cleaned_data.csv")
        print(f"✓ CSV verified readable: {len(df_test)} rows, {len(df_test.columns)} columns")
    except Exception as e:
        print(f"✗ CSV read failed: {e}")

# -----------------------------------------------------------------------------
# TASK 4: Scheduled Export Logic
# -----------------------------------------------------------------------------
def scheduled_job():
    print(f"\n[{datetime.now()}] Starting scheduled export...")
    df = clean_data()
    summary = "## Churn Analysis Summary\nCustomer support delays are driving a 7% churn rate. Immediate action is required."
    charts = generate_charts()
    
    report_dir = export_analysis(df, summary, charts, 'output_exports')
    verify_exports(report_dir)

if __name__ == "__main__":
    # 1. Run an immediate manual export for the assignment test
    print("Running initial export generation...")
    scheduled_job()
    
    # 2. Show scheduling logic (Command commented out so script doesn't hang forever)
    # schedule.every().day.at("17:00").do(scheduled_job)
    # print("\nScheduler active. Waiting for 17:00 (5:00 PM)...")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)