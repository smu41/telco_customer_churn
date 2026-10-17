import numpy as np
import streamlit as st

import plotly.graph_objects as go
import plotly.express as px

from Data import *

st.set_page_config(layout='wide')

data = load_data()
met = metrics(data)
churned = churned_pie(data)
payment = pay_method(data)
quadrant, rv = q_retention(data)
cust_risk = risk_c(data)
city_reve = city_risk(data)

metric_col = st.container(horizontal=True)  # 基礎KPI顯示

with metric_col:
    st.metric(value=met['stayed_customers'], label='風險客戶')
    st.metric(value=f'${met['churn_revenue'][0]/10**6:.2f}M', label='總風險收入')
    st.metric(value=f'{met['risk_cltv'][0]:.0f}', label='客戶終身價值風險')
    st.metric(value=f'${met['monthly_risk_revenue'][0]/1000:.2f}k', label='月收入風險')

# ===============================
# 圖表組1
# ===============================

chart = st.container(horizontal=True)
with chart:
    # 狀態餅圖
    fig = go.Figure(go.Pie(labels=churned['churn_label'],
                           values=churned['customer_id'],
                           hole=.7, textinfo='label', textposition='outside',
                           textfont=dict(size=14),
                           hovertemplate='Churned: %{label}<br> Customers: %{value}' 
                                         '<extra></extra>',
                           marker=dict(colors=['blue', 'red'],)))

    # 底部注釋
    fig.add_annotation(xref='paper', yref='paper', x=0.5, y=0.15,
                       text=f"{data.loc[data['churn_value'] == 1, 'customer_id'].count()} | "
                            f"{data.loc[data['churn_value'] == 0, 'customer_id'].count()}",
                       showarrow=False, xanchor='center', yanchor='middle', font=dict(size=14))

    fig.add_annotation(xref='paper', yref='paper', x=0.42, y=0.085, text='Yes',
                       showarrow=False, xanchor='center', yanchor='middle',
                       font=dict(size=14, color='red'))
    fig.add_annotation(xref='paper', yref='paper', x=0.5, y=0.085,
                       showarrow=False, xanchor='center', yanchor='middle',
                       text=' | ', font=dict(size=14))
    fig.add_annotation(xref='paper', yref='paper', x=0.59, y=0.085, text='No',
                       showarrow=False, xanchor='center', yanchor='middle',
                       font=dict(size=14, color='blue') )

    fig.add_annotation(xref='paper', yref='paper', x=0.5, y=0.035,
                       text='<b>Customer</b>', showarrow=False,
                       xanchor='center', yanchor='middle', font=dict(size=14))

    fig.update_layout(title=dict(text='流失',
                                 font=dict(size=16)),
                      autosize=False, width=285, height=380,
                      margin=dict(l=60, r=60, t=60, b=60),
                      showlegend=False,)

    st.plotly_chart(fig, width='content', height='content',)

    # 支付方式
    fig = go.Figure(go.Bar(x=payment['payment_method'], y=payment['customer_id'],
                           hovertemplate='Payment Method: %{x}<br>'
                                         'Churned: %{customdata[0]}<br>'
                                         'Retention: %{customdata[1]:.2f}%<br>'
                                         'Customers: %{y:.}<br>' 
                                         '<extra></extra>',
                           customdata=list(zip(payment['churn_value'], payment['stayed_rate'],))))

    fig.add_bar(x=payment['payment_method'], y=payment['churn_value'],
                text=payment['churn_rate'], textposition='outside',
                texttemplate='%{text:.0f}%',
                textfont=dict(color='rgb(0, 0, 0)'),
                hovertemplate='Payment Method: %{x}<br>' 
                              'Churned: %{y}<br>' 
                              'Churn Rate: %{customdata[1]:.2f}%<br>' 
                              'Customers: %{customdata[0]}<br>' 
                              '<extra></extra>',
                customdata=list(zip(payment['customer_id'], payment['churn_rate'])),
                offsetgroup='overlay', width=.4,)

    fig.update_layout(title=dict(text='支付方式',
                                 font=dict(size=16)),
                      showlegend=False,
                      yaxis=dict(showticklabels=False,
                                 showgrid=False,
                                 zeroline=False,),
                      autosize=False, width=285, height=380,
                      margin=dict(l=8, r=8, t=65, b=10),)

    st.plotly_chart(fig, width='content', height='content')

    # Top 風險客戶

    # 繪製左側數字圓點
    fig = go.Figure(go.Scatter(x=[0.11] * len(cust_risk['rank'][:5].tolist()),
                               y=list(range(len(cust_risk[:5]), 0, -1)), mode='markers + text',
                               marker=dict(symbol='circle', size=25,
                                           color='red', line=dict(width=0)),
                               text=[str(rank) for rank in cust_risk['rank'][:5]],
                               textposition='middle center', textfont=dict(size=12, color='black'),
                               hoverinfo='none', showlegend=False,))

    # 中間客戶名稱
    fig.add_scatter(x=[0.45] * len(cust_risk['customer_id'][:5].tolist()),
                             y=list(range(len(cust_risk[:5]), 0, -1)), mode='text',
                             text=cust_risk['customer_id'][:5].tolist(), textposition='middle center',
                             textfont=dict(size=12, color='white'), hoverinfo='none',
                             showlegend=False,)

    # 右側風險百分比
    fig.add_scatter(x=[0.88] * len(cust_risk['churn_value'][:5].tolist()),
                    y=list(range(len(cust_risk[:5]), 0, -1)), mode='text',
                    text=[f'{rate * 100:.2f}%' for rate in cust_risk['churn_value'][:5].tolist()],
                    textposition='middle center', textfont=dict(size=12, color='white'),
                    hoverinfo='none', showlegend=False,)

    # 設置X, Y軸
    fig.update_xaxes(range=[0, 1],
                     visible=False,
                     fixedrange=True)

    fig.update_yaxes(range=[0.45, 5.55],
                     visible=False,
                     fixedrange=True)

    # 設置版面
    fig.update_layout(title=dict(text='客戶風險排名',
                                 font=dict(size=16), x=0.5, xanchor='center',),
                      autosize=False, width=285, height=380,
                      margin=dict(t=102, b=10, l=8, r=8),
                      showlegend=False, hovermode=False,)

    st.plotly_chart(fig)

    # 城市風險
    
    fig = go.Figure(go.Scattermap(lat=city_reve['lat'], lon=city_reve['lon'], mode='markers',
                                  marker=dict(size=city_reve['marker_size'],
                                              color='red', opacity=0.7),
                                  customdata=city_reve[['city', 'monthly_revenue']].to_numpy(),
                                  hovertemplate='%{customdata[0]}<br>' 
                                                'Risk at Revenue: %{customdata[1]:.0f}<br>' 
                                                '<extra></extra>', showlegend=False,))

    fig.update_layout(title=dict(text='城市風險地圖',
                                 font=dict(size=16)),
                      showlegend=False,
                      coloraxis_showscale=False,
                      map=dict(style='carto-positron',
                               center=dict(lat=36.78, lon=-119.42),
                               zoom=4.75))

    st.plotly_chart(fig)

# ===============================
# 圖組2
# ===============================

chart2 = st.container(horizontal=True)
with chart2:
    # 留存質量與份額
    y = list(range(len(quadrant['share'])))[::-1]
    fig = go.Figure(data=[go.Bar(x=quadrant['share_pct'],
                                 y=y,
                                 orientation='h',
                                 width=.4,
                                 marker=dict(line=dict(width=0)),
                                 hovertemplate=("<b>%{customdata[0]}</b><br>"
                                                "Customers: %{customdata[1]:,}<br>"
                                                "Share: %{x:.2f}%"
                                                "<extra></extra>"),
                                 customdata=list(zip(quadrant['retention_quadrant'],quadrant['customers'])), )])

    # 在左，中，右欄添加每一列文字
    for yi, label, count, share in zip(y, quadrant['retention_quadrant'],
                                       quadrant['customers'],
                                       quadrant['share_pct']):
        # 左邊欄
        fig.add_annotation(xref='paper', yref='y',
                           x=0.00, y=yi, text=f'{label}',
                           showarrow=False, xanchor='left', yanchor='middle',
                           align='left', font=dict(size=13))

        # 中間欄
        fig.add_annotation(xref='paper', yref='y',
                           x=0.43, y=yi, text=f'{count}',
                           showarrow=False, xanchor='right',
                           yanchor='middle', font=dict(size=13))

        # 左邊欄
        fig.add_annotation(xref='paper', yref='y',
                           x=0.84, y=yi, text=f'{share:.2f}%',
                           showarrow=False, xanchor='left',
                           yanchor='middle', font=dict(size=13))

    # 標題欄
    headers = [(0.00, 'Retention Quadrant', 'left'),
               (0.49, 'Customers', 'right'),
               (0.69, 'Share', 'right')]

    for x, text, anchor in headers:
        fig.add_annotation(xref='paper', yref='y',
                           x=x, y=4.58, text=f'<b>{text}</b>',
                           showarrow=False, xanchor=anchor,
                           yanchor='bottom', font=dict(size=14))

    # 加入分割線
    for line_y in [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]:
        fig.add_shape(type='line', xref='paper', yref='y',
                      x0=0, x1=1, y0=line_y,  y1=line_y, line=dict(color='black', width=1))

    fig.update_xaxes(range=[0, 55], domain=[0.53, 0.88],
                     visible=False, fixedrange=True)
    fig.update_yaxes(showticklabels=False,)
    fig.update_layout(title=dict(text='留存質量與份額',
                                 font=dict(size=16)),
                      showlegend=False,)
    st.plotly_chart(fig)

    # 風險價值圖
    s2 = rv.sample(min(4000, len(rv)), random_state=42)
    col = np.where(s2['churn_value'].values == 1, '#FF0000', '#1E90FF')

    fig = px.scatter(s2, x='risk_score', y='value_score', color=col, color_discrete_sequence=col,)

    # 設置坐標軸
    fig.update_xaxes(title=None)

    fig.update_yaxes(title=dict(text='CLTV(價值)',
                                font=dict(size=12)),
                     tickvals=[2000, 3000, 4000, 5000, 6000],
                     ticktext=['2k', '3k', '4k', '5k', '6k'], ticks='',
                     showgrid=False, zeroline=False, showline=False, fixedrange=True)

    fig.update_layout(title=dict(text='風險 x 價值圖',
                                 y=0.9,
                                 font=dict(size=16)),
                      showlegend=False, coloraxis_showscale=False, hovermode=False)
    st.plotly_chart(fig)
