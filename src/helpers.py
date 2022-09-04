from functools import lru_cache
from uuid import UUID, uuid4

from fastapi import HTTPException
from pydantic import BaseSettings
from redis import Redis


class Settings(BaseSettings):
    REDIS_HOST: str = "0.0.0.0"
    REDIS_PORT: int = 6379
    ACCESS_TOKEN: str = ""


@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_redis():
    cfg = get_settings()
    return Redis(
        host=cfg.REDIS_HOST,
        port=cfg.REDIS_PORT,
        password=cfg.ACCESS_TOKEN,
    )


def generate_tokens(num: int):
    r = get_redis()
    valid_tokens = []
    for key in r.scan_iter("token_*"):
        used_flag = r.get(key)
        if used_flag == b"1":
            continue
        valid_tokens.append(UUID(key[6:].decode("utf-8")))
    for i in range(num - len(valid_tokens), 0, -1):
        token = uuid4()
        r.set(f"token_{token}", 0)
        valid_tokens.append(token)
    return valid_tokens[:num]


def check_token(token):
    r = get_redis()
    used_flag = r.get(f"token_{token}")
    if used_flag is None:
        return HTTPException(401, "token does not exist")
    elif used_flag == b"1":
        return HTTPException(401, "token has been used")
    else:
        return None


def delete_keys():
    r = get_redis()
    for key in r.scan_iter("*"):
        r.delete(key)


if __name__ == "__main__":
    # delete_keys()
    r = get_redis()
    print(generate_tokens(10))

    for key in r.scan_iter("*"):
        print(f"{key}, {r.get(key)}")
