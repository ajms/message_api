from dash import Dash, dcc, html

app = Dash(name="Show messages")


app.layout = html.Div(
    children=[
        html.H3(children="Messages"),
        html.Div(),
        html.Div(id="qr_code"),
        dcc.Interval(
            id="interval-component", interval=5000, n_intervals=0  # in milliseconds
        ),
    ],
)
