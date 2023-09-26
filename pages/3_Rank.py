import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from config import config
from config.config import blue, red, df

st.set_page_config(
    page_title='排名类绘图', page_icon='📊',
    layout='wide'
)

pio.templates.default = 'plotly_white+mytheme'

options = {
    'bar_plot': '条形图',
}

st.markdown("**注意**：上传的数据格式请参照后面的示例，总体原则是**每一列表示一个变量，每一行表示"
"一条记录**，每一列表头标题为相应变量名称，也即“长”数据格式。"
)



file_uploaded = st.file_uploader(
    '**上传CSV数据文件**', type=['csv', 'xlsx', 'xls'], help='上传CSV或excel文件格式的数据文件，其他格式数据暂不支持')

sheet_select = st.empty()

data_display = st.empty()

st.divider()

rank_type = st.selectbox(
    '##### 排名类图形：',
    options=options.keys(), index=0,
    format_func=lambda x: options[x],
)


with st.expander('调节图像尺寸（👈点击这里展开调整）'):
    col2, col3 = st.columns(2)
    width = col2.number_input('宽度', min_value=600.0, max_value=None, value=800.0,  
                            step=50.0, format='%.0f',)
    height = col3.number_input('高度', min_value=400.0, max_value=None, value=800*0.618,  
                            step=50.0, format='%.0f')

def bar_rank(data, x, y, barmode='relative', is_vertical=False,
              width=width, height=0.618*width):
    # orientation = 'v' if is_vertical else 'h'
    fig = px.bar(data, x=x, y=y, #text=y if is_vertical else x,
                #  orientation=orientation,
                width=width, height=height)

    if isinstance(y, str) and isinstance(x, str):
        fig.update_traces(
            text=data[y] if is_vertical else data[x],
        )
    else:
        for c in (y if is_vertical else x):
            fig.update_traces(
                text=data[c], selector=dict(name=c)
            )
    fig.update_traces(
        textposition='inside' if barmode=='relative' else 'outside',
        textfont_family=config.font, textfont_size=config.size-2,
    )
    fig.update_layout(
        barmode=barmode,
        xaxis=dict(
            showgrid=False,
            showline=False,
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
        ),
    )

    return fig

rank = {
    'bar_plot': bar_rank,
}

if file_uploaded is not None:
    try:
        data = pd.read_csv(file_uploaded)
    except:
        xl = pd.ExcelFile(file_uploaded)
        sheet = sheet_select.selectbox(
            '🧾**读取哪一个工作表？**', options=xl.sheet_names,
            index=0, help='默认选中第一个工作表'
        )
        data = xl.parse(sheet)
    with data_display.container():
        st.markdown('读取数据前3行展示：')
        st.dataframe(data.head(3), use_container_width=True, hide_index=True)

    columns = data.columns

    fig = None

    with st.expander('##### 绘图区 (带*号为必选)', expanded=True):
        xcol, ycol, colorcol, vcol = st.columns(4)
        x = xcol.multiselect(
            '类别类数据*', options=columns,
            placeholder='排名类别对应列...',
            max_selections=1,
        )
        y = ycol.multiselect(
            '数值类数据*', options=columns, 
            placeholder='排名数值对应列...',
            max_selections=1,
        )
        color = colorcol.multiselect(
            '颜色数据*' if data.shape[1]>2 else '颜色数据', 
            options=columns,
            placeholder='颜色对应的数据...',
            max_selections=1,
            help='颜色选项用于绘制多项目排名, 当绘制多项目排名时颜色数据必选',
        )
        with vcol.container():
            is_vertical = st.checkbox('以柱状图展示排名')
            reverse_axis = st.checkbox('排名反序')
        
        if x and y and (not (data.shape[1]>2) or color):
            # if is_vertical:
            #     x, y = y, x
            if rank_type == 'bar_plot':
                barmode = st.radio(
                    '多数据系列柱形图类型：',
                    options=['relative', 'group'], index=1,
                    format_func=lambda x: '簇状' if x=='group' else '堆叠',
                    horizontal=True,
                )

                if data.shape[1] == 2:
                    data = data.sort_values(by=y)
                    yval = y[0] if is_vertical else x[0]
                    xval = x[0] if is_vertical else y[0]
                elif data.shape[1] > 2:
                    data = data.pivot(index=x[0], columns=color[0], values=y[0])
                    data = data.sort_values(by=data.columns[0]).reset_index()
                    yval = data.columns[1:] if is_vertical else data.columns[0]
                    xval = data.columns[0] if is_vertical else data.columns[1:]

                fig = rank[rank_type](data, xval, yval, barmode, is_vertical, width, height)
  
                fig.update_layout(
                    plot_bgcolor='white',
                    legend_title=color[0] if color else '',
                )
                
                if is_vertical:
                    fig.update_layout(
                        xaxis_autorange='reversed' if reverse_axis else True,
                        yaxis_showticklabels=False,
                        xaxis_title_text='',
                        yaxis_title_text=y[0],
                    )
                else:
                    fig.update_layout(
                        yaxis_autorange='reversed' if reverse_axis else True,
                        xaxis_showticklabels=False,
                        yaxis_title_text='',
                        xaxis_title_text=y[0],
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
                
                pio.write_image(fig, f'tmp.{ext}', scale=1 if ext=='svg' else 3)
                with open(f'tmp.{ext}', 'rb') as file:
                    st.download_button(
                        f'下载图片({ext}格式)', data = file,
                        file_name=f'{options[rank_type]}.{ext}',               
                        mime=f'image/{ext}',)


st.divider()

with st.expander('##### 数据格式示例（👈点此查看上传数据格式）'):
    st.markdown('* 单项目排名类')
    st.dataframe(df['rank_single'], use_container_width=True, hide_index=True)

    st.markdown('* 多项目排名类')
    st.dataframe(df['rank_multi'], use_container_width=True, hide_index=True)