import plotly.graph_objects as go
import plotly.io as pio

import numpy as np
import pandas as pd

import os
cwd = os.getcwd()

font = f'{cwd}/font/simhei.ttf'
size = 18

pio.templates['mytheme'] = go.layout.Template(
    layout_xaxis=dict(
        title_font_family=font,
        title_font_size=size,
        tickfont_family=font,
        tickfont_size=size-2,
        gridcolor='#D8D8D8',
    ),
    layout_yaxis=dict(
        title_font_family=font,
        title_font_size=size,
        tickfont_family=font,
        tickfont_size=size-2,
        gridcolor='#D8D8D8',
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
    }),
    'pie': pd.DataFrame({
        '技术分支': ['X射线', '光学测量', '电子测量', '探针测量'],
        '申请量(项)': np.random.randint(100, 300, size=4)
    }),
    'treemap': pd.read_csv('./assets/tech_treemap.csv'),
    'waterfall': pd.read_csv('./assets/tech_comp.csv'),
    'dualbar': pd.read_csv('./assets/tech_dualbar.csv'),
    'rank_single': pd.read_csv('./assets/rank_single.csv'),
    'rank_multi': pd.read_csv('./assets/rank_multi.csv'),
    'bubble': pd.read_csv('./assets/bubble.csv'),
    'bubble_pie': pd.read_csv('./assets/bubble_pie.csv'),
    'sankey': pd.read_csv('./assets/sankey.csv')
}