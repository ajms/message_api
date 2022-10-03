import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.helpers import generate_secrets
from src.main import get_messages, login_for_access_token, post_message
from src.model import Message
from src.security import check_authentication_token


async def authorize(cfg, r, secret: str | None = None):
    if secret is None:
        secret = generate_secrets(1)[0]
    form_data = OAuth2PasswordRequestForm(
        grant_type="password", username=secret, password=secret, scope=""
    )
    return await login_for_access_token(form_data=form_data, cfg=cfg, r=r)


@pytest.mark.asyncio
async def test_login_for_access_token_success(cfg, r):
    secret = generate_secrets(1)[0]
    token = await authorize(cfg, r, secret)
    assert "access_token" in token
    r.hdel("secret", secret)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, name",
    [("test message", "test name")],
)
async def test_login_for_access_token_failed(text: str, name: str, cfg, r):
    msg_in = Message(text=text, name=name)
    secret = str(generate_secrets(1)[0])
    token = await authorize(cfg, r)
    token_data = await check_authentication_token(token=token["access_token"])
    msg_out = await post_message(body=msg_in, token_data=token_data, r=r)
    with pytest.raises(HTTPException):
        _ = await authorize(cfg, r, secret)
    r.hdel("secret", secret)
    r.hdel("message", msg_out.id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, name",
    [("test message", "test name")],
)
async def test_message(text: str, name: str, cfg, r):
    msg_in = Message(text=text, name=name)
    secret = generate_secrets(1)[0]
    token = await authorize(cfg, r, secret)
    token_data = await check_authentication_token(token=token["access_token"])
    msg_out = await post_message(body=msg_in, token_data=token_data, r=r)
    assert msg_out.name == msg_in.name
    assert msg_out.text == msg_in.text
    r.hdel("secret", secret)
    r.hdel("message", msg_out.id)


@pytest.mark.asyncio
@pytest.mark.parametrize("num", [10, 2, 5])
async def test_messages(num, r):
    num_messages = len(list(r.hscan_iter("message", "*")))
    msgs = await get_messages(num, r)
    assert len(msgs.messages) == min(num, num_messages)
