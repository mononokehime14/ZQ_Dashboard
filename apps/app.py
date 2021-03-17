from dash import Dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table


app = Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    title="ZQ Dashboard",
    update_title=None,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

app.config.suppress_callback_exceptions = True
