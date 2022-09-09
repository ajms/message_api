import pytest

from src.helpers import generate_secrets
from src.model import SimpleUser
from src.security import authenticate_user


def test_authenticate_user_success(r):
    secret = str(generate_secrets(1)[0])
    assert isinstance(authenticate_user(secret), SimpleUser)
    r.delete(f"token_{secret}")


@pytest.mark.parametrize("used_flag", [1, 2])
def test_authenticate_user_failed(used_flag, r):
    secret = generate_secrets(1)[0]
    r.set(f"token_{secret}", used_flag)
    assert not authenticate_user(secret)
    r.delete(f"token_{secret}")


def test_authenticate_user_admin():
    assert not authenticate_user("admin", "test")
