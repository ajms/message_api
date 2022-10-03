from functools import lru_cache
from uuid import uuid4

from pydantic import BaseSettings
from redis import Redis


class Settings(BaseSettings):
    REDIS_HOST: str = "0.0.0.0"
    REDIS_PORT: int = 6379
    ACCESS_TOKEN: str = ""
    JWT_SECRET_KEY = ""
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    ADMIN_PASSWORD = ""
    URL_MESSAGE_FORM = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


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


def generate_secrets(num: int):
    r = get_redis()
    valid_secrets = []
    for key, used_flag in r.hscan_iter("secret", "*"):
        if used_flag != b"unused secret":
            continue
        valid_secrets.append(key.decode("utf-8"))
    if num - len(valid_secrets) > 0:
        new_keys = {
            str(uuid4())[-6:]: "unused secret"
            for _ in range(num - len(valid_secrets), 0, -1)
        }
        r.hset("secret", mapping=new_keys)
        valid_secrets += list(new_keys.keys())
    return valid_secrets[:num]


def delete_keys():
    r = get_redis()
    for key in r.scan_iter("*"):
        r.delete(key)


if __name__ == "__main__":
    # delete_keys()
    r = get_redis()
    print(generate_secrets(1))
    for key, used_flag in r.hscan_iter("secret", "*"):
        print(f"{key}, {used_flag}")
    for key, used_flag in r.hscan_iter("message", "*"):
        print(f"{key}, {used_flag}")
