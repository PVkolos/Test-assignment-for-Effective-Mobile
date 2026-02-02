import bcrypt
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from src.config import settings
from fastapi import HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.database.orm import DataBase
from src.schemas.user_schema import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


async def validate_user_login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    email = form_data.username
    password = form_data.password

    if not (user := await DataBase.get_user(email)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет такого пользователя")
    if validate_password(password, user.password):
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный пароль")


def validate_token_type(payload: dict, token_type: str) -> bool:
    if payload.get(settings.const.TOKEN_TYPE_FIELD) == token_type:
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token type not valid")


async def check_auth(
        token: str = Depends(oauth2_scheme)
    ) -> dict:
    try:
        payload = decode_jwt(encoded=token)
        return payload
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Инвалидный токен'
        )


async def check_token_auth(
        payload: dict = Depends(check_auth)
) -> User:
    validate_token_type(payload, settings.const.TOKEN_ACCESS_FIELD)
    if user := await DataBase.get_user(payload.get("sub")):
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Пользователь не найден')


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
    ):
    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
        encoded: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
    ):
    decoded = jwt.decode(encoded, public_key, algorithms=[algorithm])
    return decoded


def create_jwt(sub: str, payload: dict, token_type: str, expire: timedelta) -> str:
    payload['sub'] = sub
    payload[settings.const.TOKEN_TYPE_FIELD] = token_type
    payload['iat'] = datetime.utcnow()
    payload['exp'] = datetime.utcnow() + expire

    payload.update(payload)
    return encode_jwt(payload)


def create_access_jwt(user: User) -> str:
    payload = {
        'email': user.email,
    }
    return create_jwt(
        sub=str(user.email),
        payload=payload,
        token_type=settings.const.TOKEN_ACCESS_FIELD,
        expire=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_jwt(user: User) -> str:
    payload = {}
    return create_jwt(
        sub=str(user.email),
        payload=payload,
        token_type=settings.const.TOKEN_REFRESH_FIELD,
        expire=settings.auth_jwt.refresh_token_expire_days,
    )
