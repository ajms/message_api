import re
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
    for key in r.scan_iter("secret_*"):
        used_flag = r.get(key)
        if used_flag != b"unused secret":
            continue
        m = re.match(r"secret_([a-z-0-9]{6})", key.decode("utf-8"))
        assert m is not None, f"{key.decode('utf-8')=}"
        valid_secrets.append(m.group(1))
    for i in range(num - len(valid_secrets), 0, -1):
        token = str(uuid4())[-6:]
        r.set(f"secret_{token}", "unused secret")
        valid_secrets.append(token)
    return valid_secrets[:num]


def delete_keys():
    r = get_redis()
    for key in r.scan_iter("*"):
        r.delete(key)


if __name__ == "__main__":
    delete_keys()
    r = get_redis()

    for key in r.scan_iter("*"):
        print(f"{key}, {r.get(key)}")
