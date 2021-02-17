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

from app import app
from settings import MAPBOX_ACCESS_TOKEN

optionlist = np.array(
    ['notification_type','notification_no','notification_date','contract_acct','cause_code','meter_no','prediction','probability']
)

def status_block(title, id_prefix, additional_classnames=""):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [],
                        id=f"{id_prefix}_chart_div",
                        className="lm--card-item col u-cell",
                        style={"position": "relative", "min-width": "138px", "max-width": "202px"},
                    ),
                ],
                style={"width": "50%"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(html.P(title, className="h2")),
                        ],
                        className="lm--card-item u-grid",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div([html.P("Attention Needed", className="h5")]),
                                    html.Span(id=f"{id_prefix}_dot_indicator", className="alert-dot"),
                                    html.Span(id=f"{id_prefix}_alert_value", className="mini_container_value"),
                                ],
                                className="lm--card-item col-sm-auto col-md-auto u-pb0 u-cell",
                            ),
                            html.Div(
                                [
                                    html.Div([html.P("Meter Stopped/Stuck", className="h5")]),
                                    html.Span(className="healthy-dot"),
                                    html.Span(id=f"{id_prefix}_healthy_value", className="mini_container_value"),
                                ],
                                className="lm--card-item col-sm-4 col-md-4 u-cell",
                            ),
                            html.Div(
                                [
                                    html.Div([html.P("Low Consumption", className="h5")]),
                                    html.Span(className="infected-dot"),
                                    html.Span(id=f"{id_prefix}_infected_value", className="mini_container_value"),
                                ],
                                className="lm--card-item col-sm-4 col-md-4 u-cell",
                            ),
                        ],
                        className = 'u-grid',
                        style={'width':'100%'}
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div([html.P("High Consumption", className="h5")]),
                                    html.Span(className="inactive-dot"),
                                    html.Span(id=f"{id_prefix}_inactive_value", className="mini_container_value"),
                                ],
                                className="lm--card-item col-sm-4 col-md-4 u-cell",
                            ),
                            html.Div(
                                [
                                    html.Div([html.P("other_cause", className="h5")]),
                                    html.Span(className="towatch-dot"),
                                    html.Span(id=f"{id_prefix}_towatch_value", className="mini_container_value"),
                                ],
                                className="lm--card-item col-sm-4 col-md-4 u-cell",
                            ),
                        ],
                        className='u-grid',
                        style={'width':'100%'}
                    ),
                ],
                className="col u-cell",
                style={"text-align": "left", "width": "50%"},
            ),
        ],
        className="lm--card " + additional_classnames,
        style={"height": "100%"},
    )

def general_scatter_diagram():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(html.P('General Scatter Diagram', className="h2")),
                ],
                className="lm--card-item u-ml2 u-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Select x-axis type:", className="h5"),
                            dcc.Dropdown(
                                id = "xaxis_label",
                                options = [{'label':option,'value':option} for option in optionlist],
                                multi = False,
                                value = 'windspeed',
                                #style={'padding':'3px 13px 3px 10px'}
                            ),
                        ],
                        className='u-ph4',
                    ),
                    html.Div(
                        [
                            html.P("Select y-axix type:", className="h5"),
                            dcc.Dropdown(
                                id = "yaxis_label",
                                options = [{'label':option,'value':option} for option in optionlist],
                                multi = False,
                                value = 'electricity_consumption',
                                #style={'padding':'3px 13px 3px 10px'}
                            ),
                        ],
                        className='u-ph4',
                    ),
                ],
                className="lm--card-item u-ml2 u-grid",
                style={'display':'flex','width':'60%'},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id = "electricity_consumption_scatter",
                                hoverData = {'points':[{'customdata':'0'}]}
                            ) 
                        ],
                        className = 'scatter_diagram',
                        style={'width':'70%'},
                    ),
                    html.Div(
                        [
                            html.P(
                                "Filter by date:",
                                className="h5",
                            ),
                            dcc.RangeSlider(
                                id="year_slider",
                                min=1,
                                max=60,
                                value=[20, 50],
                                allowCross = False,
                                step=1,
                                className="dcc_control",
                            ),
                            html.P(
                                "Filter by pressure:",
                                className="h5",
                            ),
                            dcc.RangeSlider(
                                id="pressure_slider",
                                min=954,
                                max=1024,
                                value=[970, 1010],
                                allowCross = False,
                                step=1,
                                className="dcc_control",
                            ),
                            html.P("Select Temperature strength:", className="h5"),
                            dcc.RadioItems(
                                id="temperature_selector",
                                options=[
                                    {"label": "Warm", "value":24},
                                    {"label": "Normal", "value": 10},
                                    {"label": "Cold", "value": -4},
                                ],
                                value=10,
                                #inputClassName='lm--checkbox-input',
                                #labelClassName='lm--checkbox-label',
                                labelStyle={"display": "inline-block",'margin':'1px 5px 1px 5px'},
                                className="lm--checkbox",
                            ),
                            html.P("Select Var2 value:", className="h5"),
                            dcc.Checklist(
                                id="var2_selector",
                                options=[
                                    {"label": "A", "value": "A"},
                                    {"label": "B", "value": "B"},
                                    {"label": "C", "value": "C"},
                                ],
                                value=["A"],
                                # inputClassName='lm--checkbox-input',
                                # labelClassName='lm--checkbox-label',
                                labelStyle={"display": "inline-block",'margin':'1px 5px 1px 5px'},
                                className="lm--checkbox",
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label('Add a new column'),
                                            dcc.Input(type="text",
                                                    placeholder="placeholder",
                                                    id = 'add_column_input',
                                            ),
                                        ],
                                        className='lm--input'
                                    )
                                ],
                                className='lm--input-group',
                                style={'height':'auto'},
                            ),
                            dcc.Checklist(
                                id="column_type",
                                options=[
                                    {"label": "Mean", "value": "mean"},
                                    {"label": "Probability", "value": "probability"},
                                ],
                                value=["mean"],
                                # inputClassName='lm--checkbox-input',
                                # labelClassName='lm--checkbox-label',
                                #labelStyle={"display": "inline-block"},
                                className="lm--checkbox",
                            ),
                        ],
                        className = 'col u-cell option_block',
                        id="cross-filter-options",
                    ),
                ],
                className='u-grid',
            ),            
        ],
        className="lm--card ",
        style={"height": "100%",'display':'block'},
    )

def download_block():
    return html.Div([
        # html.A("download as csv", id= 'download-link', href="/dash/download_csv/"),
        html.Button([
            html.A('Download Data',
                id='download-link',
                download="electricity_consumption.csv",
                href="",
                target="_blank"),
        ],id='download-btn',className='lm--button lm--button--solid')
    ],style={'margin':'10px 300px 10px 300px'})

def upload_block():
    return html.Div(
        [
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '600px',
                    'height': '100px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '30px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
        ]
    )                

def abnormal_graph():
    return  html.Div(
        [
            html.Div(
                [
                    html.Div(html.P('Abnormal Case Diagram', className="h2")),
                ],
                className="lm--card-item u-ml2 u-grid",
            ),
            html.Div(
                [
                    dcc.Graph(
                        id = "abnormal_scatter",
                        hoverData = {'points':[{'customdata':'0'}]}
                    ),
                ],
                className = 'scatter_diagram',
                style={'width':'70%'},
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.Div([html.P("notification_type", className="h5",style={'color':'#BEC8CE'})]),
                            html.Span(id='notification_type_label', className="mini_container_value"),
                        ],
                        className="lm--card-item u-pb0",
                    ),
                    html.Div(
                        [
                            html.Div([html.P("notification_no", className="h5",style={'color':'#BEC8CE'})]),
                            html.Span(id = 'notification_no_label', className="mini_container_value"),
                        ],
                        className="lm--card-item u-pb0",
                    ),
                    html.Div(
                        [
                            html.Div([html.P("notification_date", className="h5",style={'color':'#BEC8CE'})]),
                            html.Span(id='notification_date_label', className="mini_container_value"),
                        ],
                        className="lm--card-item u-pb0",
                    ),
                    html.Div(
                        [
                            html.Div([html.P("contract_acct", className="h5",style={'color':'#BEC8CE'})]),
                            html.Span(id='contract_acct_label', className="mini_container_value"),
                        ],
                        className="lm--card-item u-pb0",
                    ),
                    html.Div(
                        [
                            html.Div([html.P("cause_code", className="h5",style={'color':'#BEC8CE'})]),
                            html.Span(id='cause_code_label', className="mini_container_value"),
                        ],
                        className="lm--card-item u-pb0",
                    ),
                    dcc.Textarea(id='advise_label',value='AI Advise: ',style={'display':'none'}),                        
                ],
                className = 'col u-cell',
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H4('Advise Action:',
                                id = 'alert_title',
                                className = 'lm--alert-title',
                            ),
                            html.P('You have not selected a case yet',
                                id = 'alert_content',
                                style={'color':'#454f54'})
                        ],
                        className ="lm--alert-content"
                    )
                ],
                id = 'ai_alert',
                className='lm--alert lm--alert-info u-ml5 u-mt2',
                style={'width':'80%'}
            ),  
        ],
        className="lm--card ",
        style={"height": "100%"},
    )

def contribution_bar():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(html.P('Components of Advise', className="h2")),
                ],
                className="lm--card-item u-ml2 u-grid",
            ),
            dcc.Graph(
                id = "contribution_bar",
                style={'width':'100%'},
            )  
        ],
        className="lm--card ",
        style={"height": "100%",},
    )

def generate_abnormal_card(id_name,date_time,cause_code,prediction):
    return [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(id_name,className="h2"),
                                html.P(date_time,className = 'h5'), 
                            ]
                        )
                    ],
                    className = 'lm--card-item u-grid',
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P('Cause',className = 'h5'),
                                        html.P(cause_code,className = 'h5',style={'color':'var(--color-red)'})
                                    ],
                                    className = 'col u-cell lm--card-item',
                                ),
                                html.Div(
                                    [
                                        html.P('Prediction',className = 'h5'),
                                        html.P(prediction,className = 'h5',style={'color':'#4F5A60'})
                                    ],
                                    className = 'col u-cell lm--card-item',
                                ),
                            ],
                            className='u-grid',
                            # style={'width':'160px'}
                        )
                    ],
                ),

            ],
            className = 'u-pt2 lm--card',
            style={'display':'block'},
        )
    ]

layout = [
    # Title Bar
    html.Div(
        html.Nav(
            html.H1("Summary", className="u-pl4 u-mb0"),
            className="lm--header-nav",
        ),
        className="lm--header u-mb0 u-bb",
        style={"margin-top": "3px", "padding": "8px 0"},
    ),

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
                                        [
                                            html.Div(
                                                status_block('General Status','general_status_block'),
                                                className = 'col-sm-12 col-md-9 u-cell u-pt2 u-pb1 u-ph0@sm u-ph0@md u-pr0@lg',
                                            ),
                                        ],
                                        className='u-grid',
                                        style={"height": "100%"},
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                general_scatter_diagram(),
                                                className = 'col-sm-12 col-md-9 u-cell u-pt2 u-pb1 u-ph0@sm u-ph0@md u-pr0@lg',
                                            ),
                                        ],
                                        className='u-grid',
                                        style={"height": "100%"},
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                abnormal_graph(),
                                                className = 'col-sm-12 col-md-9 u-cell u-pt2 u-pb1 u-ph0@sm u-ph0@md u-pr0@lg',
                                            ),
                                        ],
                                        className='u-grid',
                                        style={"height": "100%"},
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                contribution_bar(),
                                                className = 'col-sm-12 col-md-9 u-cell u-pt2 u-pb1 u-ph0@sm u-ph0@md u-pr0@lg',
                                            ),
                                        ],
                                        className='u-grid',
                                        style={"height": "100%"},
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                upload_block(),
                                                className = 'col-sm-12 col-md-9 u-cell u-pt2 u-pb1 u-ph0@sm u-ph0@md u-pr0@lg',
                                            ),
                                        ],
                                        className='u-grid',
                                        style={"height": "100%"},
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                download_block(),
                                                className = 'col-sm-12 col-md-9 u-cell u-pt2 u-pb1 u-ph0@sm u-ph0@md u-pr0@lg',
                                            ),
                                        ],
                                        className='u-grid',
                                        style={"height": "100%"},
                                    ),
                                ],
                                className='col-sm-6 col-md-9 col-lg-10 u-cell u-pr0',
                                style={'height':'100%'}
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(className="u-mt2 alert-dot"),
                                            html.Div([html.P("Attention Needed", className="u-pl1 h3")]),                                          
                                        ],
                                        style={'display':'flex','width':'100%'}
                                    ),
                                    html.Div(
                                        [
 
                                        ],
                                        id='abnormal_cards',
                                    ),
                                ],
                                id= 'abnormal_cards_colomn',
                                className='col-sm-6 col-md-3 col-lg-2 u-cell u-pl0 u-pt2',
                                style={'text-align':'left'}
                            ),
                        ],
                        className='u-grid',
                        style={'width':'100%'}
                    )
                ],
                className="mainContent u-ph1@md u-ph3@lg",
            ),
        ],
    ),

    html.Div(
        [
            html.Div(
                [
                    html.P('2020 SP Group. All Rights Reserved',
                        className='col-sm-12 col-md-3 u-cell',
                    ),
                    html.P('This is a tagline',
                        className = "col-sm-0 col-md-2 push-md-2  u-cell"
                    ),
                    html.Ul(
                        [
                            html.Li('Contact Us',style={'display': 'inline-block','padding':'.25rem'}),
                            html.Li('Terms & Conditions',style={'display': 'inline-block','padding':'.25rem'}),
                            html.Li('Privacy & Policy',style={'display': 'inline-block','padding':'.25rem'}),
                        ],
                        className="col-sm-0 col-md-3 push-md-2 u-cell",
                    )  
                ],
                className='u-grid',
                style={'display':'flex','width':'100%'},
            )              
        ],
        className="lm--footer u-mb0 u-b u-pb0",
        style={'background':'#fff'}
    )

]


def generate_donut_chart(alarm_count, ok_count,infected,inactive,towatch):
    labels = ['Attention Needed','Healthy']

    fig = go.Figure(data=[go.Pie(labels=labels, values=[alarm_count, ok_count,infected,inactive,towatch], direction="clockwise", sort=False, hole=.76)])

    fig.update_traces(
        hoverinfo='label+percent',
        textinfo='none',
        marker=dict(colors=["#e54545", "#48dcc0"])),
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


@app.callback(
    [
        # General Status block diagram value
        Output("general_status_block_chart_div", "children"),
        Output("general_status_block_dot_indicator", "className"),
        Output("general_status_block_healthy_value", "children"),
        Output("general_status_block_alert_value", "children"),
        Output('general_status_block_infected_value','children'),
        Output('general_status_block_inactive_value','children'),
        Output('general_status_block_towatch_value','children'),
    ],
    [
        Input('memory-value','children'),
    ])
def substation_health_charts_callback(df):
    df = pd.read_json(df, orient="split")
    
    output = []

    total_count = len(df.index)

    df_alarm= df[df['prediction'] =='FALSE']
    alarm_count = len(df_alarm.index)
    df = df.groupby('cause_code')
    print(df.count()['Meter Stopped/Stuck'])
    meter_stuck_count = df.count()['Meter Stopped/Stuck'][0]
    low_consumption =  df.count()['Low Consumption'][0]
    high_consumption = df.count()['High Consumption'][0]
    other_cause = total_count - meter_stuck_count - low_consumption - high_consumption


    fig = generate_donut_chart(alarm_count, meter_stuck_count,low_consumption,high_consumption,other_cause)
    content = generate_substation_health_card_values(fig, total_count, meter_stuck_count, alarm_count,low_consumption,high_consumption ,other_cause)
    output.extend(content)

    return output


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
        'There was an error processing this file.'
    ])

    df['notification_date'] = pd.to_datetime(df['notification_date'])
    return df.to_json(orient='split')


@app.callback(
              Output('memory-value','children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_input(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        return parse_contents(list_of_contents[0], list_of_names[0], list_of_dates[0])
    else:
        # df = pd.read_csv("/data/train.csv")
        # df['datetime'] = pd.to_datetime(df['datetime'])   
        d = {'notification_type':['ZQ'],
            'notification_no':['113a8e8bd80b0afa4090ccc075f16d3a'],
            'notification_date':['7/1/2021'],
            'contract_acct':['eb45ad8f792c7443f0dcbb2bd263a486'],
            'meter_no':['20bd9f940cbf029d308888987a584f14'],
            'cause_code':['Meter Stopped/Stuck'],
            'prediction':['FALSE']}
        df= pd.DataFrame(data = d)
        return df.to_json(orient='split')


@app.callback(
    Output('intermediate-value','children'), 
    [Input('year_slider','value'),
    Input('var2_selector','value'),
    Input('pressure_slider','value'),
    Input('temperature_selector','value'),
    Input('memory-value','children'),
    Input('add_column_input','value'),
    Input('column_type','value')]
)
def update_intermedaite_value(datevalue,var2_value,pressure_value,temperature_value,jsonified_data,column_name,column_type):
    dff = pd.read_json(jsonified_data,orient='split')
    min_month = datevalue[0] % 12
    if(min_month == 0):
        min_month = 12
    max_month = datevalue[1] % 12
    if(max_month == 0):
        max_month = 12
    min_year = int(datevalue[0] / 12) + 2013
    max_year = int(datevalue[1] / 12) + 2013
    if(column_type == 'mean'):
        dff[column_name] = dff['notification_no']
    elif (column_type == 'probability'):
        dff_cause = dff.groupby('cause_code')
        dff[column_name] = 1 / dff_cause[dff['cause_code']].count()
    dff_1 = dff
    # dff_1 = dff[(dff['datetime'] < dt.datetime(max_year,max_month,1)) & (dff['datetime'] > dt.datetime(min_year,min_month,1))]
    # dff_1 = dff_1[(dff_1['pressure'] < pressure_value[1]) & (dff['pressure'] > pressure_value[0])]
    # dff_1 = dff_1[(dff_1['temperature'] < temperature_value) & (dff['pressure'] > (temperature_value -14))]                                    
    # dff_1 = dff_1[dff_1['var2'] in var2_value]
    dff_2 = dff_1[dff_1['prediction'] == 'FALSE']
    dataset = {
        'dff_1': dff_1.to_json(orient='split', date_format='iso'),
        'dff_2': dff_2.to_json(orient='split', date_format='iso'),
    }
    return json.dumps(dataset)

@app.callback(
    Output('electricity_consumption_scatter','figure'),
    [Input('xaxis_label','value'),
    Input('yaxis_label','value'),
    Input('intermediate-value','children')]
)
def update_graph(xaxis_label,yaxis_label,jsonified_data):
    dataset = json.loads(jsonified_data)
    dff = pd.read_json(dataset['dff_1'],orient='split')
    fig = px.scatter(
                    dff,
                    x= xaxis_label,
                    y= yaxis_label,
                    hover_name=dff['notification_no'],
                    )
    fig.update_traces(customdata = dff['notification_no'])
    fig.update_xaxes(title = xaxis_label,type = 'linear')
    fig.update_yaxes(title = yaxis_label,type = 'linear')
    fig.update_layout(hovermode = 'closest',autosize = True)
    return fig

@app.callback(
    Output('download-link', 'href'),
    [Input('download-btn', 'n_clicks'),
    Input('intermediate-value','children')]
)
def update_download_link(n_nclicks,jsonified_data):
    dataset = json.loads(jsonified_data)
    dff = pd.read_json(dataset['dff_1'],orient='split')
    csv_string = dff.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


@app.callback(
    Output('abnormal_scatter','figure'),
    [Input('xaxis_label','value'),
    Input('yaxis_label','value'),
    Input('intermediate-value','children')]
)

def update_abnormal_scatter(xaxis_label,yaxis_label,jsonified_data):
    dataset = json.loads(jsonified_data)
    dff = pd.read_json(dataset['dff_2'],orient='split')

    fig = px.scatter(
                    dff,
                    x= xaxis_label,
                    y= yaxis_label,
                    hover_name=dff['notification_no'],)
    fig.update_traces(customdata = dff['notification_no'])
    fig.update_xaxes(title = xaxis_label,type = 'linear')
    fig.update_yaxes(title = yaxis_label,type = 'linear')
    fig.update_layout(hovermode = 'closest',autosize = True)
    return fig

@app.callback(
    [Output('notification_type_label','children'),
     Output('notification_no_label','children'),
     Output('notification_date_label','children'),
     Output('contract_acct_label','children'),
     Output('cause_code_label','children'),
     Output('advise_label','value')],
     [Input('abnormal_scatter','hoverData'),
     Input('intermediate-value','children')]
)

def update_information_row2(hoverData,jsonified_data):
    dataset = json.loads(jsonified_data)
    dff = pd.read_json(dataset['dff_2'],orient='split')
    dff_infor = dff[dff['notification_no'] == hoverData['points'][0]['customdata']]
    if(not dff_infor.empty):
        abnormal = ''
        if dff_infor['prediction'].iloc[0] == 'TRUE':
            abnormal = 'Safe'
        else:
            abnormal = 'Need Manual Check' 

        return [f"{dff_infor['notification_type'].iloc[0]}"],[f"{dff_infor['notification_no'].iloc[0]}"],[f"{dff_infor['notification_date'].iloc[0]}"],[f"{dff_infor['contract_acct'].iloc[0]}"],[f"{dff_infor['cause_code'].iloc[0]}"],'AI advise: {}'.format(abnormal)

    return ['0'],['0'],['0'],['0'],['0'],''

@app.callback(
    [Output('ai_alert','className'),
    Output('alert_content','children'),
    Output('alert_content','style')],
    Input('advise_label','value')
)

def toggle_alert(value):
    if value == ('AI advise: {}'.format('Safe')):
        return 'lm--alert lm--alert--success u-ml5 u-mt2','You may ignore this abnormal case',{'color':'#454f54'}
    elif value == ('AI advise: {}'.format('Need Manual Check')):
        return 'lm--alert lm--alert--error u-ml5 u-mt2','You may need to manual check this case',{'color':'#e44444'}
    else:
        return 'lm--alert lm--alert-info u-ml5 u-mt2','You have not selected a case yet',{'color':'#454f54'}

@app.callback(
    Output('contribution_bar','figure'),
    [Input('abnormal_scatter','hoverData'),
    Input('intermediate-value','children')]
)

def update_contribution_bar(hoverData,jsonified_data):
    dataset = json.loads(jsonified_data)
    dff = pd.read_json(dataset['dff_2'],orient='split')
    dff_contrib = dff[dff['notification_no'] == hoverData['points'][0]['customdata']]
    if not dff_contrib.empty:
        windspeed_value = 23
        temperature_value = 26
        var1_value = 65
        pressure_value = 87
        electricity_value = 96
        factor = ['notification_type','notification_no','notification_date','contract_acct','cause_code']
        factor_value = [windspeed_value,temperature_value,var1_value,pressure_value,electricity_value]
        dfff_contrib = pd.DataFrame({'factors':factor,'percentage':factor_value})
        fig = px.bar(dfff_contrib, 
                    x='factors',
                    y='percentage',
                    color='percentage',
                    labels={'factors':'Contributing factors to our AI Advise'},
                    text=(dfff_contrib['percentage'] * 100).round(0).astype(int)
                    )
        return fig
    else:
        dfff_empty = pd.DataFrame({'factors':['notification_type','notification_no','notification_date','contract_acct','cause_code'],'percentage':[0,0,0,0,0]})
        return px.bar(dfff_empty,
                    x='factors',
                    y='percentage',
                    color='percentage',
                    labels={'factors':'Contributing factors to our AI Advise'},
                    text='percentage'
                    )


@app.callback(
    Output('abnormal_cards','children'),
    Input('memory-value','children')
)

def update_abnormal_cards(jsonified_data):
    dff = pd.read_json(jsonified_data,orient='split')
    dff = dff[dff['prediction'] == 'FALSE']
    output = []
    loop_max = 5
    loop_count = 0
    for i in range(len(dff.index)):
        loop_count+=1
        if loop_count == loop_max:
            break
        id_name = dff['notification_no'].iloc[i]
        date_time = dff['notification_date'].iloc[i]
        cause_code = dff['electricity_consumption'].iloc[i]
        prediction = dff['prediction'].iloc[i]

        card = generate_abnormal_card(id_name,date_time,cause_code,prediction)
        output.extend(card)
    
    return output

