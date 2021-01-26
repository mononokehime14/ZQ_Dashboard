from dash import Dash
import dash_html_components as html
import dash_table


app = Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    title="Dashboard Title Here",
    update_title=None,
)

app.config.suppress_callback_exceptions = True
