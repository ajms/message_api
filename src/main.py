from fastapi import Depends, FastAPI, Query

from src.helpers import check_token, generate_tokens, get_redis
from src.model import Message, Messages, Tokens

app = FastAPI(
    title="message-api",
    description="api for receiving and displaying messages",
)


@app.get("/")
async def root():
    return {
        "message": "call /docs or /redoc to show the openapi definition",
    }


@app.get(
    "/tokens",
    response_model=Tokens,
    description="Get tokens for posting messages",
)
async def tokens():
    return Tokens(__root__=generate_tokens(2))


@app.post(
    "/message",
    response_model=Message,
    description="Post message with valid token",
)
async def message(body: Message, r=Depends(get_redis)):
    err = check_token(body.token)
    if err:
        raise err
    r.set(f"message_{body.token}", body.message)
    r.set(f"token_{body.token}", 1)
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
    return messages[-10:]
