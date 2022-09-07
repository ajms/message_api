from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from src.helpers import generate_tokens, get_redis, get_settings
from src.model import AccessTokens, Message, Messages, Token
from src.security import (
    authenticate_user,
    check_authentication_token,
    create_access_token,
)

app = FastAPI(
    title="message-api",
    description="api for receiving and displaying messages",
)


@app.get("/")
async def root():
    return {
        "message": "call /docs or /redoc to show the openapi definition",
    }


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    cfg=Depends(get_settings),
    r=Depends(get_redis),
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user}, expires_delta=access_token_expires
    )
    if form_data.username != "admin":
        r.set(f"token_{form_data.username}", 1)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    "/tokens",
    response_model=AccessTokens,
    description="Get tokens for posting messages",
)
async def tokens(token_data=Depends(check_authentication_token)):
    if token_data.user != "admin":
        raise HTTPException(401, "Not authorized to view this endpoint")
    return AccessTokens(tokens=generate_tokens(2))


@app.post(
    "/message",
    response_model=Message,
    description="Post message with valid token",
)
async def message(
    body: Message,
    token_data=Depends(check_authentication_token),
    r=Depends(get_redis),
):
    r = get_redis()
    used_flag = r.get(f"token_{token_data.user}")
    if used_flag is None:
        raise HTTPException(401, "No token provided")
    elif used_flag == b"2":
        raise HTTPException(401, "Token is already used")
    else:
        r.set(f"message_{body.name}", body.message)
        r.set(f"token_{token_data.user}", 2)
    body.timestamp = datetime.now()
    return body


@app.get(
    "/messages",
    response_model=Messages,
    description="Show latest messages",
)
async def messages(
    num_messages: int = Query(default=10, title="Number of messages"),
    r=Depends(get_redis),
):
    messages = []
    for key in r.scan_iter("message_*"):
        messages.append(
            Message(token=key[8:], message=r.get(key).decode("utf-8")),
        )
    return messages[-num_messages:]
