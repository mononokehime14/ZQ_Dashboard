import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction
from urllib.parse import urlparse, parse_qs
import pandas as pd
from pathlib import Path
import math

from app import app



# def substation_equiment_data_card(serial_no, name, brand, year, overall_alarm, technique_data):
#     technique_divs = []
#
#     for t in technique_data: # {'DGA Offline': nan, 'PD Offline': 0.0}
#         if not math.isnan(technique_data[t]) and technique_data[t] is not None:
#             if technique_data[t] > 0:
#                 t_text = "Attention Needed"
#                 t_text_color = "var(--color-red)"
#             else:
#                 t_text = "Healthy"
#                 t_text_color = "var(--color-green)"
#             technique_divs.append(
#                 html.Div(
#                     [
#                         html.Div(
#                             [
#                                 html.B(t, className="lm--info-label"),
#                                 html.Div(t_text, className="lm--info-value h4", style={"color": t_text_color}),
#                             ],
#                             className="lm--info",
#                         ),
#                     ],
#                     className="lm--card-item col u-cell"
#                 )
#             )
#
#     card_style = {"align-content": "start", "min-height": "176px", "border": "1px solid var(--color-red)"} if overall_alarm is not None and float(overall_alarm)>0 else {"align-content": "start", "min-height": "176px"}
#
#     return html.Div(
#         dcc.Link(
#             [
#                 html.Div(
#                     [
#                         html.Div([html.P(f"{name}")], className="h2"),
#                         html.Div([html.P(f"{serial_no} | {brand} | {year}")], className="lm--info-label", style={"margin-bottom": "0"}),
#                     ],
#                     className="lm--card-item col-sm-12 col-md-12",
#                     style={"overflow": "hidden"},
#                 ),
#                 html.Div(className="u-block"),
#
#
#             ] + technique_divs,
#             href=f"/equipment?serialNo={serial_no}",
#             className="lm--card clickable-card u-p3@sm u-p4@md",
#             style=card_style,
#         ),
#         className="u-p1",
#         style={"width": "350px"},
#     )





layout = [
    # Title Bar
    html.Div(
        html.Nav(
            [
                html.Div(
                    html.H1("Substation", className="u-pl4 u-mb0"),
                    className="col-static",
                ),
            ],
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
                            # Equipment Attributes
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div([html.P("Details")], className="h1 u-mb0")
                                                        ],
                                                        className="lm--card pageSectionHeaderCard u-pl0",
                                                    ),
                                                ],
                                                className="u-pb1 u-pl0",
                                            ),
                                        ],
                                        className="col-sm-12 col-md-12 u-cell u-pt3",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                html.Div(
                                                    [],
                                                    id="substation_details_card",
                                                    className="lm--card u-p4",
                                                    style={"align-items": "flex-start"},
                                                ),
                                                className="u-pt2",
                                            ),
                                        ],
                                        className="col-sm-12 col-md-12 u-cell u-pt0 u-pb1 u-ph0@sm u-ph1@md u-pr1@lg",
                                    ),
                                ],
                                className="col-sm-12 col-lg-auto u-pt4 u-pr4@lg",
                                style={"min-width": "320px", "max-width": "520px"},
                            ),
                            # Equipment Health Details
                            html.Div(
                                [
                                    html.Div(
                                        [],
                                        id="substation_data_cards",
                                    ),

                                ],
                                className="col-sm-12 col-lg-auto u-pt4 u-pl4@lg"
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













# @app.callback(
#     Output("substation_details_card", "children"),
#     [Input("substation_data", "data"),
#      Input("equipment_data", "data"),
#      Input("substation_filter", "value")],
# )
# def equipment_details_callback(ss_df, eq_df, target_ss):
#     children = []
#
#     if target_ss:
#         ss_df = pd.read_json(ss_df, orient="split")
#         eq_df = pd.read_json(eq_df, orient="split")
#
#         ss_df = ss_df[ss_df["mrc"]==target_ss.strip()]
#         ss_df["substation_network"] = ss_df.apply(lambda row: "DN" if row["DN"] else "TN" if row["TN"] else None, axis=1)
#
#
#         if len(ss_df.index) > 0:
#             ss = ss_df.iloc[0]
#
#             photo_filename = f"substation.jpg"
#             my_file = Path(f"assets/{photo_filename}")
#             if my_file.exists():
#                 children.append(
#                     html.Div(
#                         html.Img(
#                             src=app.get_asset_url(photo_filename),
#                             style={"max-height": "300px"},
#                         ),
#                         className="lm--card-item col-sm-12 u-pv2",
#                         style={"text-align": "center"},
#                     ),
#                 )
#
#             attribute_cols = [
#                 "name",
#                 "mrc",
#                 "address",
#                 "substation_network",
#                 "zone",
#             ]
#
#             for col in attribute_cols:
#                 children.append(
#                     html.Div(
#                         [
#                             html.Div(
#                                 [
#                                     html.Div([html.P(col.capitalize(), className="lm--info-label u-text-muted")]),
#                                     html.Div(ss_df[col], className="lm--info-value h4"),
#                                 ],
#                                 className="lm--card-item",
#                                 style={"overflow": "auto"},
#                             ),
#                         ],
#                         className="lm--card-item col-sm-6 col-md-6",
#                     ),
#                 )
#
#     return html.Div(
#         [
#             html.Div(
#                 children,
#                 className="u-grid u-ph3",
#             ),
#         ]
#     )








# @app.callback(
#     Output("substation_data_cards", "children"),
#     [
#         Input("equipment_data", "data"),
#         Input("technique_metadata", "data"),
#         Input("substation_filter", "value")
#     ],
# )
# def substation_data_card_callback(eq_df, meta_df, target_ss):
#     children = []
#
#     if target_ss:
#         meta_df = pd.read_json(meta_df, orient="split")
#         eq_df = pd.read_json(eq_df, orient="split")
#
#         eq_df = eq_df[eq_df["mrc"]==target_ss.strip()]
#         eq_df = eq_df.sort_values("name")
#
#         eq_types_list = eq_df["equipment_type"].unique()
#         for eq_type in eq_types_list:
#             eq_type_df = eq_df[eq_df["equipment_type"]==eq_type]
#
#             eq_cards = []
#
#             for index, row in eq_type_df.iterrows():
#                 cols_to_check = meta_df[(meta_df["network"]==row["network"]) & (meta_df["equipment"]==row["equipment_type"])]["column_name"].to_list()
#                 technique_alarms = {meta_df[meta_df["column_name"]==col]["technique_name"].iloc[0] : row[f"alarm_{col}"] for col in cols_to_check}
#                 eq_cards.append(
#                     substation_equiment_data_card(row["serialNo"], row["name"], row["brand"], row["year"], row["alarm_overall"], technique_alarms)
#                 )
#
#             children.append(
#                 html.Div(
#                     [
#                         html.Div(
#                             [
#                                 html.Div(
#                                     [
#                                         html.Div(
#                                             [
#                                                 html.Div([html.P(f"{eq_type.capitalize()}")], className="h1 u-mb0")
#                                             ],
#                                             className="lm--card pageSectionHeaderCard u-pl0",
#                                         ),
#                                     ],
#                                     className="u-pb1 u-pl0",
#                                 ),
#                             ],
#                             className="col-sm-12 col-md-12 u-cell u-pt3",
#                         ),
#                         html.Div(
#                             [
#                                 html.Div(
#                                     eq_cards,
#                                     className="u-grid col-sm-12 u-p1",
#                                 )
#                             ],
#                             className="col-sm-12 col-md-12 u-cell u-pt0 u-pb3 u-ph0@sm u-ph1@md u-pr1@lg",
#                         ),
#                     ],
#                     className="col-sm-12",
#                 )
#             )
#
#     return html.Div(
#         [
#             html.Div(
#                 children,
#                 className="u-grid u-ph3",
#             ),
#         ]
#     )
