from functools import lru_cache
from io import BytesIO

import requests
from authlib.integrations.requests_client import OAuth2Auth, OAuth2Session
from dash import Dash, Input, Output, dcc, html
from PIL import Image


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
    session.cert
    token = session.fetch_token(token_endpoint, username=username, password=password)
    auth = OAuth2Auth(token)
    return auth


user = "admin"  # input("User: ")
password = "dwe2022"  # input("Password: ")
token_endpoint = "http://0.0.0.0:8000/token"

app = Dash(name="Show codes for leaving messages")

app.layout = html.Div(
    children=[
        html.H3(children="Scan the barcode to leave a message on the projection"),
        qr_code := html.Div(id="qr_code"),
        dcc.Interval(
            id="interval-component", interval=5000, n_intervals=0  # in milliseconds
        ),
    ],
)


@app.callback(
    Output(component_id="qr_code", component_property="children"),
    Input("interval-component", "n_intervals"),
)
def refresh_barcode(n_intervals) -> html.Img:
    auth = get_token(
        token_endpoint=token_endpoint,
        username=user,
        password=password,
        n_tokens=n_intervals // 840,
    )
    r = requests.get("http://0.0.0.0:8000/secrets", auth=auth, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        qr = BytesIO(r.raw.data)
    img = Image.open(qr)
    return html.Div(html.Img(src=img))


if __name__ == "__main__":
    app.run_server(debug=True)
