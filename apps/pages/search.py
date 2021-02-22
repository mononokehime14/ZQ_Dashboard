import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction
from urllib.parse import urlparse, parse_qs
import pandas as pd
from pathlib import Path
import math
import datetime
import timeit
import sqlalchemy

from app import app

def search_bar():
    return html.Div(
        [
            html.Div(
                [
                    dcc.Input(
                        id = 'search_input_content',
                        type='text',
                        placeholder='Search',
                    ),
                ],
                className = 'col-sm-6 col-md-10 col-lg-10 u-cell',
                id = 'search_input_div',
            ),
            html.Div(
                [
                    html.Button(
                        'Search',
                        id= 'search_button',
                        n_clicks = 0,
                        className = 'lm--button--primary',
                        style = {'height':'40px','width':'80px'}
                    ),
                ],
                className = 'col-sm-6 col-md-1 col-lg-1 u-cell',
                id= 'search_button_div',
                style = {'display':'block','text-align':'center'}
            ),
        ],
        className = 'u-grid',
        #style= {'display':'inline-block'},
    )

def search_result_display_dot(prediction):
    if prediction == 'True':        
        return html.Span(className="healthy-search-result-dot",style={'background-color':'#e54545'})
    else:
        return html.Span(className="healthy-search-result-dot",style={'background-color':'#48dcc0'})

def search_result_display(notification_id,notification_date,prediction,cause_code):
    return [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        search_result_display_dot(prediction),
                                    ],
                                    style= {'text-align':'center'}
                                ),
                            ],
                            className = 'col-sm-2 col-md-2 col-lg-2 u-cell u-pt3',
                        ),
                        html.Div(
                            [
                                html.P('Notification ID',className = 'h3',style={'color':'#818A91'}),
                                html.P(notification_id,className = 'h4')
                            ],
                            className = 'col-sm-2 push-sm-1 col-md-2 push-md-1 col-lg-2 push-lg-1 u-cell',
                        ),
                        html.Div(
                            [
                                html.P('Notification date',className = 'h3',style={'color':'#818A91'}),
                                html.P(notification_date,className = 'h4')
                            ],
                            className = 'col-sm-2 col-md-2 col-lg-2 u-cell',
                        ),
                        html.Div(
                            [
                                html.P('Prediction',className = 'h3',style={'color':'#818A91'}),
                                html.P(prediction,className = 'h4')
                            ],
                            className = 'col-sm-2 col-md-2 col-lg-2 u-cell',
                        ),
                        html.Div(
                            [
                                html.P('Cause_code',className = 'h3',style={'color':'#818A91'}),
                                html.P(cause_code,className = 'h4')
                            ],
                            className = 'col-sm-2 col-md-2 col-lg-2 u-cell',
                        ),
                    ],
                    className = 'u-grid',
                    style={'width':'100%'},
                ),
            ],
            className = 'lm--card',
        )
    ]

def search_result_display_none():
    return html.Div(
        [   
            html.Div(
                [
                    html.Div(
                        [
                            html.P('Ooops, no results have been found',className = 'h2',style = {'color':'#818A91'})
                        ],
                        style={'text-align':'center'}
                    )
                ],
                className = 'u-grid-center',
            ),
        ],
        className = 'lm--card',
    )

layout = [

    html.Div(
        [
            # Main Content
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(html.P('Please key in notification/account/meter number', className="h4",style={'color':'#4F5A60'})),                    
                                ],
                                id='search_title',
                                className="lm--card-item u-grid-center",
                                style={"height": "100%"},
                            ),
                            html.Div(
                                [
                                    search_bar()
                                ],
                                id = 'search_bar',
                                className = 'lm--card-item u-grid-center',
                            ),
                        ],
                        id = 'search_block',
                        className= 'lm--card u-mv3',
                        style={'display':'block','text-align':'center','width':'100%'},
                    ),
                    html.Div(
                        [
                            html.Div(
                                id = 'trend_graph_div',
                            ),
                        ],
                        id = 'display_search_result_trend_block',
                        className = 'u-mv1',
                    ),
                    html.Div(
                        [
                            
                        ],
                        id = 'display_search_result_block',
                        className = 'u-mv1',
                    ),
                ],
                className="mainContent u-ph1@md u-ph3@lg",
            ),
        ],
    ),
]

def turn_into_display_list(row,output_display):
    id_name = list(row['notification_no'])[0:10]
    id_name = ''.join(id_name)
    date = row['notification_date'].strftime('%Y-%m-%d')
    return output_display.extend(search_result_display(id_name,date,row['prediction'],row['cause_code']))

def turn_prediction_to_number(x):
    return 1 if x == 'False' else -1

@app.callback(
    [Output('trend_graph_div','children'),
    Output('display_search_result_block','children')],
    [Input('search_button','n_clicks'),
    Input('search_input_content','value')],
    #State('memory-value','data')
)

def update_search_result(n_clicks,input_value):
    if(n_clicks > 0):
        #df = pd.read_json(df,orient="split")
        starttime = timeit.default_timer()
        print("The start time is :",starttime)
        conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
        engine = sqlalchemy.create_engine(conn_url)
        df = pd.read_sql_table('notificationlist',con = engine)
        output = df[(df['notification_no'] == input_value) | (df['contract_acct'] == input_value) | (df['meter_no'] == input_value)]
     

        if output.empty:
            print("The time difference is :", timeit.default_timer() - starttime)
            return [[],search_result_display_none()]
        else:
            output_display = []
            output.apply(lambda x: turn_into_display_list(x,output_display),axis = 1)
            print("The time difference is :", timeit.default_timer() - starttime)
            #output.sort_values(by = 'notification_date')
            output['prediction_in_number'] = output['prediction'].apply(lambda x: turn_prediction_to_number(x))
            x = output['notification_date']
            y = output['prediction_in_number']
            print(y.unique())
            print(x.sort_values(ascending = True))
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x = x,
                    y = y,
                    name = 'linear',
                    line_shape = 'vh',
                )
            )
            fig.add_trace(
                go.Scatter(
                    x = x,
                    y = [0] * (y.size),
                    name = 'linear',
                    line_color = 'red',
                )
            )
            fig.update_traces(
                mode = 'lines+markers',
            )
            fig.update_layout(
                yaxis = dict(
                    tickmode = 'array',
                    tickvals = y.unique()
                ),
                xaxis = dict(
                    tickmode = 'array',
                    tickvals = x.sort_values(ascending = True)
                )
            )
            trend_graph = [
                dcc.Graph(
                    id = 'trend_graph_plot',
                    figure = fig,
                    style = {'width':'100%'},
                )
            ]
            return [trend_graph, output_display]
    else:
        return [[],[]]