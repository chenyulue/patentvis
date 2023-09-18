import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

from config import config
from config.config import blue, red, df

st.set_page_config(
    page_title='趋势类绘图', page_icon='📈',
    layout='wide'
)

pio.templates.default = 'plotly_white+mytheme'

options = {
    'line_plot': '折线图',
    'area_plot': '面积图(堆叠)',
    'bar_plot': '柱形图'
}

st.markdown("**注意**：上传的数据格式请参照后面的示例，总体原则是**每一列表示一个变量，每一行表示"
"一条记录**，每一列表头标题为相应变量名称，也即“长”数据格式。"
)


file_uploaded = st.file_uploader(
    '**上传CSV数据文件**', type=['csv'], help='上传CSV格式的数据文件，其他格式数据暂不支持')

data_display = st.empty()

st.divider()

trend_type = st.selectbox(
    '##### 趋势图类型：',
    options=options.keys(), index=0,
    format_func=lambda x: options[x],
)


with st.expander('调节图像尺寸（👈点击这里展开调整）'):
    col2, col3 = st.columns(2)
    width = col2.number_input('宽度', min_value=600.0, max_value=None, value=800.0,  
                            step=50.0, format='%.0f',)
    height = col3.number_input('高度', min_value=400.0, max_value=None, value=800*0.618,  
                            step=50.0, format='%.0f')

def line_trend(data, x='年份', y='申请量(项)', color=None,
                 width=width, height=height):
    if color is None:
        return px.line(data, x=x, y=y, width=width, height=height,)
    
    return px.line(data, x=x, y=y, color=color, width=width, height=height)

def area_trend(data, x='年份', y='申请量(项)', color=None,
                 width=width, height=0.618*width):
    if color is None:
        return px.area(data, x=x, y=y, width=width, height=height,)
    
    return px.area(data, x=x, y=y, color=color, width=width, height=height)

def bar_trend(data, x, y, color=None, barmode='relative',
              width=width, height=0.618*width):
    if color is None:
        return px.bar(data, x=x, y=y, width=width, height=height)

    return px.bar(data, x=x, y=y, color=color, barmode=barmode, 
                  width=width, height=height)

trend = {
    'line_plot': line_trend,
    'area_plot': area_trend,
    'bar_plot': bar_trend,
}

if file_uploaded is not None:
    data = pd.read_csv(file_uploaded)
    with data_display.container():
        st.markdown('读取数据前3行展示：')
        st.dataframe(data.head(3), use_container_width=True, hide_index=True)

    columns = data.columns

    with st.expander('##### 绘图区 (带*号为必选)', expanded=True):
        xcol, ycol, colorcol = st.columns(3)
        x = xcol.multiselect(
            'X轴数据*', options=columns,
            placeholder='X轴对应的数据...',
            max_selections=1,
        )
        y = ycol.multiselect(
            'Y轴数据*', options=columns, 
            placeholder='Y轴对应的数据...',
            max_selections=1,
        )
        color = colorcol.multiselect(
            '颜色数据', options=columns,
            placeholder='颜色对应的数据...',
            max_selections=1,
            help='颜色选项用于绘制多数据系列趋势图',
        )
        
        if x and y:
            c = color[0] if color else None
            if trend_type == 'bar_plot':
                barmode = st.radio(
                    '多数据系列柱形图类型：',
                    options=['relative', 'group'], index=0,
                    format_func=lambda x: '簇状' if x=='group' else '堆叠',
                    horizontal=True,
                )
                fig = trend[trend_type](data, x[0], y[0], c, barmode)
            else:
                fig = trend[trend_type](data, x[0], y[0], c)
                
            fig.update_layout(
                plot_bgcolor='white',
                xaxis_tickmode='linear',
            )
            st.plotly_chart(fig, use_container_width=False, theme=None)

            st.divider()
            
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
                    file_name=f'{options[trend_type]}.{ext}',               
                    mime=f'image/{ext}',)


st.divider()

with st.expander('##### 数据格式示例（👈点此查看上传数据格式）'):
    st.markdown('* 单类别趋势')
    st.dataframe(df['single_trend'], use_container_width=True, hide_index=True)

    st.markdown('* 多类别趋势')
    st.dataframe(df['multi_trend'], use_container_width=True, hide_index=True)