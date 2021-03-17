import dash_core_components as dcc
import dash_bootstrap_components as dbc
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
                    'width': '14%',
                    'maxWidth': '100px',
                },
                style_cell = {
                    'text-align':'center',
                },
                # style_cell_conditional=[
                #     {
                #         'if': {'column_id': 'notification_date'},
                #         'width': '15%'
                #     },
                #     {
                #         'if': {'column_id': 'cause_code'},
                #         'width': '15%'
                #     },
                # ],
                style_table={
                    'overflowX': 'auto'
                }
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader([],id = 'records-modal-header'),
                    dbc.ModalBody([],id = 'records-modal-body'),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close", className="ml-auto")
                    ),
                ],
                id = "records-modal",
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
                                value='all time',
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
    if (start_date is not None) & (trace_option is not None):
        #df = pd.read_json(df,orient="split")
        starttime = timeit.default_timer()
        # conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
        # engine = sqlalchemy.create_engine(conn_url)
        # df = pd.read_sql_table('notificationlist',con = engine)

        # df['notification_date'] = pd.to_datetime(df['notification_date'])
        # df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')
        if type(start_date) == str:
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
            max_date = dt.datetime.strptime(max_date,"%Y-%m-%d")
            min_date = dt.datetime.strptime(min_date,"%Y-%m-%d")
            if (start_date > max_date) | (start_date < min_date):
                return [None,None,'Date selected exceeds range= =',None,None]
   
        DB = DBmanager()
        #DB.update_consecutive_false()
        df = DB.trace_records(start_date)
        
        if df is not None: 

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
    max_date = get_max_date()
    min_date = get_min_date()
    return [max_date,min_date,max_date,max_date]

@app.callback(
    Output("records-modal", "is_open"),
    [Input("datatable", "active_cell"), Input("close", "n_clicks")],
    [State("records-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    [Output('records-modal-header','children'),
    Output('records-modal-body','children')],
    Input('datatable','active_cell'),
    [State('datatable','data'),
    State('datatable','columns')]
)

def update_modal(active_cell,rows,columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    if df.empty:
        return [None,None]
    
    header = df.iloc[active_cell['row'],active_cell['column']]
    header = str(header)
    body = 'The SHAP graph has not been implemented yet~'
    return [header,body]

