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

def search_result_display_dot(attention):
    if attention == 'TRUE':
        
        return html.Span(className="healthy-search-result-dot",style={'background-color':'#e54545'})
    else:
        return html.Span(className="healthy-search-result-dot",style={'background-color':'#48dcc0'})

def search_result_display(attention, notification_id,notification_date,prediction,cause_code):
    return [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        search_result_display_dot(attention),
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
                            html.P('Ooops, no results have been found',className = 'h2')
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

def search_in_dataframe(content,column_name,df):
    output = []
    for index,row in df.iterrows():
        if row[column_name] == content:
            attention = 'TRUE' if (row['prediction'] == True) else 'FALSE'
            output.append([attention, row['notification_no'],row['notification_date'],attention,row['cause_code']])
    return output

@app.callback(
    Output('display_search_result_block','children'),
    [Input('search_button','n_clicks'),
    Input('search_input_content','value')],
    State('memory-value','data')
)

def update_search_result(n_clicks,input_value,df):
    if(n_clicks > 0):
        df = pd.read_json(df,orient="split")
        output = []
        output = search_in_dataframe(input_value,'notification_no',df)
        if not output:
            output = search_in_dataframe(input_value,'contract_acct',df)
            if not output:
                output = search_in_dataframe(input_value,'meter_no',df)

        if not output:
            return search_result_display_none()
        else:
            output_display = []
            for item in output:
                id_name = list(item[1])[0:10]
                id_name = ''.join(id_name)
                date = item[2].split('T')[0]
                # print(id_name)
                # print(item[2])
                # print(date)
                output_display.extend(search_result_display(item[0],id_name,date,item[3],item[4]))
            return output_display