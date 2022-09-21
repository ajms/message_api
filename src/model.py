from datetime import datetime

from pydantic import BaseModel, Field


class OneTimeSecrets(BaseModel):
    secrets: list[str]


class Message(BaseModel):
    text: str = Field(example="This is a good day.")
    name: str | None = None
    timestamp: datetime | None = None


class Messages(BaseModel):
    messages: list[Message]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user: str | None = None


class SimpleUser(BaseModel):
    user: str
    disabled: bool | None = None


class User(SimpleUser):
    hashed_password: str
