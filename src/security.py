from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.helpers import get_redis, get_settings
from src.model import SimpleUser, TokenData, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def authenticate_user(user: str, password: str | None) -> SimpleUser | bool:
    if user != "admin":
        r = get_redis()
        used_flag = r.get(f"token_{user}")
        if not used_flag:
            return False
        return SimpleUser(user=user, disabled=used_flag)
    else:
        cfg = get_settings()
        if not verify_password(password, cfg.ADMIN_PASSWORD):
            return False
        return User(user=user, disabled=0, hashed_password=cfg.ADMIN_PASSWORD)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    cfg = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        cfg.JWT_SECRET_KEY,
        algorithm=cfg.ALGORITHM,
    )
    return encoded_jwt


async def check_authentication_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    cfg = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            cfg.JWT_SECRET_KEY,
            algorithms=[cfg.ALGORITHM],
        )
        user: str = payload.get("sub")
        if user is None:
            raise credentials_exception
        token_data = TokenData(user=user)
    except JWTError:
        raise credentials_exception
    return token_data


if __name__ == "__main__":
    pwd = input("enter pwd: ")
    print(get_password_hash(pwd))
