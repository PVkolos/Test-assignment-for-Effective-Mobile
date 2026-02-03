import bcrypt
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from src.config import settings
from fastapi import HTTPException, status, Depends, Body, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.database.orm import DataBase
from src.database.models.users_model import UserModel
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
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь не найден')


async def check_token_auth_refresh(
        payload: dict = Depends(check_auth)
    ) -> User:
    validate_token_type(payload, settings.const.TOKEN_REFRESH_FIELD)
    if user := await DataBase.get_user(payload.get("sub")):
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь не найден')


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


def check_is_active(user: UserModel) -> bool:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь удален'
        )
    return True


def check_permissions(element_name: str, action: str, ):
    async def _permission_dependency(
            request: Request,
            user: UserModel = Depends(check_token_auth),
    ):
        check_is_active(user)

        own_permission_col = f"{action}_permission"
        all_permission_col = f"{action}_all_permission"

        # Получаю ID элемента
        element_id = await DataBase.get_business_element_id(element_name)

        if not element_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Элемент {element_name} не найден в БД")

        # Ищу правило для связки Роль + Элемент в таблице access_roles_rules
        rule = await DataBase.get_rule(user, element_id)

        # Не найдена строка в таблице access_roles_rules для текущего action и element_id
        if not rule:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав доступа")

        '''
        Действия, НЕ подразумевающие групповую политику (only "permission"). Например - создание. 
        Обработка каждого такого действия прописывается отдельно, здесь.
        '''
        # Проверяем, если действие - создание объекта и есть права на создание, пропускаем
        if action == 'create' and rule.create_permission:
            return user

        '''Действия, подразумевающие групповую политику (permission/all_permission). Например - удаление, редактирование, чтение'''
        # Если разрешено ВСЁ (all_permission), то дальше можно не проверять
        if getattr(rule, all_permission_col, False):
            return user

        # Если общее разрешение False, проверяем разрешение на свое
        if getattr(rule, own_permission_col, False):
            obj_find = ''
            if element_name == 'user': # Действие производится над бизнес-логикой "user".
                obj_find = 'email'
            elif element_name == 'resume': # Действие производится над бизнес-логикой "resume"
                obj_find = 'id'

            changed_obj = request.path_params.get(obj_find) # получаем из параметров пути идентификатор объекта

            if changed_obj:
                '''
                Значение флага меняется на True, если element_name != user 
                Это будет значить, что element_name - создан пользователем (резюме, статьи, видео ...)
                (только тогда имеет смысл переменная owner_email)
                '''
                flag = False
                if element_name == 'user':
                    if changed_obj == user.email:
                        return user

                elif element_name == 'resume':
                    owner_email = await DataBase.get_owner_resume(obj_find)
                    flag = True

                '''
                Логика обработки остальных любых element_name будет идентичной с 'resume', 
                но запрос к бд будет идти к другим таблицам
                '''

                if flag and owner_email == user.email:
                    return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен: недостаточно прав"
        )

    return _permission_dependency