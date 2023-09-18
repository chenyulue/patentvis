import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from config import config
from config.config import blue, red, df

st.set_page_config(
    page_title='构成类绘图', page_icon='📊',
    layout='wide'
)

pio.templates.default = 'plotly_white+mytheme'

options = {
    'pie_plot': '饼图',
    'tree_plot': '树形图',
    'sunburst_plot': '多环图',
    'waterfall_plot': '瀑布图',
    'dualbar_plot': '比较条形图'
}

st.markdown("**注意**：上传的数据格式请参照后面的示例，总体原则是**每一列**表示**一个变量**，**每一行**表示"
"**一条记录**，每一列表头标题为相应变量名称，也即“长”数据格式。"
)


file_uploaded = st.file_uploader(
    '**上传CSV数据文件**', type=['csv'], help='上传CSV格式的数据文件，其他格式数据暂不支持')

data_display = st.empty()

st.divider()

cat_type = st.selectbox(
    '##### 技术构成图类型：',
    options=options.keys(), index=0,
    format_func=lambda x: options[x],
)


with st.expander('调节图像尺寸（👈点击这里展开调整）'):
    col2, col3 = st.columns(2)
    width = col2.number_input('宽度', min_value=600.0, max_value=None, value=600.0,  
                            step=50.0, format='%.0f',)
    height = col3.number_input('高度', min_value=600.0, max_value=None, value=600.0,  
                            step=50.0, format='%.0f')

def pie(data, values, names, insidelabel=False, is_hole=False,
        width=width, height=height):
    fig = px.pie(data, values=values, names=names, width=width, height=height)
    fig.update_traces(
        direction='clockwise',
        textfont_family=config.font, textfont_size=config.size-2,
    )
    if insidelabel:
        fig.update_traces(
            textposition='inside', textinfo='percent+label',
            showlegend=False,)
    if is_hole:
        fig.update_traces(hole=0.4)
    return fig

def treemap(data, path, values, color, labels=None, width=width, height=height):
    fig = px.treemap(data, path=path, values=values, color=color,
                     width=width, height=height)
    if labels is not None:
        fig.update_traces(
            textinfo='+'.join(labels)
        )
    return fig

def sunburst(data, path, values, color, labels=None, width=width, height=height):
    fig = px.sunburst(data, path=path, values=values, color=color,
                      width=width, height=height)
    if labels is not None:
        fig.update_traces(
            textinfo='+'.join(labels)
        )
    return fig

def waterfall(data, x, y, color, font_color):
    fig = go.Figure()
    fig.add_trace(go.Waterfall(
        orientation='v', 
        x=data[x], y=[v if i==0 else -v for i, v in enumerate(data[y])],
        measure=['absolute'] + ['relative']*(len(data[y])-1),
        text=[f'{i:.0f}' for i in data[y]], textposition='auto',
        totals_marker_color=color,
        decreasing_marker_color=color,
        textfont_color=font_color,
        textfont_family=config.font, textfont_size=config.size-2,
    ))
    fig.update_layout(
        yaxis_title_text=y,
    )
    return fig

def dualbar(df, x, y, cat, space=50, autorange=None, width=width, height=height):
    cat_data = np.unique(df[cat])
    left_cat = df[cat] == cat_data[0]
    right_cat = df[cat] == cat_data[1]

    left_data = df.loc[left_cat, :]
    right_data = df.loc[right_cat, :]

    size = len(left_data[x])

    fig = go.Figure(data=[
        # go.Bar(
        #     x=[space]*size, y=left_data[y], 
        #     marker_color='white', marker_line_color='white',
        #     orientation='h', showlegend=False,
        # ),
        go.Bar(
            name=cat_data[0], x=left_data[x], y=left_data[y], 
            orientation='h', base=[space]*size,
            text=left_data[x], textposition='outside',
            textfont_family=config.font, textfont_size=config.size-2,
        ),
        # go.Bar(
        #     x=[-space]*size, y=right_data[y], 
        #     marker_color='white', marker_line_color='white',
        #     orientation='h', showlegend=False,
        # ),
        go.Bar(
            name=cat_data[1], x=-right_data[x], y=right_data[y], 
            orientation='h', base=[-space]*size,
            text=right_data[x], textposition='outside',
            textfont_family=config.font, textfont_size=config.size-2,
        ),
        
        go.Scatter(
            x=[0]*size, y=left_data[y],
            mode='text', text=left_data[y],
            showlegend=False,
        ),
    ])
    # Change the bar mode
    fig.update_layout(
        barmode='relative',
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            automargin='height+top',
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            autorange=autorange,
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=width, height=height,
    )

    fig.add_annotation(
        x=1, y=1.1, 
        xref='x domain', yref='y domain',
        text=x,
        showarrow=False,
        font_family=config.font, font_size=config.size-2,
        # align='right', valign='bottom',
    )
    return fig


category_plot = {
    'pie_plot': pie,
    'tree_plot': treemap,
    'sunburst_plot': sunburst,
    'waterfall_plot': waterfall,
    'dualbar_plot': dualbar,
}

if file_uploaded is not None:
    data = pd.read_csv(file_uploaded)
    with data_display.container():
        st.markdown('读取数据前3行展示：')
        st.dataframe(data.head(3), use_container_width=True, hide_index=True)

    columns = data.columns

    # st.write(data)

    fig = None

    with st.expander('##### 绘图区 (带*号为必选)', expanded=True):
        if cat_type == 'pie_plot':
            namecol, valuecol, optioncol = st.columns(3)
            names = namecol.multiselect(
                '标签数据*', options=columns,
                placeholder='标签对应数据...', max_selections=1,
            )
            values = valuecol.multiselect(
                '面积数据*', options=columns,
                placeholder='扇形面积对应数据...', max_selections=1,
            )
            with optioncol.container():
                insidelabel = st.checkbox('扇形内部显示标签')
                is_hole = st.checkbox('显示为圆环图')
        
            if values and names:
                fig = pie(data, values[0], names[0], insidelabel, is_hole, width=width, height=height)
                st.plotly_chart(fig, use_container_width=False, theme=None)

        elif cat_type == 'tree_plot' or cat_type == 'sunburst_plot':
            label_map = {
                'label': '类别名称',
                'value': '类别数值',
                'percent parent': '占父类别百分比',
                'percent root': '占根类别百分比'
            }
            
            pathcol, valuecol = st.columns(2)
            path = pathcol.multiselect(
                '层级路径*', options=columns,
                placeholder='数据构成层级路径...',
                help='请按照1级分支、2级分支、3级分支...这样的顺序依次选择相应的列'
            )
            values = valuecol.multiselect(
                '数值列*', options=columns,
                placeholder='最后一级分支的数据列...',
                max_selections=1,
            )

            colorcol, labelcol = st.columns(2)
            color = colorcol.multiselect(
                '颜色数据*', options=columns,
                placeholder='树形块的颜色分类...',
                max_selections=1
            )
            labels = labelcol.multiselect(
                '标签内容选项', options=['label', 'value', 'percent parent', 'percent root'],
                default=['label'], placeholder='显示的标签内容...',
                format_func=lambda x: label_map[x],
            )
            
            if path and values and color:
                if not labels:
                    labels = ['label']
                    
                fig = category_plot[cat_type](
                    data, path, values[0], color[0], labels
                )
                st.plotly_chart(fig, use_container_width=False, theme=None)

        elif cat_type == 'waterfall_plot':
            xcol, ycol = st.columns(2)
            x = xcol.multiselect(
                'X轴数据*', options=columns,
                placeholder='X轴对应的数据列...',
                max_selections=1,
            )
            y = ycol.multiselect(
                'Y轴数据*', options=columns,
                placeholder='Y轴对应的数据列...',
                max_selections=1,
            )

            colorcol, fontcolorcol = st.columns(2)
            color = colorcol.color_picker('柱形颜色', '#4499FF')
            font_color = fontcolorcol.color_picker('标签颜色', '#FFFFFF')

            if x and y:
                fig = waterfall(data, x[0], y[0], color, font_color)
                fig.update_layout(
                    plot_bgcolor='white',
                )
                st.plotly_chart(fig, use_container_width=False, theme=None)

        elif cat_type == 'dualbar_plot':
            xcol, ycol, catcol = st.columns(3)
            x = xcol.multiselect(
                'X轴数据*', options=columns,
                placeholder='X轴对应数据...', max_selections=1,
            )
            y = ycol.multiselect(
                'Y轴数据*', options=columns,
                placeholder='Y轴对应数据...', max_selections=1,
            )
            cat = catcol.multiselect(
                '类别数据*', options=columns,
                placeholder='类别对应数据...', max_selections=1,
            )
            spacecol, autocol = st.columns(2)
            space = spacecol.number_input(
                '左右子图间隔：', min_value=10, max_value=None,
                value=50, step=5, 
                help='请根据标签长度适应调整左右子图的间隔数值，该数值为图示间隔在X轴上投影长度的一半',
            )
            auto = autocol.checkbox('Y轴是否翻转')

            if auto:
                autorange = 'reversed'
            else:
                autorange = True

            if x and y and cat:
                fig = dualbar(data, x[0], y[0], cat[0], space, autorange, width=width, height=height)
                fig.update_layout(
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
            
            pio.write_image(fig, f'tmp.{ext}', scale=1 if ext=='svg' else 3)
            with open(f'tmp.{ext}', 'rb') as file:
                st.download_button(
                    f'下载图片({ext}格式)', data = file,
                    file_name=f'{options[cat_type]}.{ext}',               
                    mime=f'image/{ext}',)


st.divider()

with st.expander('##### 数据格式示例（👈点此查看上传数据格式）'):
    st.markdown('* 饼图/圆环图')
    st.dataframe(df['pie'], use_container_width=True, hide_index=True)

    st.markdown('* 树形图或多环图')
    st.dataframe(df['treemap'], use_container_width=True, hide_index=True)

    st.markdown('* 瀑布图')
    st.markdown('瀑布图的第一行为总量，之后的各行表示各构成部分的数量，保证之后各行的数值之和等于'
                '第一行的值')
    st.dataframe(df['waterfall'], use_container_width=True, hide_index=True)

    st.markdown('* 比较条形图')
    st.dataframe(df['dualbar'], use_container_width=True, hide_index=True)

