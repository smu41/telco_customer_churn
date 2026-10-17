import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from Data import *
from color import assign_dynamic_colors

data = load_data()
metric = metrics(data)
cate = churn_category(data)
life, life_reason = lifecycle(data)
tract_life = con_life(data)
concen = concentra(data)
city = churn_city(data)

st.set_page_config(layout="wide")

metric_col = st.container(horizontal=True)
churned = metric_col.empty()
total_risk = metric_col.empty()
retention = metric_col.empty()
churn_reve = metric_col.empty()

churned.metric(value=metric['churn_customers'], label='流失客戶')
total_risk.metric(value=f"${metric['churn_revenue'][0]/10**6:.2f}M", label='總收入風險')
retention.metric(value=f"{metric['retention_rate'][0]:.2f}%", label='留存率')
churn_reve.metric(value=f"${metric['churn_revenue'][0]/10**6:.2f}M", label='流失收入')

# ============================================
# 圖組1
# ============================================

chart = st.container(horizontal=True)
with chart:
    # 分類餅圖
    cate_pie = chart.empty()
    fig = go.Figure(go.Pie(values=cate['customers'],
                           labels=cate['churn_category'],
                           hole=0.7,
                           marker=dict(colors=px.colors.sequential.RdBu),
                           textinfo='label', textposition='outside',
                           hovertemplate='Churned Category: %{label}<br>'
                                         'Churned Count: %{value}'
                                         '<extra></extra>'))

    fig.update_layout(title=dict(text='流失分類',
                                 font=dict(size=16)),
                      showlegend=False, width=350, height=350)

    cate_pie.plotly_chart(fig, width='content', height='content')

    # 生命週期集中Bar圖
    life_concen = chart.empty()
    fig = go.Figure(go.Bar(x=concen['tenure_band'],
                           y=concen['customers'].rank(ascending=False),
                           width=.7,
                           hovertemplate='Tenure Band: %{x}<br>' 
                                         'Rank of total customers: %{y}' 
                                         '<extra></extra>',))

    fig.add_bar(x=concen['tenure_band'],
                y=concen['churned'] * 8,
                text=concen['churned'] * 100,
                texttemplate='%{text:.2f}%',
                textangle=270,
                textposition='outside',
                textfont=dict(size=16),
                width=.4, offsetgroup='overlay',
                hovertemplate='Tenure Band: %{x}<br>' 
                              'Churn Rate: %{customdata:.2f}%' 
                              '<extra></extra>',
                customdata=concen['churned'] * 100)

    fig.update_layout(title=dict(text='生命週期',
                                 font=dict(size=15)),
                      showlegend=False,
                      yaxis=dict(showgrid=False,
                                 zeroline=False,
                                 showticklabels=False), width=350, height=450)

    life_concen.plotly_chart(fig, width='content', height='content')

    # 城市流失率TOP
    city_churn = chart.empty()
    # 繪製數字圓點
    fig = go.Figure(go.Scatter(x=[0.11] * len(city['rank'][:5].tolist()),
                               y=list(range(len(city[:5]), 0, -1)),
                               mode='markers+text',
                               marker=dict(symbol='circle', size=25,
                                           color='red', line=dict(width=0)),
                               text=[str(rank) for rank in city['rank'][:5]],
                               textposition='middle center',
                               textfont=dict(size=13, color='black'),
                               hoverinfo='none', showlegend=False,))

    # 繪製中間城市名稱
    fig.add_scatter(x=[0.45] * len(city['city'][:5].tolist()),
                    y=list(range(len(city[:5]), 0, -1)), mode='text',
                    text=city['city'][:5].tolist(), textposition='middle center',
                    textfont=dict(size=13, color='white'), hoverinfo='none',
                    showlegend=False,)

    # 繪製城市流失率
    fig.add_scatter(x=[0.88] * len(city['churned'][:5].tolist()),
                    y=list(range(len(city[:5]), 0, -1)), mode='text',
                    text=[f'{churn*100:.2f}' for churn in city["churned"][:5].tolist()],
                    textposition='middle center', textfont=dict(size=13, color='white'),
                    hoverinfo='none', showlegend=False,)

    # 設置X, Y軸
    fig.update_xaxes(range=[0, 1],
                     visible=False,
                     fixedrange=True)

    fig.update_yaxes(range=[0.45, 5.55],
                     visible=False,
                     fixedrange=True)

    # 設置標題
    fig.update_layout(title=dict(text='城市流失率TOP',
                                 font=dict(size=16), x=0.5, xanchor='center'),
                      autosize=False, width=285, height=380,
                      margin=dict(t=108, b=10, l=8, r=8), showlegend=False,
                      hovermode=False)

    city_churn.plotly_chart(fig)

    # 城市地圖
    map_city = chart.empty()
    # 顯示客戶數在20以上的城市
    city_data = city.loc[city['customers'] >= 20]

    fig = go.Figure(go.Scattermap(lat=city_data['lat'], lon=city_data['lon'], mode='markers',
                                  marker=dict(size=city_data['marker_size'],
                                              color='red', opacity=0.7),
                                  customdata=city_data[['city', 'churned']].to_numpy(),
                                  hovertemplate='City: %{customdata[0]}<br>' 
                                                'Churned: %{customdata[1]:.2f}' 
                                                '<extra></extra>',))

    fig.update_layout(title=dict(text='流失地圖',
                                 font=dict(size=16)),
                      showlegend=False, coloraxis_showscale=False,
                      map=dict(style='carto-positron',
                               center=dict(lat=36.78, lon=-119.42), zoom=4.75))

    map_city.plotly_chart(fig)
# ============================================

# ============================================
chart2 = st.container(horizontal=True)
with chart2:
    life_bar = chart2.empty()

    # 控制欄位中心距離: 數值越大，點與點水平距離越大
    x_order = ['Attitude', 'Competitor', 'Dissatisfaction', 'Other', 'Price']
    x_spacing = 1.35
    x_map = {category : index * x_spacing for index, category in enumerate(x_order)}
    life['x_pos'] = life['churn_category'].map(x_map)
    # 設置顏色
    life = assign_dynamic_colors(life, mode='threshold')

    fig = go.Figure(go.Scatter(x=life['x_pos'], y=life['tenure_band'],
                               mode='markers',
                               marker=dict(symbol='square', size=18,
                                           showscale=False, color=life['marker_color'],
                                           colorscale='RdBu_r',
                                           line=dict(width=0)),
                               hovertemplate='Churn Category: %{x}<br>' 
                                             'Churned Customers: %{customdata}' 
                                             '<extra></extra>',
                               customdata=life['customers'],
                               showlegend=False))

    fig.update_layout(title=dict(text='<b>流失原因與生命週期</b>',
                                 x=0.02, y=0.95, xanchor='left',
                                 yanchor='top', font=dict(size=13)),
                      width=260, height=340,
                      margin=dict(t=108, b=88, l=68, r=16), autosize=False,
                      )

    # 設置X, Y軸
    fig.update_xaxes(type='category', side='top', tickmode='array',
                     tickvals=[x_map[x] for x in x_order], ticktext=x_order,
                     range=[-0.65, x_map[x_order[-1]] + 0.65])
    fig.update_yaxes(type='category', showgrid=False)
    life_bar.plotly_chart(fig, width='content', height='content',)

    # 繪製Heatmap
    life_tract_map=chart2.empty()
    fig = go.Figure(go.Heatmap(x=tract_life['contract'],
                               y=tract_life['tenure_band'],
                               z=tract_life['churn_rate'],
                               text=tract_life["churn_rate"]*100,
                               texttemplate='%{text:.2f}%',
                               textfont=dict(size=12, color='#000000'),
                               customdata=tract_life['churned'],
                               hovertemplate='Contract: %{x}<br>' 
                                             'Tenure Band: %{y}<br>' 
                                             'Churn Number: %{customdata}<br>' 
                                             'Churn Rate: %{text:.2f}%<br>' 
                                             '<extra></extra>',
                               xgap=4, ygap=4, # 格與格的間隙
                               showscale=False, reversescale=True,))

    # 頁面設置
    fig.update_layout(title=dict(text='Contract Commitment vs Lifecycle Churn Risk',
                                 font=dict(size=13), x=0.1, y=1),
                      width=310, height=350,
                      margin=dict(t=112, b=20, l=60, r=12),
                      showlegend=False)

    # 設置X, Y軸
    fig.update_xaxes(side='top', tickangle=60,
                     ticks='', tickfont=dict(size=12),
                     showgrid=False, zeroline=False, showline=False,
                     fixedrange=True)

    fig.update_yaxes(autorange='reversed', ticks='',
                     showgrid=False, zeroline=False, showline=False,
                     tickfont=dict(size=12), fixedrange=True)

    life_tract_map.plotly_chart(fig, width='content', height='content',)

    # 歸因圖
    life_bar = chart2.empty()
    life_reason['y'] = list(range(life_reason.shape[0]))
    fig = go.Figure(go.Bar(x=life_reason['share'], y=life_reason['y'],
                           orientation='h', width=0.72,
                           marker=dict(line=dict(width=0)),
                           customdata=life_reason[['churn_category', 'churn_reason', 'customers']].to_numpy(),
                           hovertemplate='Churn Category: %{customdata[0]}<br>' 
                                         'Churn Reason: %{customdata[1]}<br>' 
                                         'Share of Total Customers: %{x:.2f}%<br> ' 
                                         'Total Customers: %{customdata[2]}<br>' 
                                         '<extra></extra>',
                           showlegend=False),)

    groups = life_reason.groupby('churn_category', observed=True).agg(y_min=('y', 'min'),
                                                                      y_max=('y', 'max'))

    for category, row in groups.iterrows():
        y_min = row['y_min']
        y_max = row['y_max']
        y_center = (y_max + y_min) / 2

        fig.add_shape(type='rect', xref='paper', yref='y',
                      x0=0, x1=1, y0=y_min - 0.48, y1=y_max + 0.48,
                      line=dict(width=0), layer='below',)

        fig.add_shape(type='line', xref='paper', yref='y',
                      x0=0, x1=1, y0=y_min - 0.5, y1=y_min-0.5,
                      line=dict(width=1), layer='below',)

        # 左側分類名稱
        fig.add_annotation(xref='paper', yref='y',
                           x=0.01, y=y_center, text=f'<b>{category}</b>',
                           showarrow=False, xanchor='left', yanchor='middle',
                           align='left', font=dict(size=11))

        # 展開/閉合箭頭
        fig.add_annotation(xref='paper', yref='y',
                           x=0.155, y=y_center, text='▼',
                           showarrow=False, xanchor='center',
                           yanchor='middle', font=dict(size=12))

    # 原文字與百分比文字
    for _, row in life_reason.iterrows():
        # 子原因名稱
        fig.add_annotation(xref='paper', yref='y',
                           x=0.21, y=row['y'],
                           text=row['churn_reason'],
                           showarrow=False, xanchor='left',
                           yanchor='middle', align='left',
                           font=dict(size=10))

        # 百分比文字
        fig.add_annotation(xref='paper', yref='y', x=0.69,
                           y=row['y'], text=f'{row['share']:.2f}%',
                           showarrow=False, xanchor='right', yanchor='middle',
                           font=dict(size=10))

    # 標題與整體版面
    fig.update_layout(title=dict(text='離開的原因',
                                 font=dict(size=13)),
                      margin=dict(t=42, b=12, l=12, r=16),
                      width=560, height=410, bargap=0.2, showlegend=False)

    # 將Bar的繪圖區限制在右側
    fig.update_xaxes(domain=[0.76, 0.99], range=[0, 21], showgrid=False,
                     zeroline=False, showline=False, visible=False,
                     fixedrange=True)
    fig.update_yaxes(range=[-0.65, len(life_reason)-0.35],
                     showgrid=False,
                     zeroline=False,
                     showline=False,
                     visible=False,
                     fixedrange=True)
    life_bar.plotly_chart(fig, width='content', height='content')
