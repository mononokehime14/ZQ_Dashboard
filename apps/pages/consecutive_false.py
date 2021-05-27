import io
import urllib.parse
import base64
import json
import timeit


import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction
import datetime as dt
import pandas as pd
import numpy as np
import sqlalchemy as sql
from dateutil.relativedelta import relativedelta


from apps.data_manager import DBmanager, Cell
from apps.app import app
from apps.pages.records import get_max_date, get_min_date, draw_SHAP_decision_bar, draw_SHAP_vicissitude_bar

display_columns = ['contract_acct','meter_no','notification_date','prediction','consecutive_false']
def datatable():
    """Data Table Div"""
    return html.Div(
        [
            dash_table.DataTable(
                id='data_table',
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
                    'width': '20%',
                    'maxWidth': '200px',
                },
                style_cell = {
                    'text-align':'center',
                },
                style_table={
                    'overflowX': 'auto'
                }
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader([],id = 'modal-header'),
                    dbc.ModalBody([],id = 'modal-body'),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                [
                                    dcc.Link('Search', href='/search'),
                                ],
                                n_clicks=0,
                                className='ml-auto',
                            ),
                            html.Div(style ={'width':'60%','display':'inline-block'}),
                            dbc.Button("Close", id="close", className="ml-auto")
                        ],
                        style={'text-align':'left'},
                    ),
                ],
                id = "modal",
                centered=True,
            ),
        ],
    )

def manipulation_bar():
    """Manipulation bar div"""
    return html.Div(
        [
            html.Div(
                [
                    dcc.DatePickerRange(
                        id='date-picker-ranger',
                        min_date_allowed=get_min_date(),
                        max_date_allowed=get_max_date()+dt.timedelta(days=1),
                        initial_visible_month=get_max_date(),
                        end_date=get_max_date(),
                        start_date = get_min_date(),
                        updatemode = 'bothdates',
                        display_format='YYYY-MM-DD',
                        #persistence = False,
                        # persistence_type = 'memory',
                        # persisted_props = ['start_date', 'end_date'],
                    ),
                    dcc.Interval(
                        id='date_selector_interval',
                        interval=600*1000, # in milliseconds
                        n_intervals=0
                    ),
                    html.Button([],id='fake_button_to_force_refresh',style={'display':'none'},n_clicks = 1),
                ],
                id = 'date-picker-ranger-div',
                className = 'u-pv2',
            ),
            html.Div(
                [
                    dcc.Checklist(
                        options=[
                            {'label': '1 or lower', 'value': '1 or lower'},
                            {'label': '2', 'value': '2'},
                            {'label': '3', 'value': '3'},
                            {'label': '4', 'value': '4'},
                            {'label': '5', 'value': '5'},
                            {'label': 'above 5', 'value': 'above 5'},
                        ],
                        value=['2', '3','4','5','above 5'],
                        # labelClassName = 'self-checkbox-label',
                        # inputClassName = 'self-checkbox-input',
                        labelStyle = {
                                    'position':'relative',
                                    'align-items':'flex-start',
                                    'display':'inline-block',
                                    'padding-left':'3px',
                                    'padding-right':'10px',
                                    },
                        inputStyle = {
                                    'border-width':'2px',
                                    'border-color':'#00b0b2',
                                    #'padding': '5px',
                                    'display':'inline-block',
                                    },
                        id = 'consec_number_checklist',
                        style = {'text-align':'center'},
                        className = 'u-pt4',
                    ) 
                ],
                id = 'consec-number-focused-div',
                className = 'u-pb2',
            ),
        ],
        className = 'u-grid',
    )

layout = [
    html.Div(
        [
            html.A('',id='anomaly-fake-cps',style={'display':'none'}),
            # Main Content
            html.Div(
                [
                    #top: Manipulation block
                    html.Div(
                        [
                            manipulation_bar(),
                        ],
                    ),
                    #bottom: Datatable block
                    html.Div(
                        [
                            datatable(),
                        ],
                        id = 'datatable-div',
                    ),
                ],
                className="mainContent u-ph1@md u-ph3@lg",
                style = {'background':'#fff'},
            ),
        ],
    ),
]


@app.callback(
    [Output('date-picker-ranger','max_date_allowed'),
    Output('date-picker-ranger','min_date_allowed'),
    Output('date-picker-ranger','initial_visible_month'),
    Output('date-picker-ranger','start_date'),
    Output('date-picker-ranger','end_date')],
    Input('fake_button_to_force_refresh','n_clicks'),
    Input('date_selector_interval','n_intervals'),
)

def update_datepicker_periodly(n_clicks,n_intervals):
    """updating datepicker, because latest/earliest datetimes in database are changing"""
    max_date = get_max_date()
    min_date = get_min_date()
    return [max_date + dt.timedelta(days=1),min_date,max_date,min_date,max_date]

def extract_consec_false(gdf):
    """This function selects the latest notification for each unique (meter & contract acct).
    This means selecting latest notification as a representative for each customer user.

    Args:
        gdf (groupby object): each distinct (meter number & contract acct)'s notifications

    Returns:
        row: latest notification
    """
    if len(gdf) == 1:
        row = gdf.iloc[0]
    else:
        index = gdf['notification_date'].argmax()
        row = gdf.iloc[index]

    return row

@app.callback(
    Output('data_table','data'),
    [Input('date-picker-ranger','start_date'),
    Input('date-picker-ranger','end_date'),
    Input('consec_number_checklist','value'),]
)

def update_data_table(start_date,end_date,checklist):
    """Main function of consecutive_false page, render the data table.

    Args:
        start_date (str/datetime): start date
        end_date (str/datetime): end date
        checklist (list): options selected by users, determining range of consecutive false number we are looking at.

    Returns:
        data: data table
    """
    starttime = timeit.default_timer()
    DB = DBmanager()
    if (start_date is not None) & (end_date is not None):
        if type(start_date) == str:
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
        if type(end_date) == str:
            end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
        if(start_date < end_date):
            df = DB.query_in_timeperiod(start_date,end_date)
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
    
    if df.empty:
        return None
    
    print("[Anomly Page]Step 1: Fetching initial data accomplished, used time:", timeit.default_timer() - starttime)
    starttime = timeit.default_timer()
    idx = df.groupby(['meter_no','contract_acct'])['notification_date'].transform(max) == df['notification_date']
    df1 = df[idx]

    print("[Anomly Page] Step 2: Concating results finished, used time:", timeit.default_timer() - starttime)
    starttime = timeit.default_timer()
    if df1.empty:
        return None
    
    df1['consecutive_false'] = df1['consec_false_12month']
    print("[Anomly Page]Step 3: Calculating results finished, used time:", timeit.default_timer() - starttime)
    starttime = timeit.default_timer()
    drop_columns = list(set(df.columns) - set(display_columns))
    df1.drop(drop_columns,axis=1,inplace= True)

    checklist_value = []
    for i in checklist:
        if i == '1 or lower':
            checklist_value.extend([0,1])
        elif i == 'above 5':
            checklist_value.extend([6,7,8,9,10])
        else:
            checklist_value.append(int(i))
    df2 = df1[df1['consecutive_false'].isin(checklist_value)]
    print("[Anomly Page]Step 4: Truncating unneeded data finished, used time:", timeit.default_timer() - starttime)
    starttime = timeit.default_timer()
    df2 = df2.sort_values(by = 'consecutive_false',ascending= False)
    print("[Anomly Page] Final Step: Sorting finished, used time:", timeit.default_timer() - starttime)
    df2['notification_date'] = df2['notification_date'].apply(lambda x : x.strftime('%Y-%m-%d'))
    if df2.empty:
        return None
    else:
        return df2.to_dict('records')


""" Following code will not be activated in real case.
Because we can only view SHAP value base on notification number: when we click on notification number,
a pop-up window will come out and dispaly shap graph.
But in consecutive false page, we will not show notification number for now...
"""
@app.callback(
    Output("modal", "is_open"),
    [Input("data_table", "active_cell"), Input("close", "n_clicks")],
    
    State("modal", "is_open"),
        
)
def toggle_modal(n1, n2, is_open):
    allow_list = ['notification_no']
    if n1 or n2:
        if n1['column_id'] in allow_list:
            return not is_open

    return is_open

@app.callback(
    [
        Output('modal-header','children'),
        Output('modal-body','children'),
        Output('anomaly-fake-cps','children'),
    ],

    Input('data_table','active_cell'),

    [State('data_table','data'),
    State('data_table','columns')]
)

def update_modal(active_cell,rows,columns):
    """This function draws the pop up window, using information of active cell that users clicked"""
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    if df.empty:
        return [None,None,None]
    
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
                            draw_SHAP_decision_bar(shap_dict)
                        ],
                    ),
                    html.Div(
                        [
                            draw_SHAP_vicissitude_bar(shap_dict)
                        ],
                    ),

                ],
                style={'display':'flex'},
            ),
        ]
    return [header_string,body,header]

@app.callback(
    Output('anomaly-cps','data'),

    Input('anomaly-fake-cps','children'),
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
