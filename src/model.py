from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AccessTokens(BaseModel):
    tokens: list[UUID]


class Message(BaseModel):
    message: str = Field(example="This is a good day.")
    name: str
    timestamp: datetime | None = None


class Messages(BaseModel):
    messages: list[Message]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user: str | None = None


class AccessToken(BaseModel):
    user: str
    disabled: bool | None = None


class User(AccessToken):
    hashed_password: str
