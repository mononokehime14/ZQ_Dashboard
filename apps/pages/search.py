import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash._callback_context
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction, ALL
from urllib.parse import urlparse, parse_qs
import pandas as pd
from pathlib import Path
import math
import datetime
import timeit
import sqlalchemy


from apps.data_manager import DBmanager, Cell
from apps.app import app

display_columns = ['notification_no','meter_no','contract_acct','notification_date','cause_code','prediction']

def search_bar():
    """This function renders the search bar at the top, which contains a input bar and a search button

    Returns:
        Div: Div for rendering
    """
    return html.Div(
        [
            html.Div(
                [
                    dcc.Input(
                        id = 'search_input_content',
                        type='text',
                        placeholder='Please key in notification/account/meter number',
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
    if prediction == True:        
        return html.Span(className="healthy-search-result-dot",style={'background-color':'#e54545'})
    else:
        return html.Span(className="healthy-search-result-dot",style={'background-color':'#48dcc0'})

def output_table():
    """This draws the data table of search outputs

    Returns:
        DataTable: data table for rendering
    """
    return dash_table.DataTable(
        id='output_datatable',
        columns=[
            {"name": i, "id": i} for i in display_columns
        ],
        sort_action="native",
        page_action="native",
        page_current= 0,
        page_size= 10,
        style_data={
            'width': '16%',
        },
        style_table={
            'overflowX': 'auto'
        },
        style_cell= {
            'text-align':'center',
        },
    )

    
def search_result_display_none():
    """Displayed if there is no matching data

    Returns:
        Div: Div for rendering
    """
    return html.Div(
        [   
            html.Div(
                [
                    html.P('Ooops, no results have been found',className = 'h2',style = {'color':'#818A91'})
                ],
            ),
        ],
        className = 'lm--card u-grid-center',
        style = {'text-align':'center'},
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
                        id='display_search_result_trend_block',
                        className='u-mv1',
                        style={'width':'100%'},
                    ),
                    html.Div(
                        [
                            output_table(),    
                        ],
                        id = 'display_search_result_block',
                        className = 'u-mv1',
                        style={'width':'100%'},
                    ),
                ],
                className="mainContent u-ph1@md u-ph3@lg",
            ),
        ],
    ),
]


@app.callback(
    [
        Output('trend_graph_div','children'),
        Output('output_datatable','data'),
    ],

    [
        Input('search_button','n_clicks'),
        Input('search_input_content','value')
    ],

    [
        State('records-cps','data'),
        State('anomaly-cps','data'),
    ]
)

def update_search_result(n_clicks,input_value,records_cps,anomaly_cps):
    """This is the main funciton of search page, display search results

    Args:
        n_clicks (int): clicking times of the search button
        input_value (str): user input
        records_cps (str): passed from records page (during jumping from records page to search page)
        anomaly_cps (str): passed from anomaly page (during jumping from anomaly page to search page)

    Returns:
        list: list of objects to render
    """
    if input_value is None:
        if records_cps is None:
            if anomaly_cps is None:
                return [None,None]
            else:
                print('Search page receive input from records:' + anomaly_cps)
                input_value = anomaly_cps

        else:
            print('Search page receive input from anomaly:' + records_cps)
            input_value = records_cps


    # if (input_value is None) | (n_clicks <= 0):
    #     return [None,None]

    DB = DBmanager()
    output = DB.query(input_value)


    if output.empty:
        return [None,None]

    # output_display = []
    # output.apply(lambda x: turn_into_display_list(x,output_display),axis = 1)
    output = output.sort_values(by = 'notification_date',ascending=True,axis =0)
    drop_columns = list(set(output.columns) - set(display_columns))
    output_display = output.drop(drop_columns,axis=1)
    output_display['notification_date'] = output_display['notification_date'].apply(lambda x : x.strftime('%Y-%m-%d'))
    #false_count = 0
    #output['prediction_in_number'] = output['prediction'].apply(lambda x: turn_prediction_to_number(x,false_count))
    x = output['notification_date']
    y = output['consec_false_12month']
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = x,
            y = y,
            name = 'linear',
            line_shape = 'hvh',
        )
    )
    fig.update_traces(
        mode = 'lines+markers',
    )
    fig.update_layout(
        margin = dict(t=10,r=5,l=5,b=10),
        yaxis = dict(
            tickmode = 'array',
            tickvals = y.unique(),
            zeroline = True,
            showgrid =  False,
            showline = True,
            linecolor = '#4F5A60',
            title_text = 'Prediction',
        ),
        xaxis = dict(
            tickmode = 'array',
            tickvals = x,
            showgrid = False,
            showspikes = True,
            showline = True,
            linecolor = '#4F5A60',
            title_text = 'Time',
        ),
        paper_bgcolor = '#fff',
        plot_bgcolor = '#fff',
    )
    trend_graph = [
        dcc.Graph(
            id = 'trend_graph_plot',
            figure = fig,
            config={'displayModeBar': False,
                    'responsive': True},
            style = {'width':'100%','height':'200px'},
        )
    ]
    return [trend_graph, output_display.to_dict('record')]
    # else:
    #     return [None,None]
    
