from fastapi.security import OAuth2PasswordRequestForm

from src.helpers import generate_secrets
from src.main import login_for_access_token


async def test_login_for_access_token_success():
    secret = generate_secrets(1)[0]
    form_data = OAuth2PasswordRequestForm(
        grant_type="password", username=secret, password=secret, scope=""
    )
    token = await login_for_access_token(form_data=form_data)
    assert "access_token" in token.keys()


async def test_login_for_access_token_failed():
    secret = generate_secrets(1)[0]
    form_data = OAuth2PasswordRequestForm(
        grant_type="password", username=secret, password=secret, scope=""
    )
    token = await login_for_access_token(form_data=form_data)
    assert "access_token" in token.keys()
    token2 = await login_for_access_token(form_data=form_data)

    assert "access_token" in token2.keys()
