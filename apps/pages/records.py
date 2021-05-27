import urllib.parse
import sqlalchemy
import timeit
import math
import json

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import dash._callback_context
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction, ALL, MATCH
import pandas as pd
from pathlib import Path
import datetime as dt
import numpy as np

from apps.data_manager import DBmanager,Cell
from apps.app import app

display_columns = ['notification_no','notification_date','contract_acct','cause_code','meter_no','prediction','consecutive_false']

#these shap values are for testing only
test_shap_value = {"Feature 1":0.94,"Feature 2":0.77, "Feature 3":0.45,"Feature 4":0.44,"Feature 5":-0.35,"Feature 6":-0.34,"Feature 7":0.22,"Feature 8":0.19,"Feature 9":0.13,"Feature 10":0.11}

def draw_datatable():
    """This function draws the data table of records"""
    return html.Div(
        [
            dash_table.DataTable(
                id='datatable',
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in display_columns
                ],
                editable=True,
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current= 0,
                page_size= 20,
                style_data={
                    'width': '14%',
                    'maxWidth': '100px',
                },
                style_cell = {
                    'text-align':'center',
                },
                style_table={
                    'overflowX': 'auto'
                }
            ),
        ]
    )

def get_max_date():
    DB = DBmanager()
    max_date = DB.find_max_date()
    return max_date

def get_min_date():
    DB = DBmanager()
    min_date = DB.find_min_date()
    return min_date

def draw_upper_block():
    """There is two pickers, and some summary information in the top bar of records page"""
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            dcc.DatePickerSingle(
                                id='date_selector_single',
                                min_date_allowed=get_min_date(),
                                max_date_allowed=get_max_date(),
                                initial_visible_month=get_max_date(),
                                date=get_max_date(),
                                className = 'datepicker_for_records_page',
                                style = {'width':'150px','height':'44px'},
                            ),
                            dcc.Interval(
                                id='date_selector_interval',
                                interval=600*1000, # in milliseconds
                                n_intervals=0
                            ),
                            html.Button([],id='fake_button_to_force_refresh',style={'display':'none'},n_clicks = 1),
                        ],
                        style = {'margin-right':'5px'},
                        id = 'date_selector_div',
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='consecutive_false_trace',
                                options=[
                                    {'label': 'Last month', 'value': 'last month'},
                                    {'label': 'Last 3 month', 'value': 'last 3 month'},
                                    {'label': 'Last 6 month', 'value': 'last 6 month'},
                                    {'label':'Last Year','value':'last year'},
                                    {'label':'All Time','value':'all time'},
                                ],
                                value='last year',
                                style = {'width':'150px','height':'44px'},
                            ),
                        ],
                        style = {'align-items':'center','margin-left':'5px'},
                        id = 'consecutive_false_trace_div',
                    ),
                    html.Div(
                        [
                            html.Button(
                                [
                                    html.A('Download',
                                        id='download-link',
                                        download="dayily_records.csv",
                                        href="",
                                        target="_blank",
                                        style = {'color':'#FFFFFF'},
                                    ),
                                ],
                                id= 'csv_download_button',
                                n_clicks = 0,
                                className = 'lm--button--primary u-mt1',
                                style = {'height':'40px','width':'80px'}
                            ),
                        ],
                        style = {'align-items':'center','margin-left':'5px'},
                        id = 'csv_download_button_div',
                    ),
                ],
                style = {'align-items':'center','display':'flex'},
                className = 'col-sm-12 col-md-6 col-lg-6 col-xl-6 u-cell',
            ),
            html.Div(
                [
                    html.Div(
                        [

                        ],
                        id = 'little_chart',
                    ),
                    html.Div(
                        [
                            html.P("", className="h4",id = 'little_chart_label')
                        ],
                        style = {'width':'100%','padding-left':'5px'},
                    ),
                ],
                style = {'display':'inline-flex','align-items':'center'},
                className = 'col-md-6 col-lg-6 col-xl-6 u-cell',
            ),
        ],
        style = {'max-hegiht':'50px'},
        className = 'lm--card u-pv2 u-grid',
    )                           
                                

layout = [
    html.Div(
        [
            # Main Content
            html.Div(
                [
                    #Top bar
                    html.Div(
                        [
                            draw_upper_block()
                        ],
                        id = 'chech_records_upper_block',
                        style = {'padding':'10px'}
                    ),
                    #datatable block
                    html.Div(
                        [
                            html.Div(
                                [
                                    draw_datatable(),
                                ],
                                id = 'display_left_block',
                            ),
                        ],
                        id = 'check_records_display_block',
                    ),
                    #pop-up window
                    dbc.Modal(
                        [
                            dbc.ModalHeader([],id = 'records-modal-header'),
                            dbc.ModalBody([],id = 'records-modal-body'),
                            dbc.ModalFooter(
                                [
                                    dbc.Button(
                                        [
                                            dcc.Link('Search',id = 'search', href='/search'),
                                        ],
                                        n_clicks=0,
                                        id='search_button',
                                        className='ml-auto',
                                    ),
                                    # html.Div(style ={'width':'60%','display':'inline-block'}),
                                    # dbc.Button(
                                    #     'Boost',
                                    #     id = 'boost_button',
                                    #     n_clicks=0,
                                    #     className='ml-auto',
                                    # ),
                                    # dbc.Button(
                                    #     'Downgrade',
                                    #     id = 'downgrade_button',
                                    #     n_clicks=0,
                                    #     className='ml-auto',
                                    # ),
                                    dbc.Button("Close", id="close", className="ml-auto"),
                                ],
                                style={'text-align':'left'},
                            ),
                        ],
                        id = "records-modal",
                        centered=True,
                        size='xl',
                        fade=False,
                        keyboard=True,
                    ),
                    html.A('',id= 'fake-records-cps',style ={'display':'none'}),
                ],
                className="mainContent u-ph1@md u-ph3@lg u-ph5@xl",
            ),
        ],
    ),
]

def generate_little_chart(true_count, false_count):
    """This function draws donut graph in uppper status block, showcasing how many notifications are reduced by ZQ model.

    Args:
        true_count (int): number of reduced notifications
        false_count (int)): number of not reduced notifications

    Returns:
        list: list of divs that make the graph
    """
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
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,1)',
    )
    return fig

#following callback updates everything (including download)
@app.callback(
    [Output('datatable','data'),

    Output('little_chart','children'),
    Output('little_chart_label','children'),
    
    Output('download-link','download'),
    Output('download-link','href'),
    ],

    [Input('date_selector_single','date'),
    Input('consecutive_false_trace','value'),
    Input('csv_download_button','n_clicks')],

    [State('date_selector_single','max_date_allowed'),
    State('date_selector_single','min_date_allowed')]
)

def update_records(start_date,trace_option,download_clicks,max_date,min_date):
    """Main funciton of records page, updating records data.

    Args:
        start_date (str/datetime): the date that users want to check its records
        trace_option (str/datetime): how many time interval should we look back? This will affect consecutive false number
        download_clicks (int): clicks of download button
        max_date (datetime): latest datetime in data base
        min_date (dattime): earliest datetime in data base

    Returns:
        list: list of objects for rendering
    """
    if (start_date is not None) & (trace_option is not None):
        starttime = timeit.default_timer()
        if type(start_date) == str:
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
            max_date = dt.datetime.strptime(max_date,"%Y-%m-%d")
            min_date = dt.datetime.strptime(min_date,"%Y-%m-%d")
            if (start_date > max_date) | (start_date < min_date):
                return [None,None,'Date selected exceeds range= =',None,None]
   
        DB = DBmanager()
        #DB.update_consecutive_false()
        df = DB.trace_records(start_date)
        
        if not df.empty: 

            if trace_option == 'last 6 month':
                df['consecutive_false'] = df['consec_false_6month']
                #end_date = start_date - dt.timedelta(days=180)
            elif trace_option == 'last month':
                df['consecutive_false'] = df['consec_false_1month']
                #end_date = start_date - dt.timedelta(days=30)
            elif trace_option == 'last 3 month':
                df['consecutive_false'] = df['consec_false_3month']
                #end_date = start_date - dt.timedelta(days=90)
            elif trace_option == 'last year':
                df['consecutive_false'] = df['consec_false_12month']
                #end_date = start_date - dt.timedelta(days=365)
            elif trace_option == 'all time':
                pass
                #end_date = get_min_date()
            else:
                return [None,None,'Trace period not supported= =',None,None] 

            drop_columns = list(set(df.columns) - set(display_columns))
            df.drop(drop_columns,axis=1,inplace= True)
            df = df.sort_values(by = 'consecutive_false',ascending= False)
            df['notification_date'] = df['notification_date'].apply(lambda x : x.strftime('%Y-%m-%d'))
            true_count = len(df[df['prediction'] == True])
            false_count = len(df) - true_count            
            rate = int((true_count / (true_count + false_count)) * 100)
            fig = generate_little_chart(true_count,false_count)
            chart_content = [dcc.Graph(
                figure=fig,
                style={'width': '48px','height':'48px'},
            )]
            csv_string = df.to_csv(index=False, encoding='utf-8')
            csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
            print("[Records Page] Fetch records acomplished, used time:", timeit.default_timer() - starttime)
            return [df.to_dict('records'),chart_content,f'True Prediction Rate: {rate}%',f'{dt.datetime.strftime(start_date,"%Y-%m-%d")}.csv',csv_string]
        else:
            return [None,None,'No records on that day',None,None]
    return [None,None,'You have not select Date',None,None]

@app.callback(
    [Output('date_selector_single','max_date_allowed'),
    Output('date_selector_single','min_date_allowed'),
    Output('date_selector_single','initial_visible_month'),
    Output('date_selector_single','date')],
    Input('date_selector_interval','n_intervals'),
    Input('fake_button_to_force_refresh','n_clicks'),
)

def update_datepicker_periodly(n_intervals,n_clicks):
    """updating datepicker, because latest/earliest datetimes in database are changing"""
    max_date = get_max_date()
    min_date = get_min_date()
    return [max_date,min_date,max_date,max_date]


def draw_SHAP_decision_bar(shap_dict):
    """Right scatter graph in the pop up window"""
    y_list = list(shap_dict.values())
    x_list = list(shap_dict.keys())
    fig = go.Figure()
    color_list = ['#48DCC0'] * len(x_list)
    for i in range(len(y_list)):
        if y_list[i] < 0:
            color_list[i] = '#e54545'

    fig.add_trace(go.Scatter(
                    y = x_list,
                    x = y_list,
                    #marker = {'color':color_list},
                    orientation = 'h',
                    mode = 'lines+markers',
                    marker_color=color_list,
                    text = y_list,
                    ))

    fig.update_layout(
        #title_text = 'Consecutively reduced tickets',
        uniformtext_minsize=8, 
        uniformtext_mode='show',
        margin = dict(t=20,r=5,l=5,b=5),
        # clickmode = 'event+select',
        height=300,
        # title='Notifications with consecutive FALSE prediction',
        yaxis=dict(
            title = 'Features',
            titlefont_size=12,
            tickfont_size=10,
            tickmode = 'array',
            tickvals = x_list,
            zeroline = False,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
        ),
        xaxis=dict(
            title='mean(|SHAP value|)',
            titlefont_size=12,
            # tickfont_size=10,
            # tickmode = 'array',
            # tickvals = y_list,
            zeroline = True,
            zerolinecolor='#bfc9cf',
            zerolinewidth=1,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
        ),
        paper_bgcolor = '#fff',
        plot_bgcolor = '#fff',
    )
    return dcc.Graph(
            id="SHAP_importance_plot",
            figure=fig,
            config={'displayModeBar': False,
                    'responsive': True},
            style={'height':'400px','width':'500px'},
        )


def draw_SHAP_vicissitude_bar(shap_dict):
    """Left bar graph in the pop up window"""
    y_list = list(shap_dict.values())
    x_list = list(shap_dict.keys())
    fig = go.Figure()
    # measurelist = ['relative'] * len(x_list)
    # measurelist[0] = 'absolute'
    color_list = ['#48DCC0'] * len(x_list)
    for i in range(len(color_list)):
        if y_list[i] < 0:
            color_list[i] = '#e54545'

    text_list = np.around(np.array(y_list),2)
    fig.add_trace(go.Bar(
                    y = x_list,
                    x = y_list,
                    marker_color=color_list,
                    # measure = measurelist,
                    # decreasing = {"marker":{"color":"#e54545", "line":{"color":"red", "width":2}}},
                    # increasing = {"marker":{"color":"#48DCC0"}},
                    text = text_list,
                    textposition = 'inside',
                    orientation='h',
                    ))

    fig.update_layout(
        # uniformtext_minsize=8, 
        # uniformtext_mode='show',
        margin = dict(t=20,r=5,l=5,b=5),
        #clickmode = 'event+select',
        yaxis=dict(
            title= 'Features',
            titlefont_size=12,
            tickfont_size=10,
            tickmode = 'array',
            tickvals = x_list,
            zeroline = False,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
        ),
        xaxis=dict(
            title = 'mean(|SHAP value|)',
            titlefont_size=12,
            # tickfont_size=10,
            # tickmode = 'array',
            # tickvals = y_list,
            # zeroline = True,
            # zerolinecolor='#ff9d5a',
            # zerolinewidth=3,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
        ),
        paper_bgcolor = '#fff',
        plot_bgcolor = '#fff',
        barmode='relative',
    )
    return dcc.Graph(
            id="SHAP_vicissitude_plot",
            figure=fig,
            config={'displayModeBar': False,
                    'responsive': True},
            style={'height':'400px','width':'500px'},
        )

@app.callback(
    [
        Output('records-modal-header','children'),
        Output('records-modal-body','children'),
        Output('fake-records-cps','children'),
        Output("records-modal", "is_open")
    ],

    [
        Input('datatable','active_cell'),
        Input("close", "n_clicks"),
    ],

    [
        State('datatable','data'),
        State('datatable','columns'),
        State("records-modal", "is_open")
    ]
)

def update_modal(active_cell,n2,rows,columns,is_open):
    """This function draws the pop up window, using information of active cell that users clicked"""
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    if (df.empty) | (not active_cell):
        print("possibility 1")
        return [None,None,None,is_open]
    
    header = str(df.iloc[active_cell['row'],active_cell['column']])
    header_string = active_cell['column_id'] + ': ' + header
    DB = DBmanager()
    shap_dict = DB.get_shapley_value(header)
    if shap_dict is None:
        body = 'No shapley results avaliable'
    else:
        body = [
            html.Div(
                [
                    html.Div(
                        [
                            draw_SHAP_vicissitude_bar(shap_dict)
                        ],
                    ),
                    html.Div(
                        [
                            draw_SHAP_decision_bar(shap_dict)
                        ],
                    ),
                ],
                style={'display':'flex'},
            ),
        ]

    allow_list = ['notification_no']
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'close' in changed_id:
        print("possibility 2")
        return [None,None,header,not is_open]
    elif active_cell:
        if active_cell['column_id'] in allow_list:
            print("possibility 3")
            print(active_cell)
            return [header_string,body,header,not is_open]
    print("possibility 4")
    return [None,None,None,is_open]

@app.callback(
    Output('records-cps','data'),

    Input('fake-records-cps','children'),
)

def update_real_cp_string(fake_string):
    """This function updates intermediary store of notification number.
    We use this intermediary string to update in the index page during our juming from records page to search page,
    so that search page is able to get the notification number that we want to search for.

    Args:
        fake_string (string): notification number selected by users

    Returns:
        data: intermedairy store
    """
    if fake_string is None:
        return None

    # print('gen xin la ' + fake_string)
    return fake_string


