import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from Data import *

st.set_page_config(layout='wide')

data = load_data()
met = metrics(data)
status = status_c(data)
age = age_churn(data)
contract = revenue_contract(data)
city_rev = city_revenue(data)
reason = churn_reason(data)

# 基礎KPI
col = st.container(horizontal=True)
customer =col.empty()
churn_rate =col.empty()
retention = col.empty()
total_revenue = col.empty()

customer.metric(value=met['total_customers'], label='Total Customer')
churn_rate.metric(value=f'{met['churn_rate'][0]:.1f}%', label='Churn Rate')
retention.metric(value=f'{met['retention_rate'][0]:.1f}%', label='Retention Rate')
total_revenue.metric(value=f'${met['total_revenue'][0]/10**6:,.2f}M', label='Total Revenue')

# ===============================
# 圖表1
# ===============================
chat = st.container(horizontal=True)
with chat:
    # status pie chart
    pie_chart = chat.empty()
    fig = go.Figure(data=[go.Pie(labels=status['customer_status'],
                                 values=status['customer_id'],
                                 hole=.6,
                                 textinfo='label',
                                 textposition='outside',
                                 marker=dict(colors=['#FF0000', '#008000', '#0000FF'], ))])

    fig.add_pie(labels=status['customer_status'],
                values=status['customer_id'],
                hoverinfo='label+value',
                textinfo='value',
                textposition='inside',
                marker=dict(colors=['#FF0000', '#008000', '#0000FF']),
                hole=.6,)

    # 底部注釋
    fig.add_annotation(xref='paper', yref='paper', x=0.5, y=0.15,
                       text=f"{status.query('customer_status == "Stayed" | customer_status == "Joined"')['customer_id'].sum()} | "
                            f"{status.query('customer_status == "Joined"')['customer_id'].values[0]} | "
                            f"{status.query('customer_status == "Churned"')['customer_id'].values[0]}",
                       showarrow=False, xanchor='center', yanchor='middle', font=dict(size=14))

    fig.add_annotation(xref='paper', yref='paper', x=0.3, y=0.085, text='Active',
                       showarrow=False, xanchor='center', yanchor='middle',
                       font=dict(size=14, color='#0000FF'))
    fig.add_annotation(xref='paper', yref='paper', x=0.41, y=0.085,
                       showarrow=False, xanchor='center', yanchor='middle',
                       text=' | ', font=dict(size=14))
    fig.add_annotation(xref='paper', yref='paper', x=0.49, y=0.085, text='New',
                       showarrow=False, xanchor='center', yanchor='middle',
                       font=dict(size=14, color='#008000'))
    fig.add_annotation(xref='paper', yref='paper', x=0.59, y=0.085,
                       showarrow=False, xanchor='center', yanchor='middle',
                       text=' | ', font=dict(size=14))
    fig.add_annotation(xref='paper', yref='paper', x=0.75, y=0.085, text='Churned',
                       showarrow=False, xanchor='center', yanchor='middle',
                       font=dict(size=14, color='#FF0000'))

    fig.add_annotation(xref='paper', yref='paper', x=0.5, y=0.015,
                       text='<b>Customer</b>', showarrow=False,
                       xanchor='center', yanchor='middle', font=dict(size=14))

    fig.update_layout(title=dict(text='客戶狀態',
                                 font=dict(size=16)),
                      autosize=False, width=285, height=380,
                      margin=dict(l=60, r=60, t=60, b=60),
                      showlegend=False, )
    pie_chart.plotly_chart(fig, width='content', height='content',)

    # gender pie chart
    gender_chart = chat.empty()
    fig = go.Figure(data=[go.Pie(labels=data['gender'],
                                 values=data['customer_id'].value_counts(),
                                 hole=.6,
                                 textinfo='value',
                                 textposition='outside',
                                 hoverinfo='label+value')])

    fig.update_layout(legend=dict(orientation='h',x=0.5,
                                  xanchor='center',
                                  yanchor='bottom',
                                  bgcolor='rgba(255, 255, 255, 0)'),
                      title=dict(text='性別',
                                 font=dict(size=16)),
                      autosize=False, width=285, height=380,
                      margin=dict(l=60, r=60, t=60, b=60))

    gender_chart.plotly_chart(fig, width='content', height='content',)

    # age Bar chart
    age_chart = chat.empty()
    fig = go.Figure(data=[go.Bar(x=age['age_band'], y=age['customer'],
                                 hoverinfo='x+y+text',text=age['churned'],
                                 textfont=dict(color='rgba(255, 255, 255, 0)'))])
    fig.add_bar(x=age['age_band'], y=age['churned'],
                width=.4, offsetgroup='overlay', hoverinfo='x+y+text',
                textposition='outside', text=age['churned'],
                textfont=dict(color='black'),
                textangle=270)
    fig.update(layout_showlegend=False,
               layout_yaxis=dict(showticklabels=False,
                                 showgrid=False), layout_title='年齡')
    age_event = age_chart.plotly_chart(fig, on_select='rerun', selection_mode='points')



    # contract bar chart
    contr = chat.empty()
    fig = go.Figure(data=[go.Bar(x=contract['contract'],
                                 y=contract['total_revenue'],
                                 text=f'${contract['total_revenue'][0]/10**6:.2f}M',
                                 width=.6,
                                 hoverinfo='x+text',
                                 textfont=dict(color='rgba(255, 255, 255, 0)'),)])
    fig.add_bar(x=contract['contract'],
                y=contract['churn_revenue'],
                text=f'${contract['churn_revenue'][0]/10**6:.2f}M',
                width=.3,
                offsetgroup='overlay',
                hoverinfo='x+text',
                textposition='outside',
                textfont=dict(color='black'),
                textangle=270 )

    fig.update(layout_yaxis=dict(showticklabels=False,
                                 showgrid=False),
               layout_title='合同收入',
               layout_showlegend=False)
    event2 = contr.plotly_chart(fig, on_select='rerun', selection_mode='points')

# ===============================
# 圖組2
# ===============================

chart2 = st.container(horizontal=True)
with chart2:
    # 城市TOP表
    table = chart2.empty()
    # 左側圓點與數字
    fig = go.Figure(go.Scatter(x=[0.11] * len(city_rev['city'][:5].tolist()),
                                     y=list(range(len(city_rev[:5]), 0, -1)),
                                     mode='markers + text',
                                     marker=dict(symbol='circle', size=25,
                                                 color='blue', line=dict(width=0)),
                                     text=[str(rank) for rank in city_rev['rank'][:5]],
                                     textposition='middle center',
                                     textfont=dict(size=13, color='black'),
                                     hoverinfo='none', showlegend=False))

    # 中間城市名稱
    fig.add_scatter(x=[0.45] * len(city_rev['city'][:5].tolist()),
                    y=list(range(len(city_rev[:5]), 0, -1)),
                    mode='text', text=city_rev['city'][:5].tolist(),
                    textposition='middle center',
                    textfont=dict(size=13, color='white'),
                    hoverinfo='none', showlegend=False)

    # 右側總收入
    fig.add_scatter(x=[0.85] * len(city_rev['city'][:5].tolist()),
                    y=list(range(len(city_rev[:5]), 0, -1)), mode='text',
                    text=[f'${rev/100:.2f}K' for rev in city_rev['total_revenue'][:5]],
                    textposition='middle center', textfont=dict(size=13, color='white'),
                    hoverinfo='none', showlegend=False)

    # 設置X, Y 軸
    fig.update_xaxes(range=[0, 1],
                     visible=False,
                     fixedrange=True)

    fig.update_yaxes(range=[0.45, 5.55],
                     visible=False,
                     fixedrange=True)

    fig.update_layout(title=dict(text='城市收入排行',
                                 font=dict(size=16), x=0.5, xanchor='center'),
                      autosize=False, width=285, height=380,
                      margin=dict(t=102, b=10, l=8, r=8),
                      showlegend=False, hovermode=False)

    table.plotly_chart(fig, width='content', height='content')

    # USA地圖
    map_AC = chart2.empty()
    city_rev = city_rev.loc[city_rev['count'] > 10]
    fig = go.Figure(go.Scattermap(lat=city_rev['lat'], lon=city_rev['lon'], mode='markers',
                                  marker=dict(size=city_rev['marker_size'],
                                              color='blue', opacity=0.7),
                                  customdata=city_rev[['city', 'total_revenue']].to_numpy(),
                                  hovertemplate='City: %{customdata[0]}<br>' 
                                                'Total Revenue: $%{customdata[1]:.2f}K<br>' 
                                                '<extra></extra>',))

    fig.update_layout(title=dict(text='城市地圖',
                                 font=dict(size=16)),
                      showlegend=False,
                      coloraxis_showscale=False,
                      coloraxis_reversescale=True,
                      map=dict(style='carto-positron',
                               center=dict(lat=36.78, lon=-119.42),
                               zoom=4.75), )

    map_AC.plotly_chart(fig)

    # 帕累托圖
    pareto = chart2.empty()
    fig = go.Figure(data=[go.Bar(x=reason['churn_reason'], y=reason['count'],
                             textangle=30, marker=dict(color='rgb(250,128,114)'),)])

    fig.add_scatter(x=reason['churn_reason'], y=reason['cum_pct'], yaxis='y2',)

    fig.update_layout(showlegend=False,
                  yaxis2=dict(overlaying='y',
                              side='right',
                              tick0=0,
                              dtick=0.2,
                              showgrid=False,),)
    pareto.plotly_chart(fig)



select_cate = ''
curve_num= None

if age_event and age_event.selection['points']:
    select_cate = age_event.selection['points'][0]['x']
    curve_num = age_event.selection['points'][0]['curve_number']

    if curve_num == 0:
        age_curve = data.loc[data['age_band'] == select_cate]
        met_age = metrics(age_curve)
        contr_age = revenue_contract(age_curve)
        table_age = city_revenue(age_curve)
        reason_age = churn_reason(age_curve)
    else:
        age_curve = data.loc[data['age_band'] == select_cate]
        met_age = metrics(age_curve)
        contr_age = revenue_contract(age_curve)
        table_age = city_revenue(age_curve)
        reason_age = churn_reason(age_curve)

    customer.metric(value=met_age['total_customers'], label='Total Customer')
    churn_rate.metric(value=f'{met_age['churn_rate'][0]:.1f}%', label='Churn Rate')
    retention.metric(value=f'{met_age['retention_rate'][0]:.1f}%', label='Retention Rate')
    total_revenue.metric(value=f'${met_age['total_revenue'][0]/10**6:,.2f}M', label='Total Revenue')

    # 交互性別餅圖
    fig = go.Figure(data=[go.Pie(labels=age_curve['gender'],
                                 values=age_curve['customer_id'].value_counts(),
                                 hole=.6, title='性別',
                                 textinfo='value',
                                 hoverinfo='label+value')])

    fig.update(layout_legend=dict(orientation='h', x=0.5,
                                  xanchor='center',
                                  yanchor='bottom',
                                  bgcolor='rgba(255, 255, 255, 0)'))
    gender_chart.plotly_chart(fig)

    # 交互客戶狀態餅圖
    fig = go.Figure(data=[go.Pie(labels=age_curve['customer_status'],
                                 values=age_curve['customer_id'].value_counts(),
                                 hole=.6,
                                 textinfo='label',
                                 textposition='outside')])

    fig.add_pie(labels=age_curve['customer_status'],
                values=age_curve['customer_id'].value_counts(),
                hoverinfo='label+value',
                textinfo='value',
                textposition='inside',
                hole=.6, title='客戶狀態')
    fig.update(layout_showlegend=False)
    pie_chart.plotly_chart(fig)

    # 交互合同收入圖
    fig = go.Figure(data=[go.Bar(x=contr_age['contract'],
                                 y=contr_age['total_revenue'],
                                 text=f'${contr_age['total_revenue'][0] / 10 ** 6:.2f}M',
                                 width=.6,
                                 hoverinfo='x+text',
                                 textfont=dict(color='rgba(255, 255, 255, 0)'), )])
    fig.add_bar(x=contr_age['contract'],
                y=contr_age['churn_revenue'],
                text=f'${contr_age['churn_revenue'][0] / 10 ** 6:.2f}M',
                width=.3,
                offsetgroup='overlay',
                hoverinfo='x+text',
                textposition='outside',
                textfont=dict(color='black'),
                textangle=270)

    fig.update(layout_yaxis=dict(showticklabels=False,
                                 showgrid=False),
               layout_title='合同收入',
               layout_showlegend=False)
    contr.plotly_chart(fig)

    # 表格交互
    fig = go.Figure(data=[go.Table(header=dict(values=['city', 'total_revenue'], ),
                                   cells=dict(values=[table_age['city'][0:5],
                                                      table_age['total_revenue'][0:5]], align='left', ), )])
    fig.update_layout(autosize=False, minreducedwidth=200, minreducedheight=200)

    table.plotly_chart(fig)

    # 地圖交互
    fig = px.scatter_map(table_age,
                         lat='lat', lon='lon',
                         size='total_revenue',
                         color='total_revenue',
                         hover_data={'lat': False, 'lon': False,
                                     'city': True, 'total_revenue': True})

    fig.update_layout(showlegend=False,
                      coloraxis_showscale=False,
                      coloraxis_reversescale=True, )

    map_AC.plotly_chart(fig)

    # Pareto交互
    fig = go.Figure(data=[go.Bar(x=reason_age['churn_reason'], y=reason_age['count'],
                                 textangle=30, marker=dict(color='rgb(250,128,114)'), )])

    fig.add_scatter(x=reason_age['churn_reason'], y=reason_age['cum_pct'], yaxis='y2', )

    fig.update_layout(showlegend=False,
                      yaxis2=dict(overlaying='y',
                                  side='right',
                                  tick0=0,
                                  dtick=0.2,
                                  showgrid=False, ), )
    pareto.plotly_chart(fig)
