import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.io as pio


def single_trend(data, year='年份', value='申请量/项'):
    return px.line(data, x=year, y=value)

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
    