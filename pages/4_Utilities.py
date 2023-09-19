import streamlit as st
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.collections as mcollections
from matplotlib.font_manager import FontProperties

from config import config
from config.config import blue, red, df

import os
cwd = os.getcwd()

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
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    font=FontProperties(fname=f'{cwd}/font/simhei.ttf')

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
                    center=(i*xscale, j*yscale), 
                    startangle=90, frame=True,
                )
            if tmp_data.all():
                handles = wedges

            if showlabel and tmp_data.sum():
                ax.text(i*xscale, j*yscale, f'{tmp_data.sum()}', 
                        ha='center', va='center',
                        fontproperties=font,)

    ax.grid(True)
    ax.yaxis.set_zorder(0)
    ax.xaxis.set_zorder(0)
    ax.set_xticks([i*xscale for i in range(len(rows))], labels=rows, fontproperties=font)
    ax.set_yticks([j*yscale for j in range(len(cols))], labels=cols, fontproperties=font)

    if handles is not None:
        ax.legend(handles, pie_seg, loc='upper left', prop=font, 
                  bbox_to_anchor=(1, 1), frameon=False)

    return fig

def hex2rgba(color, alpha=0.5):
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return f'rgba({r},{g},{b},{alpha})'


def sankey(data, colors=px.colors.qualitative.Plotly, showlinkcolor=False,
           width=width, height=height):
    outlabel = data.columns[0]
    data = data.set_index(keys=outlabel)
    label = list(data.index) + list(data.columns)
    index_top9 = data.sum(axis=1).sort_values(ascending=False).index[:9]
    colormap = dict(zip(index_top9, colors))
    colors = [colormap.get(x, px.colors.qualitative.Plotly[-1]) for x in label]

    row_num, col_num = data.shape
    data.index = range(row_num)
    data.columns = range(row_num, row_num+col_num)
    data = data.reset_index().melt(
        id_vars=['index'], value_vars=range(row_num, row_num+col_num)
    )
    data = data.query('value != 0')

    source = data['index']
    target = data['variable']
    value = data['value']

    colormap1 = dict(zip(index_top9[:5], px.colors.qualitative.Plotly))
    link_colors = [hex2rgba(colormap1.get(label[i], '#AFAFAF')) for i in source]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15, thickness=20, line=dict(color='black', width=0.5),
            label=label, color=colors,
        ),
        link=dict(
            source=source, target=target, value=value, 
            color=link_colors if showlinkcolor else '#AFAFAF',
        )
    )])
    fig.update_layout(
        width=width, height=height,
    )
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
            xcol, sizecol, showlabelcol = st.columns(3)
            x = xcol.multiselect(
                'X轴数据*', options=columns,
                placeholder='X轴数据对应第1列...',
                max_selections=1,
            )
            size_max = sizecol.number_input(
                '气泡尺寸上限', min_value=10, max_value=None, step=5, value=55,
            )
            showlabel = showlabelcol.checkbox('显示数值标签')
            y = st.multiselect(
                'Y轴数据*', options=columns, 
                placeholder='Y轴数据对应剩余列...',
                help='该选项为多选，选择Y轴对应的项目',
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

        elif utility_type == 'scatter_pie':
            xcol, catcol = st.columns(2)
            x = xcol.multiselect(
                'X轴数据*', options=columns,
                placeholder='X轴数据对应第1列...',
                max_selections=1,
            )
            cat = catcol.multiselect(
                '饼图构成数据*', options=columns,
                placeholder='饼图构成数据对应第2列...',
                max_selections=1,
            )
            y = st.multiselect(
                'Y轴数据*', options=columns, 
                placeholder='Y轴对应第3列以后的剩余列...',
                help='该选项为多选，选择Y轴对应的项目，可选部分',
            )

            rscalcol, xscalcol, yscalcol, showlabelcol = st.columns(4)
            rscale = rscalcol.number_input(
                '饼图缩放比例', min_value=1.0, max_value=None, value=1.4, 
                step=0.1, format='%.1f')
            xscale = xscalcol.number_input(
                'X轴缩放比例', min_value=1.0, max_value=None, value=3.5,
                step=0.1, format='%.1f',
            )
            yscale = yscalcol.number_input(
                'Y轴缩放比例', min_value=1.0, max_value=None, value=2.0,
                step=0.1, format='%.1f',
            )
            showlabel = showlabelcol.checkbox('显示数值标签')

            if x and y and cat:
                fig = scatter_pie(
                    data, x[0], y, cat[0], 
                    rscale=rscale, xscale=xscale, yscale=yscale, showlabel=showlabel,
                    width=width, height=height)
                st.pyplot(fig, use_container_width=True)

        elif utility_type == 'sankey_plot':
            showlinkcolor = st.checkbox(
                '连接显示颜色', 
                help=('连接线条的颜色与左侧节点相同，具有一定透明度，并且只对左侧'
                      '前5位的输出节点连线赋予颜色,避免图片太繁杂'),
            )
            fig = sankey(data, showlinkcolor=showlinkcolor,
                        width=width, height=height)
            # fig.update_layout(
            #         xaxis_title_text='',
            #         yaxis_title_text='',
            #         plot_bgcolor='white',
            #     )
            st.plotly_chart(fig, use_container_width=False, theme=None)
        
        st.divider()

        if fig is not None:   
            ext = st.radio(
                '请选择导出图片格式（推荐选择SVG矢量图格式）',
                options=['svg', 'png'], index=0,
                format_func=lambda x: 'SVG矢量图' if x=='svg' else 'PNG位图',
                horizontal=True,
            )

            if utility_type == 'scatter_plot' or utility_type == 'sankey_plot':
                pio.write_image(fig, f'tmp.{ext}', scale=1 if ext=='svg' else 3)
            elif utility_type == 'scatter_pie':
                fig.savefig(f'tmp.{ext}', bbox_inches='tight')

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

    st.markdown('* 桑基图')
    st.markdown('左右两节点的桑基图用于表示技术输入输出，具体的数据格式中，第1列表示技术输出国'
                '（来源国，即最早优先权国家），后面各列表示技术输入国（目标国，即同族中包括的国家）。')
    st.dataframe(df['sankey'], use_container_width=True, hide_index=True)
