---
id: chart-module
title: Chart
---


The `Chart` module contains methods related to creating visualizations from sql data.

Here are some of its methods:

### Generate Chart

```python
WAII.chart.generate_chart(df, ask, sql, chart_type, tweak_history) -> ChartGenerationResponse
```

This method generates the necessary information for a plot of `plot_type` based on the provided parameters.

Parameter fields:
- `df`: A pandas dataframe containing the data to plot
- `ask`: The ask, either a question or instructions on what chart to draw and any other preferences
- `sql`: The query used to generate the data
- `chart_type`: A `chart_type` enum detailing what type of chart to draw
- `tweak_history`: (array of `ChartTweak`) We can support both asking new question, or tweaking a previous visualization. If you want to tweak the previous question, you can set this field. A `ChartTweak` object looks like:
  - `chart_spec`: The previously drawn visualization
  - `ask`: The previous question you asked.
**Examples:**
    
**Draw a new visualization:**

```python
from waii_sdk_py.query import RunQueryRequest
query = None
run_query_response = WAII.query.run(RunQueryRequest(ask=query))
>>> chart = WAII.chart.generate_chart(df=run_query_response.to_pandas_df(), 
                                      ask="Draw a bar graph",
                                      sql=query,
                                      chart_type=ChartType.METABASE)
```

**Ask a follow-up question:**
```python
>>> WAII.chart.generate_chart(df=run_query_response.to_pandas_df(), 
                              ask="Title the graph trends per year, sort by year order descending",
                              sql=query,
                              chart_type=ChartType.METABASE,
                              tweak_history=[ChartTweak(ask="Draw a bar graph", chart_spec=chart.chart_spec)])
```
