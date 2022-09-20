from datetime import datetime
from functools import lru_cache

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


app = Dash(name="Message stream", url_base_pathname="/messages/")
server = app.server

app.layout = html.Div(
    children=[
        html.H3(children="Messages"),
        html.Div(id="messages"),
        dcc.Interval(
            id="interval-component", interval=5000, n_intervals=0  # in milliseconds
        ),
    ],
)


@app.callback(
    Output(component_id="messages", component_property="children"),
    Input("interval-component", "n_intervals"),
)
def refresh_barcode(n_intervals) -> html.Img:
    cfg = load_config()
    r = requests.get(cfg.MESSAGES_ENDPOINT)
    if r.status_code == 200:

        messages = Messages(**r.json())
        print(messages)
    return [
        html.Div(f"{message.name}@ {message.timestamp}: {message.text}")
        for message in messages.messages
    ]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8051", debug=False)
