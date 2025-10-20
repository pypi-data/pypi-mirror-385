import plotly.graph_objects as go

import aifund

data = aifund.etf_daily(159915)

fig = go.Figure(data=go.Candlestick(
    x=data.index,
    open=data.open,
    high=data.high,
    low=data.low,
    close=data.close
))

fig.update_layout(
    title='Salesforce (CRM)',
    title_x=0.5,
    autosize=False,
    width=800,
    height=600,
    xaxis=dict(rangeselector=dict(
        buttons=list([
            dict(count=1,
                 label="1H",
                 step="hour",
                 stepmode="backward"),
            dict(label='1D', step="all"),
        ])
    )),
)
fig.show()
