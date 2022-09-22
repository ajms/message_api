from datetime import datetime
from functools import lru_cache

import dash_bootstrap_components as dbc
import requests
from dash import Dash, Input, Output, dcc, html
from pydantic import BaseModel, BaseSettings, Field


class Message(BaseModel):
    text: str = Field(example="This is a good day.")
    name: str | None = None
    timestamp: datetime | None = None


class Messages(BaseModel):
    messages: list[Message]


class Config(BaseSettings):
    MESSAGES_ENDPOINT: str = "http://0.0.0.0:8000/messages"


@lru_cache
def load_config():
    return Config()


app = Dash(
    name="Message stream",
    external_stylesheets=[dbc.themes.CYBORG],
    url_base_pathname="/projection-messages/",
)
server = app.server

app.layout = dbc.Container(
    id="main_content",
    children=[
        dbc.Row(
            dbc.Col(
                html.H3(children="The wall of comments for Faxen Dicke"),
                width={"size": 9, "order": 2, "offset": 1},
            )
        ),
        html.Div(id="messages"),
        dcc.Interval(
            id="interval-component", interval=5000, n_intervals=0  # in milliseconds
        ),
    ],
    fluid=True,
    style={"padding": "5px 5px 5px 5px"},
)


@app.callback(
    Output(component_id="messages", component_property="children"),
    Input("interval-component", "n_intervals"),
)
def refresh_barcode(n_intervals) -> html.Img:
    cfg = load_config()
    r = requests.get(cfg.MESSAGES_ENDPOINT, params={"num_messages": 20})
    if r.status_code == 200:
        messages = Messages(**r.json())
        return html.Div(
            children=[
                dbc.Row(
                    children=[
                        dbc.Col(
                            html.H5(message.timestamp.strftime("%H:%M:%S")),
                            width={"size": 1, "order": 2, "offset": 1},
                        ),
                        dbc.Col(
                            html.H5(message.name),
                            width={"size": 1, "order": 1, "offset": 1},
                        ),
                        dbc.Col(
                            html.H5(message.text),
                            width={"size": 7, "order": 3, "offset": 1},
                        ),
                    ],
                )
                for message in messages.messages
            ],
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8051", debug=False)
