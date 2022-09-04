from fastapi import FastAPI
from src.model import Tokens, Message, Messages

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tokens", response_model=Tokens)
async def tokens():
    pass


@app.post("/message", response_model=Message)
async def message(body: Message):
    pass


@app.get("/messages", response_model=Messages)
async def messages():
    pass
