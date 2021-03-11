import datetime
from dateutil import tz
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import pandas as pd
import re

from apps.app import app
from apps.data_manager import DBmanager,Cell
from apps.pages import summary,search,records
#from ..user import VALID_USERNAME_PASSWORD_PAIRS
from apps.settings import VALID_PASSWORD, VALID_USER

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask
import timeit

# import os
# import pprint
# pprint.pprint(dict(os.environ),width = 1)
# os.environ['DB_url'] = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
# print(os.environ['DB_url'])

server = app.server

VALID_USERNAME_PASSWORD_PAIRS = {
    VALID_USER: VALID_PASSWORD
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
#DB = DBmanager()
# DB.start_over()
#DB.update_consecutive_false_for_whole()
# conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
# engine = sqlalchemy.create_engine(conn_url)
# df = pd.read_sql_table('notificationlist',con = engine)

# df = pd.read_csv('data/combined.csv',parse_dates=['notification_date'],dayfirst=True)
# df['notification_date'] = pd.to_datetime(df['notification_date'])
# #df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')

# def find_consecutive_false(group):
#     if(len(group) > 1):
#         group = group.sort_values(by = 'notification_date',ascending = True)
#         false_count = 0
#         for index,row2 in group.iterrows():
#             if row2['prediction'] == 'False':
#                 false_count += 1
#             elif row2['prediction'] == 'True':
#                 false_count = 0
#             consecutive_false_dic[row2['notification_no']] = false_count
#     else:
#         for i in group['notification_no']:
#             consecutive_false_dic[i] = 0
#     return 0

# if 'consecutive_false' not in df.columns:
#     print('kaishi gengixng')
#     consecutive_false_dic = {}
#     starttime = timeit.default_timer()
#     print("The start time is :",starttime)
#     df.groupby(['meter_no','contract_acct']).apply(lambda x: find_consecutive_false(x))
#     print("The time difference is :", timeit.default_timer() - starttime)

#     starttime = timeit.default_timer()
#     print("The start time is :",starttime)
#     df['consecutive_false']= df['notification_no'].apply(lambda x: consecutive_false_dic[x])
#     print("The time difference is :", timeit.default_timer() - starttime)
#     df['notification_date'] = df['notification_date'].apply(lambda x : x.strftime('%Y-%m-%d'))
#     #df.to_sql('notificationlist',con=engine,if_exists='replace')

#     print("The time difference is :", timeit.default_timer() - starttime)

# print(df['prediction'].unique())
def serve_layout():
    return html.Div(
        [
            #dcc.Store(id="memory-value", data=df.to_json(orient='split',date_format='iso')),

            # represents the URL bar, doesn't render anything
            dcc.Location(id='url', refresh=False),

            # Header Navigation Bar
            html.Div(
                html.Nav(
                    [
                        html.Div(
                            html.Img(
                                src=app.get_asset_url("spgroup-logo.png"),
                                id="spgroup-logo",
                            ),
                            className="lm--header-logo u-hidden@sm"
                        ),
                        html.Nav(
                            html.Ul(
                                [],
                                id="nav-tabs",
                                className="lm--tabs-nav",
                                style={"height": "100%"},
                            ),
                            **{
                                'data-tabs': '',
                            }
                        ),
                        html.Ul(
                            html.Li(
                                [
                                    html.Div(
                                        id="current_datetime_display"
                                    ),
                                    dcc.Interval(
                                        id="interval-component",
                                        interval=1*1000, # in milliseconds
                                        n_intervals=0
                                    ),
                                ],
                                className="u-hidden@sm"
                            ),
                            className="lm--header-menu lm--header-menu--secondary",
                        )
                    ],
                    className="lm--header-nav",
                ),
                className="lm--header u-mb0 u-bb",
            ),

            html.Div(id="pageContent"),
        ]
    )




@app.callback(Output('current_datetime_display', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_date(n):
    now = datetime.datetime.utcnow().astimezone(tz.gettz('Asia/Singapore'))
    return [
        html.P(now.strftime("%A"), style={"margin": "0"}),
        html.P(now.strftime("%d %B %Y"), style={"margin": "0"}),
        html.P(now.strftime("%I:%M:%S %p"), style={"margin": "0"}),
    ]



# Handle navigation tabs
@app.callback(
    [Output("pageContent", "children"),
     Output("nav-tabs", "children")],
    [Input("url", "pathname")],
)
def display_page(pathname):
    pages = {
        "/": {
            "title": "Summary",
            "layout": summary.layout
        },
        "/search": {
            "title": "Query",
            "layout": search.layout
        },
        "/records": {
            "title": "Records",
            "layout": records.layout
        },
    }

    tabs = [
        html.Li(
            dcc.Link(
                html.Span(pages.get(path).get("title"), className="nav-tab-text"),
                href=path,
                className="lm--tabs-link"
            ),
            className="lm--tabs-item is-active" if path==pathname else "lm--tabs-item",
            style={"height": "100%"}
        )
        for path in pages
    ]

    page_item = pages.get(pathname, {})
    layout = page_item.get("layout", [
            # Title Bar
            html.Div(
                html.Nav(
                    html.H1("Error 404: Page Not Found", className="u-pl4 u-mb0"),
                    className="lm--header-nav",
                ),
                className="lm--header u-mb0 u-bb",
                style={"margin-top": "3px", "padding": "8px 0"},
            ),
    ])

    return layout, tabs

app.layout = serve_layout

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port='8425')
