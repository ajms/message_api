import logging
from functools import lru_cache
from io import BytesIO

import requests
from authlib.integrations.requests_client import OAuth2Auth, OAuth2Session
from dash import Dash, Input, Output, dcc, html
from PIL import Image
from pydantic import BaseSettings


class Config(BaseSettings):
    TOKEN_ENDPOINT: str = "http://0.0.0.0:8000/token"
    SECRETS_ENDPOINT: str = "http://0.0.0.0:8000/secrets"


@lru_cache
def load_config():
    return Config()


@lru_cache
def get_token(
    token_endpoint: str,
    username: str,
    password: str,
    n_tokens: int,
) -> OAuth2Auth:
    session = OAuth2Session(
        token_endpoint_auth_method="client_secret_basic",
        token_endpoint=token_endpoint,
    )
    logging.info(n_tokens)
    token = session.fetch_token(token_endpoint, username=username, password=password)
    auth = OAuth2Auth(token)
    return auth


app = Dash(name="Show codes for leaving messages")
server = app.server

app.layout = html.Div(
    children=[
        html.H3(children="Scan the qr-code to leave a message"),
        html.Div(
            password := dcc.Input(id="admin_password", type="password"),
            style={"display": "block"},
        ),
        html.Div(id="qr_code"),
        html.Div(html.H4(id="url")),
        dcc.Interval(
            id="interval-component", interval=5000, n_intervals=0  # in milliseconds
        ),
    ],
)


@app.callback(
    Output(component_id="qr_code", component_property="children"),
    Output(component_id="url", component_property="children"),
    Output(component_id="admin_password", component_property="style"),
    Input("admin_password", "value"),
    Input("interval-component", "n_intervals"),
)
def refresh_barcode(password, n_intervals) -> html.Img:
    cfg = load_config()
    auth = get_token(
        token_endpoint=cfg.TOKEN_ENDPOINT,
        username="admin",
        password=password,
        n_tokens=n_intervals // 840,
    )
    r = requests.get(cfg.SECRETS_ENDPOINT, auth=auth, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        qr = BytesIO(r.raw.data)
    img = Image.open(qr)
    r = requests.get(f"{cfg.SECRETS_ENDPOINT}_old", auth=auth)
    if r.status_code == 200:
        url = r.json()["secrets"][0]
    return html.Div(html.Img(src=img)), url, {"display": "none"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8050", debug=False)
