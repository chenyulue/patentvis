import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

from config import config
from config.config import blue, red, width, df

pio.templates.default = 'plotly_white+mytheme'

options = {
    'line_plot': '折线图',
    'area_plot': '面积图',
}

select = st.selectbox(
    '请选择你需要绘制的趋势图类型：',
    options=options.keys(), index=0,
    format_func=lambda x: options[x],
)
st.markdown("**注意**：上传的数据格式请参照后面的示例，总体原则是**每一列表示一个变量，每一行表示"
"一条记录**，每一列表头标题为相应变量名称，也即“长”数据格式。"
)


def single_trend(data, year='年份', value='申请量(项)', 
                 width=width, height=0.618*width):
    return px.line(data, x=year, y=value, width=width, height=height,)

file_uploaded = st.file_uploader(
    '上传CSV数据文件', type=['csv'], help='上传CSV格式的数据文件')

if file_uploaded is not None:
    data = pd.read_csv(file_uploaded)
    fig = single_trend(data)
    
    canvas = st.empty()
    canvas.plotly_chart(fig, use_container_width=True)

    pio.write_image(fig, 'tmp.svg')
    with open('tmp.svg', 'rb') as file:
        st.download_button(
            '下载图片(SVG格式)', data = file,
            file_name="趋势图.svg",               
            mime='image/svg', 
            help='下载图片的格式为SVG，便于后续编辑')


st.markdown('**数据格式示例：**')

st.markdown('* 单类别趋势')
st.dataframe(df['single_trend'], use_container_width=True, hide_index=True)

st.markdown('* 多类别趋势')
st.dataframe(df['multi_trend'], use_container_width=True, hide_index=True)