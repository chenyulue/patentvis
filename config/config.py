import plotly.graph_objects as go
import plotly.io as pio

import numpy as np
import pandas as pd

font = 'SimHei'
size = 18

pio.templates['mytheme'] = go.layout.Template(
    layout_xaxis=dict(
        title_font_family=font,
        title_font_size=size,
        tickfont_family=font,
        tickfont_size=size-2,
    ),
    layout_yaxis=dict(
        title_font_family=font,
        title_font_size=size,
        tickfont_family=font,
        tickfont_size=size-2,
    ),
    layout_legend=dict(
        font_family=font,
        font_size=size-4,
        title_font_family=font,
        title_font_size=size-4,
    ),
    data_scatter=[dict(
        textfont_family=font,
        textfont_size=size-2,
    )],
)

pio.templates.default = 'plotly_white+mytheme'

blue = '#636EFA'
red = '#EF553B'

width = 800

df = {
    'single_trend': pd.DataFrame({
        '年份': range(2011, 2011+5),
        '申请量(项)': np.random.randint(23, 57, size=5)}),
    'multi_trend': pd.DataFrame({
        '年份': range(2011, 2011+6),
        '地区': ['国内']*3 + ['国外']*3,
        '申请量(项)': np.random.randint(23, 57, size=6)
    })
}