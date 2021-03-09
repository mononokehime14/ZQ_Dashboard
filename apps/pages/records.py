import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction
import pandas as pd
from pathlib import Path
import math
import datetime as dt
import urllib.parse
import sqlalchemy
import timeit

from apps.data_manager import DBmanager,Cell
from apps.app import app

display_columns = ['notification_no','notification_date','contract_acct','cause_code','meter_no','prediction','consecutive_false']

def draw_datatable():
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
def get_max_date():
    DB = DBmanager()
    max_date = DB.find_max_date()
    max_date = dt.datetime.strftime(max_date,"%Y-%m-%d")
    return max_date

def get_min_date():
    DB = DBmanager()
    min_date = DB.find_min_date()
    min_date = dt.datetime.strftime(min_date,"%Y-%m-%d")
    return min_date

def draw_upper_block():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
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
                                                style = {'width':'100px','height':'44px'},
                                            ),
                                            dcc.Interval(
                                                id='date_selector_interval',
                                                interval=600*1000, # in milliseconds
                                                n_intervals=0
                                            ),
                                        ],
                                        id = 'date_selector_div',
                                        className = 'col-sm-3 col-md-3 col-lg-3 col-xl-3 u-cell',
                                    ),
                                    html.Div(
                                        [
                                            dcc.Dropdown(
                                                id='consecutive_false_trace',
                                                options=[
                                                    {'label': 'Last week', 'value': 'last week'},
                                                    {'label': 'Last month', 'value': 'last month'},
                                                    {'label': 'Last three month', 'value': 'last three month'},
                                                    {'label':'Last Year','value':'last year'},
                                                    {'label':'All Time','value':'all time'},
                                                ],
                                                value='all time',
                                                style = {'width':'120px','height':'44px'},
                                            ),
                                        ],
                                        id = 'consecutive_false_trace_div',
                                        className  = 'col-sm-3 col-md-3 col-lg-3 col-xl-3 u-cell',
                                    ),
                                    html.Div(
                                        [
                                            html.Button(
                                                'Apply',
                                                id= 'date_selector_button',
                                                n_clicks = 0,
                                                className = 'lm--button--primary u-mt1',
                                                style = {'height':'40px','width':'80px'}
                                            ),
                                        ],
                                        id = 'date_selector_button_div',
                                        className = 'col-sm-2 col-md-2 col-lg-2 col-xl-2 u-cell',
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
                                        id = 'csv_download_button_div',
                                        className = 'col-sm-2 col-md-2 col-lg-2 col-xl-2 u-cell',
                                    ),
                                ],
                                className = 'u-grid',
                            ),  
                            html.Div(
                                [
                                    html.P('Select a date to check its records',
                                            className = 'h4',
                                            id='date_selector_output',
                                            style={'color':'#4F5A60'},
                                    )
                                ],
                                style = {'width':'100%'},
                            ),
                        ],
                        style = {'display':'block','height':'100%'}
                    ),
                ],
                className = 'col-sm-6 col-md-6 col-lg-6 col-xl-6 u-cell',
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [

                                        ],
                                        id = 'little_chart',
                                        className = 'col-sm-2 col-md-2 col-lg-2 col-xl-2 u-cell',
                                    ),
                                    html.Div(
                                        [
                                            html.P("", className="h4",id = 'little_chart_label')
                                        ],
                                        className = 'col-sm-8 push-sm-2 col-md-8 push-md-2 col-lg-8 push-lg-2 push-xl-2 col-xl-8 u-cell',
                                        style = {'display':'flex','text-align':'center'}
                                    ),
                                ],
                                className = 'u-grid',
                            )
                        ],
                        
                        style = {'text-align':'right'}
                    ),
                ],
                className = 'col-sm-3  col-md-3  col-lg-3 col-xl-3 u-cell',
            ),
        ],
        className = 'lm--card u-pv2 u-grid',
    )                           
                                

layout = [
    html.Div(
        [
            dcc.Store(id="temp_for_download",storage_type='local'),
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
                            html.Div(
                                [

                                ],
                                id = 'display_right_block',
                            )
                        ],
                        id = 'check_records_display_block',
                    ),
                ],
                className="mainContent u-ph1@md u-ph3@lg u-ph5@xl",
            ),
        ],
    ),
]

def generate_little_chart(true_count, false_count):
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
    Output('date_selector_output','children'),

    Output('little_chart','children'),
    Output('little_chart_label','children'),
    
    #Output('temp_for_download','data')
    Output('download-link', 'href'),
    ],

    [Input('date_selector_single','date'),
    Input('date_selector_button','n_clicks'),
    Input('consecutive_false_trace','value'),
    Input('csv_download_button','n_clicks')],

    #State('memory-value','data')
)

def update_records(start_date,n_clicks,trace_option,download_clicks):
    if(n_clicks>0) & (start_date is not None):
        #df = pd.read_json(df,orient="split")
        starttime = timeit.default_timer()
        # conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
        # engine = sqlalchemy.create_engine(conn_url)
        # df = pd.read_sql_table('notificationlist',con = engine)

        # df['notification_date'] = pd.to_datetime(df['notification_date'])
        # df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')
        if type(start_date) == str:
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
        if trace_option == 'last week':
            end_date = start_date - dt.timedelta(days=7)
        elif trace_option == 'last month':
            end_date = start_date - dt.timedelta(days=30)
        elif trace_option == 'last three month':
            end_date = start_date - dt.timedelta(days=90)
        elif trace_option == 'last year':
            end_date = start_date - dt.timedelta(days=365)
        elif trace_option == 'all time':
            end_date = get_min_date()
        else:
            return [None,'You have not chosen trace period',None,'','']

        # df['meter_contract_no'] = df['meter_no'] + df['contract_acct']
        # combine_list = df[df['notification_date'] == start_date]['meter_contract_no'].tolist()
        # dff = df[(df['notification_date'] <= start_date) & (df['notification_date'] >= end_date) & (df['consecutive_false'] != 0) & (df['meter_contract_no'].isin(combine_list))]
        # consecutive_false_dic = {}
        # dfff = dff.groupby(['meter_no','contract_acct'])
        # for index,row in dfff:
        #     row.sort_values(by = 'notification_date')
        #     false_count = 0
        #     for index,row2 in row.iterrows():
        #         if row2['prediction'] == 'False':
        #             false_count += 1
        #         elif row2['prediction'] == 'True':
        #             false_count = 0
        #     for i in row['notification_no']:
        #         consecutive_false_dic[i] = false_count
        # for index,row in dff.iterrows():
        #     df.loc[index,'consecutive_false'] = consecutive_false_dic[row['notification_no']]
        # dff = dff[dff['notification_date'] == start_date]
        # df = df[(df['notification_date'] == start_date) & (df['consecutive_false'] == 0)]
        # df = pd.concat([df,dff])     
        DB = DBmanager()
        #DB.update_consecutive_false()
        df = DB.trace_records(start_date,end_date)  
        label = f'You have chosen date: {start_date}; Trace back to: {trace_option}'
        if df is not None:  
            drop_columns = list(set(df.columns) - set(display_columns))
            df.drop(drop_columns,axis=1,inplace= True)
            df = df.sort_values(by = 'consecutive_false',ascending= False)
            true_count = len(df[df['prediction'] == True].index)
            false_count = len(df.index) - true_count            
            rate = int((true_count / (true_count + false_count)) * 100)
            fig = generate_little_chart(true_count,false_count)
            chart_content = [dcc.Graph(
                figure=fig,
                style={'width': '48px','height':'48px'},
            )]
            csv_string = df.to_csv(index=False, encoding='utf-8')
            csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
            print("All things acomplished, used time:", timeit.default_timer() - starttime)
            #df.to_json(orient='split',date_format='iso')
            return [df.to_dict('records'),label,chart_content,f'True Prediction Rate: {rate}%',csv_string]
        else:
            return [None,label,None,'There is no records on that day','']
    return [None,'Select a date to check its records',None,'','']

@app.callback(
    [Output('date_selector_single','max_date_allowed'),
    Output('date_selector_single','min_date_allowed')],
    Input('date_selector_interval','n_intervals'),
)

def update_max_min_date(n_intervals):
    return [get_max_date(),get_min_date()]
# @app.callback(
#     Output('download-link', 'href'),
#     Input('csv_download_button','n_clicks'),
#     State('temp_for_download','data')
# )

# def try_update(n_clicks,df):
#     #df = pd.read_json(df, orient="split")
#     #print(df.head(5))
#     if (df is not None) & (n_clicks > 0):
#         print('chenggong')
#         df = pd.read_json(df, orient="split")
#         #df['notification_date'] = df['notification_date'].apply(lambda x : x.strftime('%Y-%m-%d'))
#         csv_string = df.to_csv(index=False, encoding='utf-8')
#         csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
#         print(csv_string)
#         return csv_string

# @app.callback(
#     Output('download-link', 'href'),
#     Input('csv_download_button','n_clicks'),
#     State('temp_for_download','data')
# )

# def suibian(n_clicks,df):
#     DB = DBmanager()
#     if df is None:
#         df = DB.query('qwer')
#     else:
#         df = pd.DataFrame(columns = display_columns)
#     csv_string = df.to_csv(index=False, encoding='utf-8')
#     csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
#     return csv_string
    
