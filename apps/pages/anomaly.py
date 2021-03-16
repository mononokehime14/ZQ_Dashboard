import io
import urllib.parse
import base64
import json
import timeit


import dash_core_components as dcc
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
from apps.pages.records import display_columns
from apps.pages.records import get_max_date, get_min_date

def datatable():
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
                    'width': '10%',
                    'maxWidth': '100px',
                    'minWidth': '100px',
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'notification_date'},
                        'width': '15%'
                    },
                    {
                        'if': {'column_id': 'cause_code'},
                        'width': '15%'
                    },
                ],
                style_table={
                    'overflowX': 'auto'
                }
            ),
        ]
    )

def manipulation_bar():
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
                        id = 'consec_number_checklist',
                    ) 
                ],
                id = 'consec-number-focused-div',
            ),
        ],
    )

layout = [
    html.Div(
        [
            # Main Content
            html.Div(
                [
                    #left: Datatable block
                    html.Div(
                        [
                            datatable(),
                        ],
                        id = 'datatable-div',
                    ),
                    #right: Manipulation block
                    html.Div(
                        [
                            manipulation_bar(),
                        ],
                    ),
                ]
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
    max_date = get_max_date()
    min_date = get_min_date()
    return [max_date + dt.timedelta(days=1),min_date,max_date,min_date,max_date]

def extract_consec_false(gdf,start_date):
    # gdf = gdf.sort_values(by='notification_date', descending=True)
    if len(gdf) == 1:
        row = gdf.iloc[0]
    else:
        index = gdf['notification_date'].argmax()
        row = gdf.iloc[index]
    
    row_date = row['notification_date']
    date_buoy = start_date 
    loop_count = 0
    if date_buoy == row_date:
        pass
    else:
        date_buoy += relativedelta(months=+1)
        while (date_buoy <= row_date) & (loop_count < 12):
            date_buoy += relativedelta(months=+1)
            loop_count += 1
    
    if loop_count >= 12:
        pass
    else:
        row['consecutive_false'] = row['consec_false_{}month'.format(str(loop_count + 1))]
    return row

@app.callback(
    Output('data_table','data'),
    [Input('date-picker-ranger','start_date'),
    Input('date-picker-ranger','end_date'),
    Input('consec_number_checklist','value'),]
)

def update_data_table(start_date,end_date,checklist):
    starttime = timeit.default_timer()
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
        end_date = get_max_date()
        end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")
    
    if df.empty:
        return None
    
    print("[Anomly Page]Step 1: Fetching initial data accomplished, used time:", timeit.default_timer() - starttime)
    starttime = timeit.default_timer()
    group_dfs = []
    for n, g in df.groupby(['meter_no', 'contract_acct']):
        _  = extract_consec_false(g,start_date)
        group_dfs.append(_)

    df1 = pd.DataFrame()
    df1 = df1.append(group_dfs)
    print(df1.head(10))
    print("[Anomly Page] Step 2: Calculating results finished, used time:", timeit.default_timer() - starttime)
    starttime = timeit.default_timer()
    if df1.empty:
        return None

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
    print("[Anomly Page]Step 3: Truncating unneeded data finished, used time:", timeit.default_timer() - starttime)
    starttime = timeit.default_timer()
    df2 = df2.sort_values(by = 'consecutive_false',ascending= False)
    print("[Anomly Page] Final Step: Sorting finished, used time:", timeit.default_timer() - starttime)
    if df2.empty:
        return None
    else:
        return df2.to_dict('records')

