from datetime import datetime
from functools import lru_cache

import dash_bootstrap_components as dbc
import requests
from dash import Dash, Input, Output, dcc, html
from pydantic import BaseModel, BaseSettings, Field


class Message(BaseModel):
    id: int | None = None
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
                html.H3(children="Mietenschmutztwitter"),
                width={"size": 8, "order": 2, "offset": 1},
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
                            children=[
                                f"# {message.id} @ {message.timestamp.strftime('%H:%M:%S')}",
                                html.H5(message.name),
                            ],
                            width={"size": 2, "order": 1, "offset": 1},
                        ),
                        dbc.Col(
                            html.H6(message.text),
                            width={"size": 7, "order": 1, "offset": 0},
                        ),
                    ],
                    style={"padding-bottom": "20px"},
                )
                for message in messages.messages
            ],
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8051", debug=False)
