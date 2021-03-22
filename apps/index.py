import datetime
from dateutil import tz
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import pandas as pd
import re

from apps.app import app
from apps.data_manager import DBmanager, Cell
from apps.pages import summary, search, records, anomaly
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

def serve_layout():
    return html.Div(
        [
            #dcc.Store(id="memory-value", data=df.to_json(orient='split',date_format='iso')),
            dcc.Store(id = 'records-cps',data = None),
            dcc.Store(id = 'anomaly-cps',data = None),
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
        "/anomaly": {
            "title": "Anomaly",
            "layout": anomaly.layout
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
