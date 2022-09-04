from pydantic import BaseModel
from uuid import uuid4, UUID


class Tokens(BaseModel):
    __root__: list[UUID]


class Message(BaseModel):
    message: str
    token: UUID


class Messages(BaseModel):
    __root__: list[Message]
