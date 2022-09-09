import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.helpers import generate_secrets
from src.main import login_for_access_token, message, messages
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
    secret = str(generate_secrets(1)[0])
    token = await authorize(cfg, r, secret)
    assert "access_token" in token
    r.delete(f"token_{secret}")


@pytest.mark.asyncio
async def test_login_for_access_token_failed(cfg, r):
    secret = str(generate_secrets(1)[0])
    _ = await authorize(cfg, r)
    with pytest.raises(HTTPException):
        _ = await authorize(cfg, r, secret)
    r.delete(f"token_{secret}")


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
    msg = await message(body=msg_in, token_data=token_data, r=r)
    assert msg.name == msg_in.name
    assert msg.text == msg_in.text
    r.delete(f"token_{secret}")
    r.delete(f"message_{secret}")


@pytest.mark.asyncio
@pytest.mark.parametrize("num", [10, 2, 5])
async def test_messages(num, r):
    num_messages = len(list(r.scan_iter("message_*")))
    msgs = await messages(num, r)
    assert len(msgs.messages) == min(num, num_messages)
