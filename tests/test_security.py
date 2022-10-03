from datetime import timedelta

import pytest

from src.helpers import generate_secrets
from src.model import SimpleUser
from src.security import (
    authenticate_user,
    check_authentication_token,
    create_access_token,
)


def test_authenticate_user_success(r):
    secret = str(generate_secrets(1)[0])
    assert isinstance(authenticate_user(secret), SimpleUser)
    r.hdel("secret", secret)


@pytest.mark.parametrize("used_flag", ["authenticated", "message posted"])
def test_authenticate_user_failed(used_flag, r):
    secret = str(generate_secrets(1)[0])
    r.hset("secret", secret, used_flag)
    assert not authenticate_user(secret)
    r.hdel("secret", secret)


def test_authenticate_user_admin():
    assert not authenticate_user("admin", "test")


def test_create_access_token(cfg):
    secret = str(generate_secrets(1)[0])
    access_token_expires = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": secret}, expires_delta=access_token_expires
    )
    assert isinstance(access_token, str)


@pytest.mark.asyncio
async def test_check_authentication_token(cfg):
    secret = str(generate_secrets(1)[0])
    access_token_expires = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": secret}, expires_delta=access_token_expires
    )
    token_data = await check_authentication_token(access_token)
    assert token_data.user == str(secret)
