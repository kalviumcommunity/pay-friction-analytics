# Task 5: Date Range Slider for Weekly Revenue Chart

## Question
You have a time-series Plotly chart showing revenue by week.
You want to add a date range slider so users can select which weeks to view
(e.g., "show me only Q1 2024"). How would you implement this in Plotly?

---

## Answer

Plotly provides **two complementary mechanisms** for date range selection on a
time-series chart: `rangeselector` (predefined period buttons) and
`rangeslider` (drag-to-select slider). Both are applied via
`fig.update_xaxes()`.

### Approach 1 – Range Selector Buttons (Predefined Periods)

```python
import plotly.graph_objects as go
import pandas as pd

# Example: weekly revenue data
fig = go.Figure(
    data=go.Scatter(
        x=weekly_df['week_start'],
        y=weekly_df['revenue'],
        mode='lines+markers',
        hovertemplate='<b>Week of %{x|%Y-%m-%d}</b><br>Revenue: $%{y:,.0f}<extra></extra>',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8),
    )
)

fig.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1,  label='1M',  step='month', stepmode='backward'),
            dict(count=3,  label='3M',  step='month', stepmode='backward'),
            dict(count=6,  label='6M',  step='month', stepmode='backward'),
            dict(count=1,  label='YTD', step='year',  stepmode='todate'),
            dict(step='all', label='All'),
        ]
    )
)

fig.update_layout(title='Weekly Revenue – Range Selector Buttons', height=500)
fig.write_html('weekly_revenue_selector.html')
```

**When to use:** When you want to give users quick, common period shortcuts
(Last Month, Last Quarter, YTD, All). Great for executive dashboards where
the most common views are well-known.

---

### Approach 2 – Range Slider (Drag-to-Select Any Custom Range)

```python
fig.update_xaxes(
    rangeslider=dict(visible=True),
    type='date',
)

fig.update_layout(title='Weekly Revenue – Range Slider', height=500)
fig.write_html('weekly_revenue_slider.html')
```

**When to use:** When stakeholders need to select arbitrary date windows
(e.g., "show me exactly weeks 12–18"). Ideal for exploratory analysis where
the range of interest is not fixed in advance.

---

### Approach 3 – Both Combined (Best of Both Worlds)

```python
fig.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1,  label='1M',  step='month', stepmode='backward'),
            dict(count=3,  label='Q1',  step='month', stepmode='todate'),
            dict(count=6,  label='6M',  step='month', stepmode='backward'),
            dict(count=1,  label='YTD', step='year',  stepmode='todate'),
            dict(step='all', label='All'),
        ]
    ),
    rangeslider=dict(visible=True),
    type='date',
)
```

The buttons let users jump to standard periods instantly; the slider lets them
fine-tune the exact window afterwards. This is the recommended approach for
most production dashboards.

---

## Summary Table

| Approach | Best For | User Action |
|---|---|---|
| `rangeselector` buttons | Known, common periods (Q1, YTD) | One click |
| `rangeslider` | Arbitrary custom ranges | Drag handles |
| Both combined | Full flexibility | Click then fine-tune |
