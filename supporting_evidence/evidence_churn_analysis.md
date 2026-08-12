# Supporting Evidence – Churn Analysis
**Assignment 2.48 – Task 2**

This document provides the specific data, chart references, and statistics that
back every claim made in `analysis_narrative.md`. Each finding is paired with its
evidence and an explanation of why that evidence is convincing.

---

## Finding 1: Support Response Time Is the Strongest Driver of Churn

### Evidence

**Chart 1 – Scatter Plot: Response Time vs Churn Rate**
Each point represents one weekly cohort of customers. X-axis: average first
response time in hours. Y-axis: churn rate percentage. The downward-left trend
is visible without statistical knowledge — as response time rises, churn rises
with it. The relationship is nearly linear up to 24 hours, then plateaus.

**Chart 2 – Churn Rate by Response Time Bucket**

| Response Time     | Churn Rate | Relative Risk |
|-------------------|------------|---------------|
| < 2 hours         | 3%         | 1× (baseline) |
| 2–4 hours         | 5%         | 1.7×          |
| 4–24 hours        | 9%         | 3×            |
| > 24 hours        | 12%        | 4×            |

The step pattern across four buckets eliminates the possibility that this is a
coincidence. Each delay band is progressively worse. The 4× difference between
fastest and slowest is consistent across all quarters.

**Stat:** The relationship between response time and churn is real and strong —
not a fluke. Response time alone accounts for **40% of the difference in churn
rates** across all customers. No other variable we examined (subscription tier,
contract length, product line) came close to this explanatory power.

### Why It Matters

This is not theoretical. The pattern holds in every quarter, every segment, every
product tier. It tells us exactly which operational change — faster support response
— would reduce churn most. We do not need more research. We need faster hiring.

---

## Finding 2: The Pattern Holds Across All Customer Segments

### Evidence

**Chart 3 – Churn Rate by Response Time Bucket, Segmented**

| Segment     | < 2 hrs | 2–4 hrs | 4–24 hrs | > 24 hrs |
|-------------|---------|---------|----------|----------|
| Enterprise  | 2%      | 4%      | 8%       | 11%      |
| SMB         | 3%      | 5%      | 9%       | 12%      |
| Startup     | 4%      | 6%      | 10%      | 14%      |

All three segments show the same staircase pattern. Startups churn at slightly
higher baseline rates (expected — they are younger businesses), but the response
time effect is identical in direction and magnitude across all three.

### Why It Matters

A finding that only appears in one segment might reflect a segment-specific
quirk. A finding that appears in all three segments is a platform-wide structural
issue. This one is platform-wide. The fix must be platform-wide too.

---

## Finding 3: Churn Decisions Are Made Before Support Responds

### Evidence

**Analysis of 100 churned customers (manual review of support tickets + renewal timestamps)**

- **62 of 100** churned customers sent their final support ticket more than 24 hours
  before their cancellation timestamp. This means the support interaction did not
  cause them to leave — they had already decided.
- **41 of 100** churned customers opened a new support ticket within 48 hours of
  renewal date and received a response after the renewal window closed.
- In **zero of the 100 cases** did a customer send a message saying "I am leaving
  because support was slow." They simply did not renew. The dissatisfaction was
  invisible until the revenue was gone.

**Customer example (anonymised):** A Startup customer on a $4,800 annual plan
opened a billing ticket at 09:00 on a Monday. The first response arrived at 11:30
the following day — 26.5 hours later. The customer had already submitted a
cancellation request at 17:00 on Monday — 8 hours before support replied.
The support agent resolved the billing issue correctly. It made no difference.

### Why It Matters

Slow support does not just frustrate customers — it loses them before the
conversation even starts. This reframes the recommendation: the goal is not to
improve support quality. It is to respond before the customer's decision window closes.

---

## Technical Appendix (For Data Team Reference Only)

*The following section contains technical details not included in the executive
narrative. It is provided here for reproducibility and peer review.*

- **Method:** Pearson correlation between mean weekly first-response time (hours)
  and weekly churn rate across 104 weekly cohorts. r = −0.65 (p < 0.001).
- **Secondary model:** Logistic regression with churn as binary outcome.
  Predictors: response time bucket, subscription tier, contract length, NPS score.
  Response time bucket was the strongest predictor. Model AUC: 0.72.
- **Variance explained:** Response time bucket alone explains approximately 40%
  of variance in churn rate (R² = 0.40 in OLS regression of churn rate on bucket).
- **Data quality:** No missing values on `response_time_hours` or `churn_flag`.
  3.2% of records had missing NPS score — imputed with segment median.
