Product Requirements Document (PRD)

Product Name
PayFriction Analytics

1. Product Overview
PayFriction Analytics is an end-to-end analytics platform that enables finance, payment
operations, and business teams to analyze payment failures, retry behavior, and bank
response codes in one unified workspace.
The platform transforms fragmented payment data into actionable insights by distinguishing
temporary payment friction from permanent revenue loss, enabling organizations to
improve payment recovery rates and reduce lost revenue.
The solution provides a standardized, reproducible analytics environment so every team
member can execute identical analytical workflows across development, testing, and
production environments.

2. Problem Statement
Modern fintech systems generate payment data from multiple independent sources
including:
● Payment Gateway Logs
● Retry Events
● Bank Response Codes
● Transaction History
● Settlement Reports
Because these datasets exist separately, finance teams face challenges in:
● Understanding why payments fail
● Measuring payment friction
● Identifying recoverable transactions
● Quantifying permanently lost revenue

● Comparing payment gateway performance
● Optimizing retry strategies
Current analysis is manual, time-consuming, and often inconsistent across teams.

3. Objectives
Business Objectives
● Reduce revenue leakage.
● Increase successful payment recovery.
● Improve retry strategy effectiveness.
● Enable faster financial reporting.
● Standardize payment analytics.
Product Objectives
● Centralize payment analytics.
● Decode bank response codes.
● Classify payment failures.
● Provide interactive dashboards.
● Generate automated insights.
● Support reproducible analytical workflows.

4. Target Users
Primary Users
● Finance Team
● Revenue Operations
● Payment Operations
● Risk Analysts
Secondary Users
● Product Managers
● Business Intelligence Teams
● Engineering Teams
● Customer Support

5. User Stories
Finance Analyst
As a Finance Analyst,
I want to identify recoverable failed payments,
so that I can reduce revenue loss.

Payment Operations
As a Payment Operations Manager,
I want to understand retry success rates,
so that retry policies can be optimized.

Product Manager
As a Product Manager,
I want to monitor payment friction across banks,
so I can improve customer payment experience.

Executive
As a Finance Executive,
I want to see revenue leakage trends,
so I can make informed business decisions.

6. Functional Requirements

Payment Analytics Dashboard
Display
● Total Transactions
● Successful Payments
● Failed Payments
● Pending Transactions
● Retry Attempts
● Retry Success Rate
● Revenue Recovered
● Revenue Lost
● Revenue at Risk

Retry Analysis
Analyze
● Retry Count
● Retry Timeline
● Retry Success Percentage
● Average Retry Delay
● Retry Effectiveness
● Retry Distribution by Gateway

Bank Response Code Decoder
Automatically decode response codes.
Example
Response
Code

Meaning Recommendation

00 Approved Success
05 Do Not Honor Manual Review
51 Insufficient Funds Retry Later
54 Expired Card Permanent Failure
91 Issuer Unavailable Retry Automatically

Payment Friction Classification
Classify failed payments into:
Temporary Friction
● Network Timeout
● Gateway Timeout
● Bank Unavailable
● System Maintenance
● Processing Delay
Recommended Action
Retry Automatically

Permanent Failure
● Expired Card
● Invalid Card
● Closed Account
● Fraud Block
● Customer Cancellation
Recommended Action
Stop Retry
Notify Customer

Revenue Intelligence Dashboard
Display
● Recoverable Revenue
● Permanently Lost Revenue
● Revenue Leakage %
● Average Recovery Time
● Revenue by Bank
● Revenue by Payment Gateway
● Revenue by Merchant
● Revenue Trends

Bank Performance Analytics
Compare
● Approval Rate
● Failure Rate
● Retry Success
● Average Processing Time
● Revenue Impact

Failure Trend Analysis
Visualizations
● Daily Failures
● Weekly Trends
● Monthly Trends
● Failure Heatmaps
● Hourly Failure Distribution

Search & Filters
Filter by
● Date Range
● Payment Gateway
● Bank
● Merchant
● Transaction Status
● Failure Reason
● Retry Status
● Amount Range

Reporting
Generate
● Daily Reports
● Weekly Reports
● Monthly Reports
● Revenue Leakage Report

● Retry Effectiveness Report
● Bank Performance Report
Export formats
● CSV
● Excel
● PDF

7. Non-Functional Requirements
Performance
● Dashboard loads in under 2 seconds.
● Analytics queries complete within 5 seconds.
● Support over 10 million transaction records.
Availability
● 99.9% uptime.
Security
● Role-Based Access Control (RBAC)
● Audit Logging
● Encrypted Data Storage
● Secure Authentication
Scalability
● Horizontal scaling.
● Containerized deployment.
● Cloud-native architecture.

8. Dashboard Metrics
Business KPIs
● Payment Success Rate

● Payment Failure Rate
● Retry Success Rate
● Revenue Recovery Rate
● Revenue Leakage
● Recoverable Revenue
● Permanent Revenue Loss
Operational KPIs
● Gateway Performance
● Bank Performance
● Processing Time
● Retry Distribution
● Error Distribution

9. API Requirements
Transaction APIs
● Get Transactions
● Get Transaction Details
● Get Retry History
Analytics APIs
● Payment Summary
● Retry Analytics
● Revenue Analytics
● Bank Analytics
● Failure Analytics
Reporting APIs
● Generate Reports
● Export Reports
● Download Analytics

10. Database Entities
● Users
● Transactions

● Payment Attempts
● Retry Events
● Bank Response Codes
● Payment Gateways
● Banks
● Merchants
● Customers
● Analytics Reports
● Revenue Metrics
● Audit Logs

11. Success Metrics
Business Success
● 20% improvement in payment recovery.
● 25% reduction in manual reporting.
● 15% decrease in revenue leakage.
Technical Success
● Dashboard response time below 2 seconds.
● Query success rate above 99%.
● Analytics accuracy above 95%.

12. Technology Stack
Frontend
● Next.js
● React
● TypeScript
● Tailwind CSS
● Recharts
● TanStack Query
Backend
● NestJS
● PostgreSQL
● Prisma ORM
● Redis

● BullMQ
Analytics
● Python
● Pandas
● SQL
● Jupyter Notebooks
Infrastructure
● Docker
● Docker Compose
● GitHub Actions
● AWS
● NGINX

13. Future Enhancements
● AI-powered payment failure prediction.
● Intelligent retry recommendation engine.
● Payment gateway health monitoring.
● Predictive revenue forecasting.
● Customer payment behavior analysis.
● Real-time anomaly detection.
● Multi-currency analytics.
● Executive AI insights and summaries.
● Integration with ERP, accounting, and BI platforms.





## Pipeline Stages
1 - Ingestion Stage (scripts/pipeline.py): Ingests raw files from local paths or Streamlit memory buffers using @st.cache_data.

2 - Validation Stage (scripts/validate_data.py): Runs schema, data type, non-null, and minimum row count checks. Returns exit code 1 on failure to block bad CI/CD merges.

3 - Cleaning Stage: Strips null records in mandatory primary keys (customer_id, amount), filters negative transactions, and coerces datetime types.

4 - Aggregation Stage: Computes segment-level revenue sums, average order values, and record counts. Saves outputs to data/processed/.

5 - Dashboard Layer (scripts/app.py): Renders reactive layout columns, Plotly distribution charts, and interactive sidebar filter controls.

6 - Active Alerting Layer (scripts/alert_config.py): Continuously evaluates computed metrics against threshold definitions and displays visual st.error() or st.warning() banners.

7 - Delivery Layer (scripts/email_sender.py): Formats structured 3-section summaries (KPIs, Findings, Actions) and sends them via SMTP.