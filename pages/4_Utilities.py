import streamlit as st
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.io as pio

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.collections as mcollections

from config import config
from config.config import blue, red, df

st.set_page_config(
    page_title='实用图表', page_icon='📊',
    layout='wide'
)

pio.templates.default = 'plotly_white+mytheme'

options = {
    'scatter_plot': '单汽泡图',
    'scatter_pie': '饼状气泡图',
    'sankey_plot': '桑基图',
}

st.markdown("**注意**：气泡图和桑基图的数据格式都采用“宽”数据格式或混合数据格式，具体请参照后面的示例。"
)


file_uploaded = st.file_uploader(
    '**上传CSV数据文件**', type=['csv'], help='上传CSV格式的数据文件，其他格式数据暂不支持')

data_display = st.empty()

st.divider()

utility_type = st.selectbox(
    '##### 图表类型：',
    options=options.keys(), index=0,
    format_func=lambda x: options[x],
)


with st.expander('调节图像尺寸（👈点击这里展开调整）'):
    col2, col3 = st.columns(2)
    width = col2.number_input('宽度', min_value=600.0, max_value=None, value=800.0,  
                            step=50.0, format='%.0f',)
    height = col3.number_input('高度', min_value=400.0, max_value=None, value=800*0.618,  
                            step=50.0, format='%.0f')

# Plotting functions
def scatter_plot(data, x, y, size, showlabel=True, size_max=55, 
                width=width, height=height):
# 长数据格式
    fig = px.scatter(
        data, x=x, y=y, size=size, 
        size_max=size_max, text=size,
        width=width, height=height,
    )
    fig.update_traces(
        marker_line=dict(
            color='#1A29FA',
            width=2,
        ),
        mode='markers+text' if showlabel else 'markers',
        marker_sizemode='area',
    )
    return fig

def scatter_pie(data, x, y, cat, colors=px.colors.qualitative.Plotly,
                rscale=1.4, xscale=3.5, yscale=2, showlabel=True,
                width=width, height=height):
    # 长宽混合数据格式
    dpi = plt.rcParams['figure.dpi']
    pie_seg = np.unique(data[cat])
    data = data.set_index(keys=[x, cat])
    rows = np.unique([idx[0] for idx in data.index])
    cols = y
    colors = dict(zip(pie_seg, colors))

    grouped_data = data.groupby(level=0).sum()
    maximum = grouped_data.max().max()
    minimum = grouped_data.min().min()

    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi))
    handles = None
    for i in range(len(rows)):
        for j in range(len(cols)):
            tmp_data = data.loc[rows[i], cols[j]]
            c = []
            for idx in tmp_data.index:
                c.append(colors[idx])
            r = np.sqrt(tmp_data.sum()) / np.sqrt(maximum)
            if r:
                wedges, *_ = ax.pie(
                    tmp_data, colors=c, radius=r*rscale,
                    center=(i*xscale, j*yscale)
                )
            if all(tmp_data):
                handles = wedges

            if showlabel and data.sum():
                ax.text(i*xscale, j*yscale, f'{tmp_data.sum()}', ha='center', va='center')

    ax.grid(True)
    ax.yaxis.set_zorder(0)
    ax.xaxis.set_zorder(0)
    ax.set_xticks([i*xscale for i in range(len(rows))], labels=rows)
    ax.set_yticks([j*yscale for j in range(len(cols))], labels=cols)

    if handles is not None:
        ax.legend(handles, pie_seg, loc='upper left',
                  bbox_to_anchor=(1, 1), frameon=False)

    return fig

utility = {
    'scatter_plot': scatter_plot,
    'scatter_pie': scatter_pie,
    # 'sankey_plot': sankey,
}

if file_uploaded is not None:
    data = pd.read_csv(file_uploaded)
    with data_display.container():
        st.markdown('读取数据前3行展示：')
        st.dataframe(data.head(3), use_container_width=True, hide_index=True)

    columns = data.columns

    fig = None

    with st.expander('##### 绘图区 (带*号为必选)', expanded=True):
        if utility_type == 'scatter_plot':
            xcol, ycol, sizecol = st.columns(3)
            x = xcol.multiselect(
                'X轴数据*', options=columns,
                placeholder='X轴数据对应第1列...',
                max_selections=1,
            )
            y = ycol.multiselect(
                'Y轴数据*', options=columns, 
                placeholder='Y轴数据对应剩余列...',
            )
            with sizecol.container():
                showlabel = st.checkbox('显示数值标签')
                size_max = st.number_input(
                    '气泡尺寸上限', min_value=10, max_value=None, step=5, value=55,
                )

            if x and y:
                data = data.melt(id_vars=x[0], value_vars=y)
                fig = scatter_plot(
                    data, x=x[0], y='variable', size='value',
                    showlabel=showlabel, size_max=size_max, 
                    width=width, height=height,
                )

                fig.update_layout(
                    xaxis_title_text='',
                    yaxis_title_text='',
                    plot_bgcolor='white',
                )
                st.plotly_chart(fig, use_container_width=False, theme=None)


        st.divider()

        if fig is not None:   
            ext = st.radio(
                '请选择导出图片格式（推荐选择SVG矢量图格式）',
                options=['svg', 'png'], index=0,
                format_func=lambda x: 'SVG矢量图' if x=='svg' else 'PNG位图',
                horizontal=True,
            )

            if utility_type == 'scatter_plot':
                pio.write_image(fig, f'tmp.{ext}', scale=1 if ext=='svg' else 3)

            with open(f'tmp.{ext}', 'rb') as file:
                st.download_button(
                    f'下载图片({ext}格式)', data = file,
                    file_name=f'{options[utility_type]}.{ext}',               
                    mime=f'image/{ext}',)


st.divider()

with st.expander('##### 数据格式示例（👈点此查看上传数据格式）'):
    st.markdown('* 单气泡图')
    st.markdown('绘制单气泡图的数据格式中，第1列为X轴上的标签，剩余列的表头为Y轴上的标签，该数据为“宽”数据格式。')
    st.dataframe(df['bubble'], use_container_width=True, hide_index=True)

    st.markdown('* 饼状气泡图')
    st.markdown('饼状气泡区可表示具有构成关系的两个以上区域或申请人在同一领域的技术功效图，'
                '但通常构成对象数量**不建议超过3个**。绘制饼状气泡图的数据格式中，第1列为'
                'X轴上的标签，第2列为饼状图的构成项目，前2列实际上为“长”数据格式；剩余列的'
                '表头为Y轴上的标签, 其采用的“宽”数据格式，所以饼状气泡图的数据格式是混合数据格式。')
    st.dataframe(df['bubble_pie'], use_container_width=True, hide_index=True)
