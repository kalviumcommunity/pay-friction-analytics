import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def run_anomaly_detection():
    print("="*60)
    print("ANOMALY DETECTION & RISK IDENTIFICATION")
    print("="*60)
    
    # Load and prep data
    df = pd.read_csv('data/raw/daily_kpis.csv')
    df['date'] = pd.to_datetime(df['date'])
    daily_revenue = df.set_index('date')['amount']

    # ---------------------------------------------------------
    # Task 1: Threshold-Based Anomaly Detection
    # ---------------------------------------------------------
    print("\n[Task 1] Threshold-Based Alerting...")
    alert_rules = {
        'daily_revenue': {'min': 5000, 'max': 50000},
        'transaction_count': {'min': 100, 'max': 10000},
        'signup_rate': {'min': 20, 'max': 500}
    }

    # Extract the metrics for the known problem day (2026-08-15) to test thresholds
    problem_day = df[df['date'] == '2026-08-15'].iloc[0]
    test_metrics = {
        'daily_revenue': problem_day['amount'], 
        'transaction_count': problem_day['transactions'], 
        'signup_rate': problem_day['signups']
    }

    alerts = []
    for metric_name, rule in alert_rules.items():
        value = test_metrics[metric_name]
        if value < rule['min']:
            alerts.append({'metric': metric_name, 'value': value, 'threshold': rule['min'], 'direction': 'BELOW_MIN', 'severity': 'HIGH'})
        elif value > rule['max']:
            alerts.append({'metric': metric_name, 'value': value, 'threshold': rule['max'], 'direction': 'ABOVE_MAX', 'severity': 'MEDIUM'})
            
    for alert in alerts:
        print(f"⚠️ {alert['metric']} {alert['direction']}: {alert['value']} (Threshold: {alert['threshold']})")

    # ---------------------------------------------------------
    # Task 2: Statistical Anomaly Detection (Z-Score)
    # ---------------------------------------------------------
    print("\n[Task 2] Statistical Z-Score Detection (Last 30 Days)...")
    
    def detect_anomalies_zscore(series, threshold=2):
        mean = series.mean()
        std = series.std()
        z_scores = np.abs((series - mean) / std)
        anomalies = series[z_scores > threshold]
        return anomalies, z_scores

    anomalies, z_scores = detect_anomalies_zscore(daily_revenue, threshold=2)
    print(f"Detected {len(anomalies)} anomalies out of {len(daily_revenue)} days")
    
    for date, value in anomalies.items():
        print(f"  {date.strftime('%Y-%m-%d')}: ${value:,.0f} (z-score: {z_scores[date]:.2f})")

    # ---------------------------------------------------------
    # Task 3: Severity Classification
    # ---------------------------------------------------------
    print("\n[Task 3] Classifying Anomaly Severity...")
    
    def classify_severity(value, mean, std):
        z_score = abs((value - mean) / std)
        if z_score > 3: return 'CRITICAL'
        elif z_score > 2: return 'HIGH'
        elif z_score > 1.5: return 'MEDIUM'
        else: return 'LOW'

    anomaly_data = []
    mean_rev = daily_revenue.mean()
    std_rev = daily_revenue.std()
    
    for date, value in anomalies.items():
        severity = classify_severity(value, mean_rev, std_rev)
        anomaly_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'value': value,
            'z_score': round(z_scores[date], 2),
            'severity': severity
        })

    severity_df = pd.DataFrame(anomaly_data)
    print(severity_df)

    critical = severity_df[severity_df['severity'].isin(['CRITICAL', 'HIGH'])]
    print(f"\n⚠️ {len(critical)} CRITICAL/HIGH anomalies require immediate investigation.")

    # ---------------------------------------------------------
    # Task 4: Anomaly Logging and Audit Trail
    # ---------------------------------------------------------
    print("\n[Task 4] Generating Anomaly Audit Log...")
    
    anomaly_log = []
    for date, value in anomalies.items():
        severity = classify_severity(value, mean_rev, std_rev)
        anomaly_log.append({
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'anomaly_date': date.strftime('%Y-%m-%d'),
            'metric': 'daily_revenue',
            'value': value,
            'expected_range': f"{mean_rev - 2*std_rev:.0f} to {mean_rev + 2*std_rev:.0f}",
            'z_score': round(z_scores[date], 2),
            'severity': severity,
            'status': 'OPEN' 
        })

    os.makedirs('output', exist_ok=True)
    anomalies_df = pd.DataFrame(anomaly_log)
    anomalies_df.to_csv('output/anomalies_log.csv', index=False)
    print(f"✓ Logged {len(anomalies_df)} anomalies to 'output/anomalies_log.csv'")

    # ---------------------------------------------------------
    # Task 5: Visualization with Flagged Points
    # ---------------------------------------------------------
    print("\n[Task 5] Generating Visual Alert Dashboard...")
    
    fig, ax = plt.subplots(figsize=(14, 6))

    # Raw Data
    ax.plot(daily_revenue.index, daily_revenue.values, marker='o', label='Daily Revenue', color='black', linewidth=1.5)

    # 7-day Rolling Average
    rolling_avg = daily_revenue.rolling(window=7, min_periods=1).mean()
    ax.plot(rolling_avg.index, rolling_avg.values, label='7-day MA', color='green', linewidth=2)

    # Shade expected range (Mean ± 2 Standard Deviations)
    ax.fill_between(daily_revenue.index, mean_rev - 2*std_rev, mean_rev + 2*std_rev, alpha=0.15, color='blue', label='Expected Range ±2σ')

    # Highlight Anomalies
    for date, value in anomalies.items():
        ax.scatter(date, value, color='red', s=250, marker='X', zorder=5)
        ax.annotate('ANOMALY', (date, value), xytext=(0, -25), textcoords='offset points', ha='center', color='red', fontweight='bold')

    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Revenue ($)', fontweight='bold')
    ax.set_title('Daily Revenue Monitoring: Anomalies Flagged via Z-Score', fontsize=14, pad=15)
    ax.legend(loc='lower left')
    ax.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('output/anomaly_detection.png', dpi=150)
    print("✓ Saved monitoring visualization to 'output/anomaly_detection.png'")
    print("="*60)

if __name__ == "__main__":
    run_anomaly_detection()