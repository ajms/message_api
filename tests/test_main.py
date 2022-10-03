import asyncio

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


async def send_message(msg, secret, cfg, r):
    token = await authorize(cfg, r, secret)
    token_data = await check_authentication_token(token=token["access_token"])
    return await post_message(body=msg, token_data=token_data, r=r)


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
    msg_out = await send_message(msg_in, secret, cfg, r)
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
    msg_out = await send_message(msg_in, secret, cfg, r)
    assert msg_out.name == msg_in.name
    assert msg_out.text == msg_in.text
    r.hdel("secret", secret)
    r.hdel("message", msg_out.id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "messages, names",
    [([f"message{i}" for i in range(20)], [f"name{i}" for i in range(20)])],
)
async def test_message_concurrency(messages: list[str], names: list[str], cfg, r):
    last_message_id = r.get("id")
    if not r.get("id"):
        last_message_id = 0
    else:
        last_message_id = int(last_message_id)
    msgs_in = [
        Message(text=message, name=name) for message, name in zip(messages, names)
    ]
    secrets = generate_secrets(len(msgs_in))
    msgs_out = await asyncio.gather(
        *(
            send_message(msg_in, secret, cfg, r)
            for msg_in, secret in zip(msgs_in, secrets)
        )
    )
    assert len(msgs_in) == len(msgs_out)
    assert max((msg.id for msg in msgs_out)) == last_message_id + len(msgs_in) - 1

    for msg_out, secret in zip(msgs_out, secrets):
        r.hdel("message", msg_out.id)
        r.hdel("secret", secret)


@pytest.mark.asyncio
@pytest.mark.parametrize("num", [10, 2, 5])
async def test_messages(num, r):
    num_messages = len(list(r.hscan_iter("message", "*")))
    msgs = await get_messages(num, r)
    assert len(msgs.messages) == min(num, num_messages)
