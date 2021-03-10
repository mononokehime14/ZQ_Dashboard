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
import timeit

from apps.data_manager import DBmanager, Cell
from apps.app import app
from apps.pages.records import get_max_date, get_min_date


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
                        className="lm--card-item u-grid-center",
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
                                className="lm--card-item col-sm-6 col-md-6 col-lg-6 col-xl-6 u-cell",
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
                                className="lm--card-item col-sm-6 col-md-6 col-lg-6 col-xl-6 u-cell",
                            ),
                            # html.Div(
                            #     [
                            #         html.Div(
                            #             [
                            #                 html.Button(
                            #                     [
                            #                         html.Div(
                            #                             [
                            #                                 html.Div([html.P("Attention Needed", className="h5",style={'color':'#4F5A60'})]),
                            #                                 html.Div(
                            #                                     [
                            #                                         html.Span(id=f"{id_prefix}_dot_indicator", className="alert-dot"),
                            #                                         html.Span(id=f"{id_prefix}_alert_value", className="mini_container_value",style={'color':'#4F5A60'}),
                            #                                     ],
                            #                                     style = {'text-align':'left'},
                            #                                 ),
                            #                             ],
                            #                         ),
                            #                     ],
                            #                     id = 'alert_button',
                            #                     n_clicks = 0,
                            #                     className = 'transparent_button',
                            #                 ),
                            #             ],
                            #             style = {'text-align':'left'},
                            #         ),
                            #     ],
                            #     className="lm--card-item col-sm-auto col-md-auto u-pb0 u-cell",
                            # ),
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
                                                    # html.Div(
                                                    #     [
                                                            html.Div([html.P("High Consumption", className="h5",style={'color':'#4F5A60'})]),
                                                            html.Div(
                                                                [
                                                                    html.Span(className="healthy-dot",style={'background-color':'#ffe75a'}),
                                                                    html.Span(id=f"{id_prefix}_high_consumption_value", className="mini_container_value",style={'color':'#4F5A60'}),
                                                                ],
                                                                style = {'text-align':'left'},
                                                            ),
                                                    #     ],
                                                    # ),
                                                ],
                                                id = 'high_consumption_button',
                                                n_clicks = 0,
                                                className = 'transparent_button',
                                            ),
                                        ],
                                        style = {'text-align':'left'},
                                    ),
                                ],
                                className="lm--card-item col-sm-6 col-md-6 col-lg-6 col-xl-6 u-cell",
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
                                className="lm--card-item col-sm-6 col-md-6 col-lg-6 col-xl-6 u-cell",
                            ),
                        ],
                        className='u-grid',
                        style={'width':'100%'}
                    ),
                ],
                className="col-sm-6 col-md-6 col-lg-6 col-xl-6 u-cell",
            ),
            html.Div(
                [
                    html.Div(
                        [],
                        id="reduced_number_chart_div",
                        className="lm--card-item col u-cell",
                        style={"position": "relative", "min-width": "138px", "max-width": "188px",'text-align':'center'},
                    ),
                ],
                className = 'col-sm-3 col-md-3 col-lg-3 u-cell',
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
                        min_date_allowed=get_min_date(),
                        max_date_allowed=get_max_date(),
                        initial_visible_month=get_max_date(),
                        end_date=get_max_date(),
                        start_date = get_min_date(),
                        className = 'datepicker_for_summary_page',
                        display_format = 'Do YYYY',
                        updatemode = 'bothdates',
                    ),
                    dcc.Interval(
                        id='date_selector_interval',
                        interval=5*1000, # in milliseconds
                        n_intervals=0
                    ),
                ],
                className = 'u-grid-center',
                style={'width':'100%'}
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
                                                className  = 'col-sm-9 col-md-9 col-lg-9 u-cell',
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.P('Reduced more than 2 times:',className = 'h5'),
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
                            html.Div(
                                [
                                    html.Div(
                                        [

                                        ],
                                        id = 'prediction-time graph div',
                                        style = {'width':'100%'},
                                    ),
                                ],
                                className='u-pt2 u-pb1 u-ph0@sm u-ph1@md u-pr1@lg lm--card',
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

def generate_substation_health_card_values(fig, total_count, ok_count,infected,inactive,towatch):
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
    ], [f"{ok_count}"],[f"{infected}"],[f"{inactive}"],[f"{towatch}"]

def draw_consecutive_true_bar(df):

    dff = df.groupby(['consecutive_false'])['notification_no'].size()
    dff = dff.iloc[1:]
    fig = go.Figure()
    fig.add_trace(go.Bar(y = dff,
                    x = dff.index,
                    marker_color='#48DCC0',
                    text = dff,
                    textposition = 'outside'
                    ))

    fig.update_layout(
        #title_text = 'Consecutively reduced tickets',
        uniformtext_minsize=8, 
        uniformtext_mode='show',
        margin = dict(t=20,r=5,l=5,b=5),
        height = 300,
        # title='Notifications with consecutive FALSE prediction',
        yaxis=dict(
            title='Notifications number',
            titlefont_size=12,
            tickfont_size=10,
            tickmode = 'array',
            tickvals = dff.tolist(),
            zeroline = True,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
        ),
        xaxis=dict(
            title = 'Consecutive Reduction number',
            titlefont_size=12,
            tickfont_size=10,
            tickmode = 'array',
            tickvals =  dff.index,
            zeroline = True,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
        ),
        paper_bgcolor = '#fff',
        plot_bgcolor = '#fff',
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
            style={'height':'100%','margin-top':'5px'},
        ),
    ]

def draw_prediction_time_bar_graph(df,start_date,end_date):
    if df.empty:
        return None
    time_width = end_date - start_date
    print(time_width)
    if time_width <= dt.timedelta(days=12):
        time_width = dt.timedelta(days=1)
    else:
        time_width = time_width / 12
    print(time_width)
    dt_pointer = start_date
    t_dict = {}
    f_dict = {}
    while(dt_pointer < end_date):
        df_p = df[(df['notification_date'] >= dt_pointer) & (df['notification_date'] < dt_pointer + time_width)]   
        if len(df_p)  != 0:
            t_count = len(df_p[df_p['prediction'] == True])
            f_count = len(df_p[df_p['prediction'] == False])
            if time_width == dt.timedelta(days=1):
                tlabel = dt.datetime.strftime(df_p['notification_date'][0],"%-d %b")
                t_dict[tlabel] = t_count
                f_dict[tlabel] = f_count
            else:
                tlabel_front = dt.datetime.strftime(df_p['notification_date'].min(),"%-d %b")
                tlabel_back = dt.datetime.strftime(df_p['notification_date'].max(),"%-d %b")
                tlabel = f"{tlabel_front} - {tlabel_back}"
                t_dict[tlabel] = t_count
                f_dict[tlabel] = f_count
        dt_pointer += time_width
    fig = go.Figure()
    fig.add_trace(go.Bar(
                    name = 'Reduced',
                    y = list(f_dict.values()),
                    x = list(f_dict.keys()),
                    marker_color='#48DCC0',
                    text = list(map(str, f_dict.values())),
                    textposition = 'inside'
                    ))
    fig.add_trace(go.Bar(
                    name = 'Remain',
                    y = list(t_dict.values()),
                    x = list(t_dict.keys()),
                    marker_color="#e54545",
                    text = list(map(str, t_dict.values())),
                    textposition = 'inside'
                    ))

    fig.update_layout(
        #title_text = 'Reductions in chosen period',
        margin = dict(t=5,r=5,l=5,b=5),
        height = 320,
        # title='Notifications with consecutive FALSE prediction',
        yaxis=dict(
            title='Prediction result',
            titlefont_size=12,
            tickfont_size=10,
            # tickmode = 'array',
            # tickvals = dff.tolist(),
            zeroline = True,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
        ),
        xaxis=dict(
            title = 'Time',
            titlefont_size=12,
            tickfont_size=10,
            tickmode = 'array',
            tickvals = list(f_dict.keys()),
            zeroline = True,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
        ),
        paper_bgcolor = '#fff',
        plot_bgcolor = '#fff',
        legend=dict(
            x=1.01,
            y=0.9,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='stack',
        bargap=0.1, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    return  [
        dcc.Graph(
            id="prediction_time_bar_plot",
            figure=fig,
            config={'displayModeBar': False,
                    'responsive': True},
            style={'height':'100%','width':'100%'},
        ),
    ]

def draw_reduced_number_chart(true_count, false_count):
    labels = ['TRUE','FALSE']

    fig = go.Figure(data=[go.Pie(labels=labels, values=[true_count, false_count], direction="clockwise", sort=False, hole=.76)])

    fig.update_traces(
        hoverinfo='label+percent',
        textinfo='none',
        marker=dict(colors=["#e54545", "#48dcc0"]),
    ),
    fig.update_layout(
        showlegend=False,
        autosize=True,
        height = 170,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,1)',
    )
    return html.Div([
        dcc.Graph(
            id="reduced_number_chart",
            figure=fig,
            config={'displayModeBar': False,
                    'responsive': True},
            style={'width': '100%'},
        ),
        html.Div(
            [
                html.H4(f"{false_count}", style={"font-size":"1.8rem", "font-weight":"450", "line-height":"normal", "margin-bottom":"0", "padding-bottom":"0"}),
                html.P(f"Reduced", style={"line-height":"normal", "margin-top":"0", "padding-bottom":"0"})
            ],
            className="mini_container_data_label"
        ),
    ])

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

# def find_consecutive_false(gdf):

#     consecutive_false_dict = {}
#     gdf = gdf.sort_values(by='notification_date', ascending=True)
#     # global false_count
#     false_count = 0 
#     for i, r in gdf.iterrows():
#         if r['prediction'] == False:
#             false_count += 1
#         elif r['prediction'] == True:
#             false_count = 0
#         consecutive_false_dict[r['notification_no']] = false_count

#     gdf['consecutive_false'] = gdf['notification_no'].apply(lambda x: consecutive_false_dict.get(x))
#     return gdf

#this callback uses filted data to updata char, status block, bar graph and so on.
@app.callback(
    [
        # General Status block diagram value
        Output("general_status_block_chart_div", "children"),
        Output("general_status_block_meter_stuck_value", "children"),
        Output('general_status_block_low_consumption_value','children'),
        Output('general_status_block_high_consumption_value','children'),
        Output('general_status_block_other_cause_value','children'),

        #consecutive bar graph
        Output('consecutive_ture_bar','children'),
        Output('more_than_2_value','children'),
        Output('latest_value','children'),

        #prediction-time bar graph
        Output('prediction-time graph div','children'),
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
    # conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
    # engine = sqlalchemy.create_engine(conn_url)
    # df = pd.read_sql_table('notificationlist',con = engine)

    # df['notification_date'] = pd.to_datetime(df['notification_date'])
    # df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')
    
    print("-------Counting summary page used time ----------")
    DB = DBmanager()
    #DB.update_consecutive_false()
    # print("Upadated DB, used time:", timeit.default_timer() - starttime)

    starttime = timeit.default_timer()
    if (start_date is not None) & (end_date is not None):
        if type(start_date) == str:
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
        if type(end_date) == str:
            end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
        if(start_date < end_date):
            df = DB.query_in_timeperiod(start_date,end_date)
            # df = df[df['notification_date'] > start_date]
            # df = df[df['notification_date'] < end_date]
        else:
            df = DB.fetch_all()
            start_date = get_min_date()
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
            end_date = get_max_date()
            end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
    else:
        df = DB.fetch_all()
        start_date = get_min_date()
        start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
        end_date = get_max_date()
        end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
    
    print("Getting initial data, used time:", timeit.default_timer() - starttime)

    output = []

    total_count = 0
    meter_count = 0
    low_consumption =  0
    high_consumption = 0
    other_cause = 0
    # print(df[df['prediction'] > 1])
    # alarm_count = len(df[df['prediction'] == False])
    if not df.empty:
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
    starttime = timeit.default_timer()
    if meter_n_clicks % 2 == 1:
        label_list.append('meter_count')
        value_list.append(meter_count)
        total_count += meter_count
        if not df.empty:
            df_temp = df[df['cause_code'].str.contains('Meter',na=False, regex=True)]
            df_for_bar= pd.concat([df_temp,df_for_bar])

    if lc_n_clicks % 2 == 1:
        label_list.append('low_consumption')
        value_list.append(low_consumption)
        total_count += low_consumption
        if not df.empty:
            df_temp = df[df['cause_code'] == 'Low Consumption']
            df_for_bar= pd.concat([df_temp,df_for_bar])

    if hc_n_clicks % 2 == 1:
        label_list.append('high_consumption')
        value_list.append(high_consumption)
        total_count += high_consumption
        if not df.empty:
            df_temp = df[df['cause_code'] == 'High Consumption']
            df_for_bar= pd.concat([df_temp,df_for_bar])

    if other_n_clicks % 2 == 1:
        label_list.append('other_cause')
        value_list.append(other_cause)
        total_count += other_cause
        if not df.empty:
            df_temp = df[(~(df['cause_code'].str.contains('Meter',na=False, regex=True))) & (df['cause_code'] != 'High Consumption') & (df['cause_code'] != 'Low Consumption')]
            df_for_bar= pd.concat([df_temp,df_for_bar])

    if (meter_n_clicks % 2 == 0) & (lc_n_clicks % 2 == 0) & (hc_n_clicks % 2 == 0) & (other_n_clicks % 2 == 0):
        label_list = ['meter_count','low_consumption','high_consumption','other_cause']
        value_list = [meter_count,low_consumption,high_consumption,other_cause]
        total_count = meter_count + low_consumption + high_consumption + other_cause
        df_for_bar = df

    print("df_for_bar ready, used time:", timeit.default_timer() - starttime)
    fig = generate_donut_chart(label_list,value_list)
    content = generate_substation_health_card_values(fig, total_count, meter_count,low_consumption,high_consumption ,other_cause)
    output.extend(content)

    bar = draw_consecutive_true_bar(df_for_bar)
    output.append(bar)

    starttime = timeit.default_timer()
    df_for_bar = df_for_bar[df_for_bar['consecutive_false'] > 2]
    print("Searching for more than 2 done, used time:", timeit.default_timer() - starttime)
    more_than_2 = [f"{df_for_bar.size}"]
    output.append(more_than_2)
    if(more_than_2 == 0):
        latest = 'None'
    else:
        #df_for_bar['notification_date'] = pd.to_datetime(df_for_bar['notification_date'])
        df_for_bar = df_for_bar.sort_values(by = 'notification_date',ascending = True)
        latest = df_for_bar.tail(1)['notification_date'].dt.strftime('%Y-%m-%d')
    output.append(latest)

    prediction_time_bar = draw_prediction_time_bar_graph(df,start_date,end_date)
    output.append(prediction_time_bar)
    return output

@app.callback(
    [Output('date-picker-range','max_date_allowed'),
    Output('date-picker-range','min_date_allowed'),],
    Input('date_selector_interval','n_intervals'),
)

def update_max_min_date(n_intervals):
    max_date = get_max_date()
    min_date = get_min_date()
    print('Updating Min and Max date allowed, Min:{}, Max:{}'.format(min_date,max_date))
    return [max_date,min_date]

@app.callback(
    Output('reduced_number_chart_div','children'),
    [
        Input('date-picker-range','start_date'),
        Input('date-picker-range','end_date'),
    ]

)

def update_reduced_number_chart(start_date,end_date):
    DB = DBmanager()
    if (start_date is not None) & (end_date is not None):
        if type(start_date) == str:
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
        if type(end_date) == str:
            end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
        if(start_date < end_date):
            df = DB.query_in_timeperiod(start_date,end_date)
            # df = df[df['notification_date'] > start_date]
            # df = df[df['notification_date'] < end_date]
        else:
            df = DB.fetch_all()
            start_date = get_min_date()
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
            end_date = get_max_date()
            end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
    else:
        df = DB.fetch_all()
        start_date = get_min_date()
        start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
        end_date = get_max_date
        end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
    
    if df.empty:
        return None
    
    true_count = len(df[df['prediction'] == True])
    false_count = len(df[df['prediction'] == False])
    return draw_reduced_number_chart(true_count, false_count)

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
