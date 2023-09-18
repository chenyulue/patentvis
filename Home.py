'''
# 专利分析统一绘图
这个平台用于专利分析中统一绘制相关图表，便于后期统稿时图表格式统一。
'''
import os
import sys
sys.path.append(os.getcwd())

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title='主页', page_icon='🏠',
)

st.title('专利分析统一绘图平台')
st.write('---')
st.markdown('''
这个平台用于专利分析中统一绘制相关图表，便于后期统稿时图表格式统一。目前功能还比较简单，选择对应的
图表类型，然后上传特定格式的数据，即可绘制相关图表，绘制完之后点击下载即可。

下载的图片格式以*SVG*矢量图为主，因为矢量图后期的编辑更加方便。如果需要，也可以选择*PNG*位图格式。
''')

df = pd.DataFrame({
    'A1': [1,2,3],
    'B1': [4,5,6],
    'C1': [7,8,9],
}, index=['A0', 'B0', 'C0'],)

st.markdown('''### 关于数据格式
* “长”数据格式

“长”数据格式可以表示多维数据，**每一行**表示一条**记录**，**每一列**表示一个**变量**，其中每列标题表示变量名如下面的表格所示
''')

st.dataframe(
    df.reset_index().melt(id_vars='index', value_vars=['A1', 'B1', 'C1']).rename(
        columns={'index': '分支1', 'variable': '分支2', 'value': '申请量'}), 
    use_container_width=True, hide_index=True)

st.markdown('''* “宽”数据格式
“宽”数据格式只能表示二维数据，其中每一行表示一个维度，每一列表示另一个维度，其中每列和每行的标题表示这两个维度的值
''')
st.dataframe(
    df, use_container_width=True
)
