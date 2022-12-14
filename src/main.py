import io
import json
from datetime import datetime, timedelta

import pytz
import qrcode
import redis
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import StreamingResponse

from src.helpers import generate_secrets, get_redis, get_settings
from src.model import Message, Messages, OneTimeSecrets, Token, TokenData
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
        "message": "Hello :)",
    }


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    cfg=Depends(get_settings),
    r=Depends(get_redis),
) -> Token:
    user = authenticate_user(str(form_data.username), form_data.password)
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
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    "/secrets",
    description="Get secrets for posting messages",
)
async def get_secrets(
    num_secrets: int = Query(default=1),
    token_data=Depends(check_authentication_token),
    cfg=Depends(get_settings),
) -> OneTimeSecrets:
    if token_data.user != "admin":
        raise HTTPException(401, "Not authorized to view this endpoint")
    secrets = OneTimeSecrets(secrets=generate_secrets(num_secrets))
    img = qrcode.make(f"{cfg.URL_MESSAGE_FORM}{secrets.secrets[0]}")
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.get(
    "/secrets_text",
    response_model=OneTimeSecrets,
    description="Get secrets for posting messages",
)
async def get_secrets_text(
    num_secrets: int = Query(default=1),
    token_data=Depends(check_authentication_token),
    cfg=Depends(get_settings),
) -> OneTimeSecrets:
    if token_data.user != "admin":
        raise HTTPException(401, "Not authorized to view this endpoint")
    secrets = OneTimeSecrets(
        secrets=[
            f"{cfg.URL_MESSAGE_FORM}{secret}"
            for secret in generate_secrets(num_secrets)
        ]
    )
    return secrets


@app.post(
    "/message",
    response_model=Message,
    description="Post message with valid token",
)
async def post_message(
    body: Message,
    token_data: TokenData = Depends(check_authentication_token),
    r=Depends(get_redis),
) -> Message:
    used_flag = r.hget("secret", token_data.user)
    if used_flag is None:
        raise HTTPException(401, "Invalid token")
    elif used_flag == b"message posted":
        raise HTTPException(401, "Token is already used")
    else:
        try:
            pipeline = r.pipeline()
            pipeline.watch("id")
            id = pipeline.get("id")
            if not id:
                r.set("id", 0)
                id = 0
            message = Message(
                id=int(id),
                text=body.text,
                name=body.name,
                timestamp=datetime.now(
                    tz=pytz.timezone("Europe/Berlin"),
                ),
            )
            pipeline.hset(name="message", key=int(id), value=message.json())
            pipeline.hset(name="secret", key=token_data.user, value="message posted")
            pipeline.unwatch()
            pipeline.incr("id")
            pipeline.execute()
        except redis.WatchError:
            return HTTPException(409, "An occurrency error occurred, please try again.")
    return message


@app.delete("/message", response_model=Message, description="Delete message by id")
async def delete_message(
    id: int = Query("message id"),
    token_data: TokenData = Depends(check_authentication_token),
    r: redis.Redis = Depends(get_redis),
) -> Message:
    message_keys = list(r.scan_iter(f"message_{id}_*"))
    if message_keys != []:
        for key in message_keys:
            message = json.loads(r.hget("message", key))
            r.hdel("message", key)
            r.hset("deleted_message", key, json.dumps(message))
        return message
    else:
        raise HTTPException(404, "Message not found")


@app.get(
    "/messages",
    response_model=Messages,
    description="Show latest messages",
)
async def get_messages(
    num_messages: int = Query(default=10, title="Number of messages"),
    r=Depends(get_redis),
) -> Messages:
    messages = []
    last_message_id = r.get("id")
    if not last_message_id:
        last_message_id = b"0"

    i = int(last_message_id)
    while i > 0 and num_messages >= 0:
        value = r.hget("message", i)
        if value:
            msg = json.loads(value)
            messages.append(Message(**msg))
            num_messages -= 1
        i -= 1

    return Messages(
        messages=sorted(messages, key=lambda x: x.timestamp, reverse=True)[
            :num_messages
        ]
    )
