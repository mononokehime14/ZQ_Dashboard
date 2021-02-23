import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output, State, ClientsideFunction
import datetime as dt
import pandas as pd
import numpy as np
import io
import urllib.parse
import base64
import json
import sqlalchemy

from app import app
from settings import MAPBOX_ACCESS_TOKEN



def status_block(title, id_prefix, additional_classnames=""):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [],
                        id=f"{id_prefix}_chart_div",
                        className="lm--card-item col u-cell",
                        style={"position": "relative", "min-width": "138px", "max-width": "188px",'text-align':'center'},
                    ),
                ],
                className = 'col-sm-3 col-md-3 col-lg-3 u-cell',
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(html.P(title, className="h4")),
                        ],
                        className="lm--card-item u-grid",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Button(
                                                [
                                                    html.Div(
                                                        [
                                                            html.P("Meter Problem", className="h5",style={'color':'#4F5A60'}),
                                                            html.Div(
                                                                [
                                                                    html.Span(className="healthy-dot",style={'background-color':'#48dcc0'}),
                                                                    html.Span(id=f"{id_prefix}_meter_stuck_value", className="mini_container_value",style={'color':'#4F5A60'}),
                                                                ],
                                                                style = {'text-align':'left'},
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                id = 'meter_cause_button',
                                                n_clicks = 0,
                                                className = 'transparent_button',
                                            ),
                                        ],
                                        style = {'text-align':'left'},
                                    ),                                   
                                ],
                                className="lm--card-item col-sm-4 col-md-4 u-cell",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Button(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div([html.P("Low Consumption", className="h5",style={'color':'#4F5A60'})]),
                                                            html.Div(
                                                                [
                                                                    html.Span(className="healthy-dot",style={'background-color':'#ff9d5a','padding-left':'0'}),
                                                                    html.Span(id=f"{id_prefix}_low_consumption_value", className="mini_container_value",style={'color':'#4F5A60'}),
                                                                ],
                                                                style = {'text-align':'left'},
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                id = 'low_consumption_button',
                                                n_clicks = 0,
                                                className = 'transparent_button',
                                            ),
                                        ],
                                        style = {'text-align':'left'},
                                    ),  
                                ],
                                className="lm--card-item col-sm-4 col-md-4 u-cell",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Button(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div([html.P("Attention Needed", className="h5",style={'color':'#4F5A60'})]),
                                                            html.Div(
                                                                [
                                                                    html.Span(id=f"{id_prefix}_dot_indicator", className="alert-dot"),
                                                                    html.Span(id=f"{id_prefix}_alert_value", className="mini_container_value",style={'color':'#4F5A60'}),
                                                                ],
                                                                style = {'text-align':'left'},
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                id = 'alert_button',
                                                n_clicks = 0,
                                                className = 'transparent_button',
                                            ),
                                        ],
                                        style = {'text-align':'left'},
                                    ),
                                ],
                                className="lm--card-item col-sm-auto col-md-auto u-pb0 u-cell",
                            ),
                        ],
                        className = 'u-grid',
                        style={'width':'100%'}
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Button(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div([html.P("High Consumption", className="h5",style={'color':'#4F5A60'})]),
                                                            html.Div(
                                                                [
                                                                    html.Span(className="healthy-dot",style={'background-color':'#ffe75a'}),
                                                                    html.Span(id=f"{id_prefix}_high_consumption_value", className="mini_container_value",style={'color':'#4F5A60'}),
                                                                ],
                                                                style = {'text-align':'left'},
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                id = 'high_consumption_button',
                                                n_clicks = 0,
                                                className = 'transparent_button',
                                            ),
                                        ],
                                        style = {'text-align':'left'},
                                    ),
                                ],
                                className="lm--card-item col-sm-4 col-md-4 u-cell",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Button(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div([html.P("Other_cause", className="h5",style={'color':'#4F5A60'})]),
                                                            html.Div(
                                                                [
                                                                    html.Span(className="healthy-dot",style={'background-color':'#158693'}),
                                                                    html.Span(id=f"{id_prefix}_other_cause_value", className="mini_container_value",style={'color':'#4F5A60'}),
                                                                ],
                                                                style = {'text-align':'left'},
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                id = 'other_cause_button',
                                                n_clicks = 0,
                                                className = 'transparent_button',
                                            ),
                                        ],
                                        style = {'text-align':'left'},
                                    ),
                                ],
                                className="lm--card-item col-sm-4 col-md-4 u-cell",
                            ),
                        ],
                        className='u-grid',
                        style={'width':'100%'}
                    ),
                ],
                className="col-sm-7 col-md-7 col-lg-7 u-cell",
            ),
        ],
        className="lm--card u-grid" + additional_classnames,
        style={'max-height':'198px'},
    )

def manipulation_bar():
    return html.Div(
        [
            html.Div(
                [
                    html.P('Manipulation Bar',className='h5')
                ],
                className = 'u-pb2',
            ),
            html.Div(
                [
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        min_date_allowed=dt.date(2019, 4, 17),
                        max_date_allowed=dt.date(2021, 1, 8),
                        initial_visible_month=dt.date(2021, 1, 8),
                        end_date=dt.date(2020, 4, 17),
                        start_date = dt.date(2019,4,17),
                        className = 'datepicker_for_summary_page',
                    ),
                ],
                className = 'u-grid-center',
                style={'width':'100%'}
            ),
            # html.Div(
            #     [
            #         html.Div(
            #             [
            #                 html.Div(
            #                     [
            #                         dcc.Input(
            #                             type="text",
            #                             placeholder="consecutive_FALSE",
            #                             id = 'add_column_input',
            #                             className="input",
            #                         ),
            #                     ],
            #                     className = 'col-sm-6 col-md-9 col-lg-8 u-cell',
            #                 ),
            #                 html.Div(
            #                     [
            #                         html.Button('Add', 
            #                         id = 'add_column_button', 
            #                         className='lm--button--secondary u-pv2',
            #                         ),
            #                     ],                            
            #                     className = 'col-sm-6 col-md-2 col-lg-3 u-cell',
            #                 ),

            #             ],
            #             className = 'u-grid',
            #         ),
            #     ],
            #     className = 'u-pv2',
            #     style={'height':'100%','display':'block'}
            # ),
            html.Div(
                [
                    html.Button(
                        [
                            html.P('Save Changes',className = 'h4'),
                        ],
                        id = 'save_change_button',
                        className='lm--button--primary',
                    ),
                ],
                # className = 'u-grid u-grid-center@md u-grid-center@sm u-pv2',
                className = 'u-pv2',
                style={'height':'100%','display':'block'}
            ),

        ],
        className = 'lm--card',
        style={'text-align':'center','display':'block'}
    )


def footer():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.P('2020 SP Group. All Rights Reserved'),
                        ],
                        className='col-sm-4 col-md-3 push-md-1 u-cell',
                    ),
                    html.Div(
                        [
                            html.P('This is a tagline'),
                        ],
                        className = "col-sm-4 col-md-2 push-md-2  u-cell"
                    ),
                    html.Div(
                        [
                            html.Ul(
                                [
                                    html.Li('Contact Us',style={'display': 'inline-block','padding':'.25rem'}),
                                    html.Li('Terms & Conditions',style={'display': 'inline-block','padding':'.25rem'}),
                                    html.Li('Privacy & Policy',style={'display': 'inline-block','padding':'.25rem'}),
                                ],
                            )
                        ],
                        className="col-sm-4 col-md-3 push-md-1 u-cell",
                    )  
                ],
                className='u-grid',
                style={'width':'100%'},
            )              
        ],
        className="lm--footer",
        style={'background':'#fff','position':'relative'}
    )



layout = [
    dcc.Store(id="intermediate-value",storage_type='session'),
    html.Div(
        [
            # Main Content
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        status_block('Notification Causes','general_status_block'),
                                    ),
                                ],
                                className='u-pt2 u-pb1 u-ph0@sm u-ph1@md u-pr1@lg',
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [

                                                ],
                                                id= 'consecutive_ture_bar',
                                                style = {'max-height':'300px'},
                                                className  = 'col-sm-9 col-md-9 col-lg-9 u-cell',
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.P('FALSE more than 2 times:',className = 'h5'),
                                                            html.Span(id="more_than_2_value", className="mini_container_value",style={'color':'#4F5A60'}),
                                                        ],
                                                        className = 'u-pb3 u-mb3',
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.P('Latest',className = 'h5'),
                                                            html.Span(id="latest_value", className="mini_container_value",style={'color':'#4F5A60'}),
                                                        ],
                                                    ),
                                                ],
                                                className = 'col-sm-3 col-md-3 col-lg-3 u-cell',
                                            ),
                                        ],
                                        className = 'lm--card u-grid',
                                    ),
                                ],
                                # style = {'max-height':'300px'},
                                className='u-pt0 u-pb1 u-ph0@sm u-ph1@md u-pr1@lg',
                            ),
                        ],
                        className = 'col-sm-6 col-md-9 col-md-8 u-cell',
                        # style={'display':'block'},
                    ),
                    #Manipulation bar
                    html.Div(
                        [
                            html.Div(
                                [
                                    manipulation_bar()
                                ],
                                id = 'manipulation_bar',
                            ),
                        ],
                        className = 'col-sm-5 col-md-2 col-md-3 u-cell u-pt2 u-pb1 u-ph0@sm u-ph1@md u-pr1@lg',
                    ),
                ],
                className="mainContent u-ph1@md u-ph3@lg u-grid",
            ),
        ],
    ),
    # html.Div(
    #     [
    #         footer()
    #     ],
    # ),

]

def draw_non_consecutive_found():
        return html.Div(
        [   
            html.Div(
                [
                    html.Div(
                        [
                            html.P('No anomaly found',className = 'h2',style={'color':'#4F5A60'})
                        ],
                        style={'text-align':'center'}
                    )
                ],
                className = 'u-grid-center',
                style={'text-align':'center'}
            ),
        ],
        className = 'lm--card',
        style={'text-align':'center','display':'block'}
    )

def generate_donut_chart(label_list,value_list):
    # labels = ['meter_count','low_consumption','high_consumption','other_cause']
    color_dic = {'meter_count':"#48dcc0",'low_consumption':'#ff9d5a','high_consumption':'#ffe75a','other_cause':'#158693'}
    fig = go.Figure(data=[go.Pie(labels=label_list, values=value_list, direction="clockwise", sort=False, hole=.76)])

    fig.update_traces(
        hoverinfo='label+percent',
        textinfo='none',
        marker=dict(colors=[color_dic[i] for i in label_list])),
    fig.update_layout(
        showlegend=False,
        autosize=True,
        height=170,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,1)',
    )
    return fig


def generate_substation_health_card_values(fig, total_count, ok_count, alarm_count,infected,inactive,towatch):
    return [
        dcc.Graph(
            id="source_stations_chart",
            figure=fig,
            config={'displayModeBar': False,
                    'responsive': True},
            style={'width': '100%'},
        ),
        html.Div(
            [
                html.H4(f"{total_count}", style={"font-size":"1.8rem", "font-weight":"450", "line-height":"normal", "margin-bottom":"0", "padding-bottom":"0"}),
                html.P(f"Total", style={"line-height":"normal", "margin-top":"0", "padding-bottom":"0"})
            ],
            className="mini_container_data_label"
        ),
    ], "inactive-dot" if alarm_count==0 else "alert-dot", [f"{ok_count}"], [f"{alarm_count}"],[f"{infected}"],[f"{inactive}"],[f"{towatch}"]

def draw_consecutive_true_bar(df):

    dff = df.groupby(['consecutive_false'])['notification_no'].size()
    dff = dff.iloc[1:]
    fig = go.Figure()
    fig.add_trace(go.Bar(y = dff,
                    x = dff.index,
                    marker_color='#00B0B2'
                    ))

    fig.update_layout(
        margin = dict(t=5,r=5,l=5,b=5),
        height = 300,
        # title='Notifications with consecutive FALSE prediction',
        yaxis=dict(
            title='Notifications number',
            titlefont_size=12,
            tickfont_size=10,
            showgrid = False,
        ),
        xaxis=dict(
            title = 'Consecutive False number',
            titlefont_size=12,
            tickfont_size=10,
            showgrid= False,
        ),
        # legend=dict(
        #     x=0,
        #     y=1.0,
        #     bgcolor='rgba(255, 255, 255, 0)',
        #     bordercolor='rgba(255, 255, 255, 0)'
        # ),
        barmode='group',
        # bargap=0.15, # gap between bars of adjacent location coordinates.
        # bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    return  [
        dcc.Graph(
            id="consecutive_true_bar_plot",
            figure=fig,
            config={'displayModeBar': False,
                    'responsive': True},
            style={'height':'100%'},
        ),
    ]

def update_status_chart(label_list,value_list,total_count,n_clicks,temp_label,temp_value):
    if n_clicks % 2 == 1:
        label_list.append(temp_label)
        value_list.append(temp_value)
        total_count += temp_value
    else:
        if temp_label in label_list:
            temp_index = list.index(temp_label)
            del label_list[temp_index]
            del value_list[temp_index]
            total_count -= temp_value
    return label_list,value_list,total_count

#this callback uses filted data to updata char, status block, bar graph and so on.
@app.callback(
    [
        # General Status block diagram value
        Output("general_status_block_chart_div", "children"),
        Output("general_status_block_dot_indicator", "className"),
        Output("general_status_block_meter_stuck_value", "children"),
        Output("general_status_block_alert_value", "children"),
        Output('general_status_block_low_consumption_value','children'),
        Output('general_status_block_high_consumption_value','children'),
        Output('general_status_block_other_cause_value','children'),

        Output('consecutive_ture_bar','children'),
        Output('more_than_2_value','children'),
        Output('latest_value','children'),
    ],
    [
        Input('date-picker-range','start_date'),
        Input('date-picker-range','end_date'),
        Input('meter_cause_button','n_clicks'),
        Input('low_consumption_button','n_clicks'),
        Input('high_consumption_button','n_clicks'),
        Input('other_cause_button','n_clicks'),
    ])

def substation_health_charts_callback(start_date,end_date,meter_n_clicks,lc_n_clicks,hc_n_clicks,other_n_clicks):
    #df = pd.read_json(df, orient="split")
    conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
    engine = sqlalchemy.create_engine(conn_url)
    df = pd.read_sql_table('notificationlist',con = engine)

    #df['notification_date'] = pd.to_datetime(df['notification_date']).dt.strftime('%Y-%m-%d')
    df['notification_date'] = pd.to_datetime(df['notification_date'])

    if (start_date is not None) & (end_date is not None):
        start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
        end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
        if(start_date < end_date):
            df = df[df['notification_date'] > start_date]
            df = df[df['notification_date'] < end_date]

    output = []

    total_count = 0
    meter_count = 0
    low_consumption =  0
    high_consumption = 0
    other_cause = 0

    alarm_count =  df.groupby(['prediction']).size().iloc[1]
    df_cause = df.groupby('cause_code').notification_no.nunique()
    cause_code_type = df_cause.index

    for i in range(len(cause_code_type)):
        if 'Meter' in cause_code_type[i]:
            meter_count += df_cause[i]
        elif cause_code_type[i] == 'Low Consumption':
            low_consumption += df_cause[i]
        elif cause_code_type[i] == 'High Consumption':
            high_consumption += df_cause[i]
        else:
            other_cause += df_cause[i]

    label_list = []
    value_list = []
    df_for_bar = pd.DataFrame()
    # label_list,value_list,total_count = update_status_chart(label_list,value_list,total_count,meter_n_clicks,'meter_count',meter_count)
    # label_list,value_list,total_count = update_status_chart(label_list,value_list,total_count,lc_n_clicks,'low_consumption',low_consumption)
    # label_list,value_list,total_count = update_status_chart(label_list,value_list,total_count,hc_n_clicks,'high_consumption',high_consumption)
    # label_list,value_list,total_count = update_status_chart(label_list,value_list,total_count,other_n_clicks,'other_cause',other_cause)
    if meter_n_clicks % 2 == 1:
        label_list.append('meter_count')
        value_list.append(meter_count)
        total_count += meter_count
        df_temp = df[df['cause_code'].str.contains('Meter',na=False, regex=True)]
        df_for_bar= pd.concat([df_temp,df_for_bar])

    if lc_n_clicks % 2 == 1:
        label_list.append('low_consumption')
        value_list.append(low_consumption)
        total_count += low_consumption
        df_temp = df[df['cause_code'] == 'Low Consumption']
        df_for_bar= pd.concat([df_temp,df_for_bar])

    if hc_n_clicks % 2 == 1:
        label_list.append('high_consumption')
        value_list.append(high_consumption)
        total_count += high_consumption
        df_temp = df[df['cause_code'] == 'High Consumption']
        df_for_bar= pd.concat([df_temp,df_for_bar])

    if other_n_clicks % 2 == 1:
        label_list.append('other_cause')
        value_list.append(other_cause)
        total_count += other_cause
        df_temp = df[(~(df['cause_code'].str.contains('Meter',na=False, regex=True))) & (df['cause_code'] != 'High Consumption') & (df['cause_code'] != 'Low Consumption')]
        df_for_bar= pd.concat([df_temp,df_for_bar])

    if (meter_n_clicks % 2 == 0) & (lc_n_clicks % 2 == 0) & (hc_n_clicks % 2 == 0) & (other_n_clicks % 2 == 0):
        label_list = ['meter_count','low_consumption','high_consumption','other_cause']
        value_list = [meter_count,low_consumption,high_consumption,other_cause]
        total_count = meter_count + low_consumption + high_consumption + other_cause
        df_for_bar = df

    fig = generate_donut_chart(label_list,value_list)
    content = generate_substation_health_card_values(fig, total_count, meter_count, alarm_count,low_consumption,high_consumption ,other_cause)
    output.extend(content)

    bar = draw_consecutive_true_bar(df_for_bar)
    output.append(bar)

    df_for_bar = df_for_bar[df_for_bar['consecutive_false'] > 2]
    more_than_2 = [f"{len(df_for_bar.index)}"]
    output.append(more_than_2)
    if(more_than_2 == 0):
        latest = 'None'
    else:
        #df_for_bar['notification_date'] = pd.to_datetime(df_for_bar['notification_date'])
        df_for_bar.sort_values(by = 'notification_date')
        latest = df_for_bar.tail(1)['notification_date'].dt.strftime('%Y-%m-%d')
    output.append(latest)
    return output


#this callback uses date picker range to filte data
# @app.callback(
#     Output('intermediate-value', 'data'),
#     [Input('date-picker-range','start_date'),
#     Input('date-picker-range','end_date')],
#     #State('memory-value','data')
# )

# def update_date_range(start_date,end_date):
#     #df = pd.read_json(df, orient="split")
#     conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
#     engine = sqlalchemy.create_engine(conn_url)
#     df = pd.read_sql_table('notificationlist',con = engine)

#     #df['notification_date'] = pd.to_datetime(df['notification_date']).dt.strftime('%Y-%m-%d')
#     df['notification_date'] = pd.to_datetime(df['notification_date'])

#     if (start_date is not None) & (end_date is not None):
#         start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
#         end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
#         if(start_date < end_date):
#             df = df[df['notification_date'] > start_date]
#             df = df[df['notification_date'] < end_date]

#     return df.to_json(orient='split',date_format='iso')
