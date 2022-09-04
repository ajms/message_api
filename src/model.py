from uuid import UUID

from pydantic import BaseModel, Field


class Tokens(BaseModel):
    __root__: list[UUID]


class Message(BaseModel):
    message: str = Field("This is a good day.")
    token: str


class Messages(BaseModel):
    __root__: list[Message]
