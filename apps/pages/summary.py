import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction
import pandas as pd

from app import app
from settings import MAPBOX_ACCESS_TOKEN




def substation_health_card(title, id_prefix, additional_classnames=""):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(html.P(title, className="h2")),
                        ],
                        className="lm--card-item",
                    ),
                    html.Div(
                        [
                            html.Div([html.P("Attention Needed", className="h5")]),
                            html.Span(id=f"{id_prefix}_dot_indicator", className="alert-dot"),
                            html.Span(id=f"{id_prefix}_alert_value", className="mini_container_value"),
                        ],
                        className="lm--card-item u-pb0",
                    ),
                    html.Div(
                        [
                            html.Div([html.P("Healthy", className="h5")]),
                            html.Span(className="healthy-dot"),
                            html.Span(id=f"{id_prefix}_healthy_value", className="mini_container_value"),
                        ],
                        className="lm--card-item u-pt0",
                    ),
                ],
                className="col u-cell",
                style={"text-align": "right", "width": "50%"},
            ),
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
        ],
        className="lm--card " + additional_classnames,
        style={"height": "100%"},
    )


def substation_map_card():
    return html.Div(
        [
            html.Div(
                dcc.Graph(id="mapbox", config={'displayModeBar': False, 'responsive': True}, clear_on_unhover=True, className="lm--card-item"),
                id="mapbox_container",
                className="lm--card-item col-sm-12 col-md-12 u-cell",
            )
        ],
        className="lm--card",
        style={"height": "100%"}
    )




def equipment_health_card(network, eq_type, ok_count, ok_percentage, alarm_count, alarm_percentage):
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
                                            html.Div(html.P(f"{network} {eq_type}s", className="h2 u-pl0")),
                                        ],
                                        className="lm--card-item col-sm-12 u-cell",
                                    ),
                                    html.Div(
                                        [
                                            html.Div([html.P("Attention Needed", className="h5")]),
                                        ],
                                        className="lm--card-item col-sm-12 u-cell u-pt1 u-pb0",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        [],
                                                        title=f"{alarm_percentage}%",
                                                        style={"width": f"{max(alarm_percentage, 4) if alarm_count>0 else 0}%", "height": "100%", "background-color": "var(--color-red)", "display": "inline-block"},
                                                    ),
                                                ],
                                                title=f"{alarm_percentage}%",
                                                style={"height": "80%", "background-color": "var(--color-grey100)"},
                                            ),
                                        ],
                                        className="lm--card-item col u-cell u-pt0 u-pr0",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(f"{alarm_count}", className="mini_container_value u-p0", style={"line-height": "normal"}),
                                        ],
                                        className="lm--card-item u-cell u-pt0",
                                        style={"width": "90px"},
                                    ),

                                    html.Div(
                                        [
                                            html.Div([html.P("Healthy", className="h5")]),
                                        ],
                                        className="lm--card-item col-sm-12 u-cell u-pt1 u-pb0",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        [],
                                                        title=f"{ok_percentage}%",
                                                        style={"width": f"{max(ok_percentage, 4) if ok_count>0 else 0}%", "height": "100%", "background-color": "var(--color-green)", "display": "inline-block"},
                                                    ),
                                                ],
                                                title=f"{ok_percentage}%",
                                                style={"height": "80%", "background-color": "var(--color-grey100)"},
                                            ),
                                        ],
                                        className="lm--card-item col u-cell u-pt0 u-pr0",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(f"{ok_count}", className="mini_container_value u-p0", style={"line-height": "normal"}),
                                        ],
                                        className="lm--card-item u-cell u-pt0",
                                        style={"width": "90px"},
                                    ),

                                ],
                                className="u-grid",
                                style={"width": "100%"},
                            ),
                        ],
                        className="lm--card u-p4",
                        style={"width": "100%"},
                    ),
                ],
                className="lm--card",
            ),
        ],
        className="col-sm-12 col-xl-auto u-cell u-p1",
        style={"min-width": "304px"}
    )



def equipment_list_table(network, eq_type, test_type, df):
    return html.Div(
        [
            html.P(test_type, className="h4 u-pt4"),
            dcc.Link(
                [
                    dash_table.DataTable(
                        columns=[{"name": i.capitalize(), "id": i} for i in df.columns],
                        data=df.to_dict("records"),
                        # css=[{"selector": "tr:first-child", "rule": "text-align: left",}],
                        style_data={"border": "0", "font-family": "var(--font-sans-serif)"},
                        style_cell={"color": "black", "textAlign": "left", "font-size": "0.8rem"},
                        style_as_list_view=True,
                        page_size=5,
                        style_table={"height": "auto", 'overflowY': 'auto'},
                        style_data_conditional=[
                            {
                            'if': {
                                    'filter_query': '{health} = "Alarm"'
                                },
                                'backgroundColor': '#FDD4D5',
                            },
                            {
                                'if': {
                                    'state': 'selected'  # 'active' | 'selected'
                                },
                               'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                               'border': '0',
                            }
                        ],
                        id=f"{network.lower()}_{eq_type.lower()}_{test_type.replace(' ','_').lower()}_datatable",
                    )
                ],
                href="/equipment?serialNo=TE3501-034",
            ),
        ],
        className="col-sm-12 u-pb4",
        style={"height": "auto"},
    ),


def equipment_list_card(network, equip_type, divs_by_test_type):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div([html.P(f"{network} {equip_type} Details")]),
                                ],
                                className="lm--card-item h2",
                            ),
                        ],
                        className="lm--card-item col-sm-12 col-md-12 u-cell u-pb0",
                    ),
                    html.Div(
                        [
                            html.Div(
                                divs_by_test_type,
                                className="lm--card-item col-sm-12 u-pt0"
                            ),
                        ],
                        className="lm--card-item col-sm-12 col-md-12 u-cell u-ph5 u-pt0",
                    ),

                ],
                className="lm--card u-mt2",
            ),
        ],
        className="u-pb1",
    ),














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
                                                [
                                                    html.Div([html.P("Substations")], className="h1 u-mb0")
                                                ],
                                                className="lm--card pageSectionHeaderCard",
                                            ),
                                        ],
                                        className="u-pb1",
                                    ),
                                ],
                                className="col-sm-12 col-md-12 u-cell u-pt3",
                            ),
                        ],
                        className="u-grid u-pt4 u-ph2"
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        substation_map_card(),
                                        className="col u-pt2",
                                        id="substation_map",
                                    ),
                                ],
                                className="col-sm-12 col-md-auto u-cell u-pt0 u-pb1 u-ph0@sm u-ph1@md u-pr1@lg",
                                style={"height": "100%"},
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                substation_health_card("Source Stations", "source_stations"),
                                                className="col-sm-12 col-md-6 u-cell u-pb1 u-pt0@sm u-ph0@sm u-ph1@md u-pr2@md",
                                            ),
                                            html.Div(
                                                substation_health_card("CBD Stations", "cbd"),
                                                className="col-sm-12 col-md-6 u-cell u-pb1 u-pt2@sm u-ph0@sm u-ph1@md u-pl1@md",
                                            ),
                                            html.Div(
                                                substation_health_card("Priority Stations", "priority_stations"),
                                                className="col-sm-12 col-md-6 u-cell u-pt2 u-pb1 u-ph0@sm u-ph1@md u-pr2@md",
                                            ),
                                            html.Div(
                                                substation_health_card("All Other Stations", "all_other_stations"),
                                                className="col-sm-12 col-md-6 u-cell u-pt2 u-pb1 u-ph0@sm u-ph1@md u-pl1@md",
                                            ),
                                        ],
                                        className="u-grid",
                                        style={"height": "100%"},
                                    )
                                ],
                                id="substation_health_cards",
                                className="col-sm-12 col-md-auto u-cell u-pt2@sm u-pt2@md u-pl3@lg",
                            ),
                        ],
                        className="u-grid u-ph3 u-pt0 u-pb2",
                    ),


                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            # TRANSMISSION NETWORK
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.Div(
                                                                        [
                                                                            html.Div(
                                                                                [
                                                                                    html.Div([html.P("Transmission Network")], className="h1 u-mb0")
                                                                                ],
                                                                                className="lm--card pageSectionHeaderCard",
                                                                            ),
                                                                        ],
                                                                        className="u-pb1",
                                                                    ),
                                                                    html.Div(
                                                                        [
                                                                            html.Div(
                                                                                [],
                                                                                id="tn_equipment_health_chart_div",
                                                                                className="u-grid u-mt0 u-ph2 u-pt2",
                                                                            ),
                                                                        ],
                                                                        className="u-pb0",
                                                                    ),
                                                                    html.Div(
                                                                        [],
                                                                        id="transmission_network_alerts_cards",
                                                                    ),
                                                                ],
                                                                # className="col-sm-12 col-md-6 u-cell u-pt0",
                                                            ),
                                                        ],
                                                        className="u-ph0@sm u-pr4@md u-pt4 u-pb2",
                                                    ),
                                                ],
                                                className="col-sm-12 col-md-6 u-cell u-pt4 u-ph1",
                                            ),

                                            # DISTRIBUTION NETWORK
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.Div(
                                                                        [
                                                                            html.Div(
                                                                                [
                                                                                    html.Div([html.P("Distribution Network")], className="h1 u-mb0")
                                                                                ],
                                                                                className="lm--card pageSectionHeaderCard",
                                                                            ),
                                                                        ],
                                                                        className="u-pb1",
                                                                    ),
                                                                    html.Div(
                                                                        [
                                                                            html.Div(
                                                                                [],
                                                                                id="dn_equipment_health_chart_div",
                                                                                className="u-grid u-mt0 u-ph2 u-pt2",
                                                                            ),
                                                                        ],
                                                                        className="u-pb0",
                                                                    ),
                                                                    html.Div(
                                                                        [],
                                                                        id="distribution_network_alerts_cards",
                                                                    ),
                                                                ],
                                                            ),
                                                        ],
                                                        className="u-ph0@sm u-pl4@md u-pt4 u-pb2",
                                                    ),
                                                ],
                                                className="col-sm-12 col-md-6 u-cell u-pt4 u-ph1",
                                            ),
                                        ],
                                        className="u-grid",
                                        style={"height": "100%"},
                                    )
                                ],
                                id="equipment_health_cards",
                                className="col-sm-12 u-cell",
                            ),
                        ],
                        className="u-grid u-ph3",
                    ),

                ],
                className="mainContent u-ph1@md u-ph3@lg",
            ),
        ],
    ),
]












def generate_donut_chart(alarm_count, ok_count):
    labels = ['Attention Needed','Healthy']

    fig = go.Figure(data=[go.Pie(labels=labels, values=[alarm_count, ok_count], direction="clockwise", sort=False, hole=.76)])

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


def generate_substation_health_card_values(fig, total_count, ok_count, alarm_count):
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
    ], "inactive-dot" if alarm_count==0 else "alert-dot", [f"{ok_count}"], [f"{alarm_count}"]


@app.callback(
    [
        # Source Stations
        Output("source_stations_chart_div", "children"),
        Output("source_stations_dot_indicator", "className"),
        Output("source_stations_healthy_value", "children"),
        Output("source_stations_alert_value", "children"),

        # CBD Stations
        Output("cbd_chart_div", "children"),
        Output("cbd_dot_indicator", "className"),
        Output("cbd_healthy_value", "children"),
        Output("cbd_alert_value", "children"),

        # Priority Stations
        Output("priority_stations_chart_div", "children"),
        Output("priority_stations_dot_indicator", "className"),
        Output("priority_stations_healthy_value", "children"),
        Output("priority_stations_alert_value", "children"),

        # All Other Substations
        Output("all_other_stations_chart_div", "children"),
        Output("all_other_stations_dot_indicator", "className"),
        Output("all_other_stations_healthy_value", "children"),
        Output("all_other_stations_alert_value", "children"),
    ],
    [
        Input("dummy_store", "data"),
    ])
def substation_health_charts_callback(df):
    df = pd.read_json(df, orient="split")

    charts = ["source_stations", "cbd_stations", "priority_stations", "all_other_stations"]

    output = []

    for type in charts:
        total_count = 123
        alarm_count = 11
        ok_count = 112

        fig = generate_donut_chart(alarm_count, ok_count)
        content = generate_substation_health_card_values(fig, total_count, ok_count, alarm_count)
        output.extend(content)

    return output











@app.callback(
    [
        Output("tn_equipment_health_chart_div", "children"),
        Output("dn_equipment_health_chart_div", "children")
    ],
    [
        Input("dummy_store", "data"),
    ])
def equipment_health_chart_callback(df):
    df = pd.read_json(df, orient="split")

    output = []

    networks = ["TN", "DN"]

    for network in networks:
        # nw_df = df[df["network"]==network]
        # eq_types_list = nw_df["equipment_type"].unique()
        eq_types_list = ["transformer", "switchgear"]

        chart = []

        for eq_type in eq_types_list:
            # eq_filter = nw_df["equipment_type"]==eq_type

            # total_count = nw_df[eq_filter].nunique()["serialNo"]
            #
            # cols_to_check = meta_df[(meta_df["network"]==network) & (meta_df["equipment"]==eq_type)]["column_name"].to_list()
            # all_false = [False]*len(nw_df.index)
            # alarm_condition = all_false if not cols_to_check else nw_df[f"alarm_{cols_to_check[0]}"]==1
            # no_test_record_condition = all_false if not cols_to_check else nw_df[f"alarm_{cols_to_check[0]}"].isnull()
            # for col in cols_to_check:
            #     alarm_condition = (alarm_condition) | (nw_df[f"alarm_{col}"]==1)
            #     no_test_record_condition = (no_test_record_condition) & (nw_df[f"alarm_{col}"].isnull())
            #
            # alarm_count = nw_df[(eq_filter) & (alarm_condition)].nunique()["serialNo"]
            # no_test_record_count = nw_df[(eq_filter) & (no_test_record_condition)].nunique()["serialNo"]
            # ok_count = total_count - alarm_count - no_test_record_count
            #
            # # if no alarm record for a substation, assume that substation is healthy
            # ok_count += no_test_record_count

            total_count = 999
            alarm_count = 99
            ok_count = 900

            ok_percentage = round((ok_count/total_count)*100, 1)
            alarm_percentage = round((alarm_count/total_count)*100, 1)

            chart.append(
                equipment_health_card(network, eq_type.capitalize(), ok_count, ok_percentage, alarm_count, alarm_percentage)
            )

        output.append(chart)

    return output










# generate map chart
def generate_graph(lat=['1.3521', '1.3711'], lon=['103.8198', '103.7898'], text=['s11111111', 's222222222'], customdata=None):
    fig = go.Figure(go.Scattermapbox(
        lat=lat,
        lon=lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color="#e54545",
        ),
        text=text,
        textposition="top center",
        # hovertemplate="<b>%{text}</b> [%{customdata[0]}]<br>" \
        #               + "<i>%{customdata[1]}</i><br><br>" \
        #               + "Type: %{customdata[2]}, " \
        #               + "Zone: %{customdata[3]}<br>" \
        #               + "<extra></extra>",
        customdata=customdata,
    ))
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, b=0, t=0),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="white"
        ),
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            style="basic",
            center=go.layout.mapbox.Center(
                lat=1.3450,
                lon=103.8198
            ),
            zoom=10.3,
        )
    )
    return fig


@app.callback(
    Output("mapbox", "figure"),
    [
        Input("dummy_store", "data"),
    ])
def mapbox_callback(df):
    # df = pd.read_json(df, orient="split")
    #
    # lats, lons, texts, customdata = [], [], [], []
    #
    # has_alarm_df = df[df["alarm"]==True]
    #
    # for row in has_alarm_df.itertuples():
    #     lats.append(row.lat)
    #     lons.append(row.long)
    #     texts.append(row.name)
    #     customdata.append([
    #         row.mrc, #mrc
    #         row.address, #address
    #         "T&D" if (row.DN and row.TN) \
    #             else "TN" if (not row.DN and row.TN) \
    #             else "DN" if (row.DN and not row.TN) \
    #             else "Unknown", #type
    #         row.zone, #zone
    #     ])

    return generate_graph()








# @app.callback(
#     Output("url", "href"),
#     [
#         Input("mapbox", "clickData"),
#     ])
# def map_marker_onclick_handler(map_data):
#     if map_data:
#         substation_mrc = map_data.get("points")[0].get("customdata")[0]
#         return f"/substation?mrc={substation_mrc}"
