from fastapi import APIRouter, Body, HTTPException, status, Path, Query, Depends
from typing import Annotated, List, Dict
from sqlalchemy.exc import IntegrityError

from pydantic import EmailStr

from src.database.orm import DataBase

from src.schemas.user_schema import CreateUser, User
from src.schemas.auth_schemas import TokenInfo

from . import utils
from src.config import settings
router_users = APIRouter()


@router_users.post('/users/add', tags=['Работа с пользователями'], summary='Добавление пользователя в бд')
async def add_user(user: Annotated[CreateUser, Body(..., example={
                                                                    "name": "Имя",
                                                                    "surname": "Фамилия",
                                                                    "middle_name": "Отчество",
                                                                    "password": "Пароль",
                                                                    "password_again": "Пароль повторно",
                                                                    "email": "email",
                                                                    "role": "Роль пользователя"
                                                                })],
                    creator: Annotated[User, Depends(utils.check_permissions("user", "create"))]
                   ):
    try:
        await DataBase.insert_user(user.name, user.surname, user.middle_name, user.email, utils.hash_password(user.password), user.role)
    except IntegrityError as error:
        raise HTTPException(401, 'Такой email уже зарегистрирован')
    return {'response': user.name, }


@router_users.post('/users/delete/{email}', tags=['Работа с пользователями'], summary='Дезактивация пользователя')
async def delete_user(email: Annotated[str, Path(..., title='email пользователя для удаления')],
                      user: Annotated[User, Depends(utils.check_permissions("user", "delete"))]
                ) -> Dict[str, int]:
    await DataBase.delete_user(email)
    return {'response': 200}


@router_users.post('/users/change/{email}', tags=['Работа с пользователями'], summary='Изменение данных пользователя')
async def change_data(email: Annotated[EmailStr, Path(..., title='email пользователя для удаления')],
                      user: Annotated[User, Depends(utils.check_permissions("user", "update"))],
                      name: Annotated[str | None, Query(title='Новое имя')] = None,
                      surname: Annotated[str | None, Query(title='Новое фамилия')] = None,
                      middle_name: Annotated[str | None, Query(title='Новое отчество')] = None,
                ) -> Dict[str, int]:
    await DataBase.update_user(email, name, surname, middle_name)
    return {'response': 200}


@router_users.post('/users/login',
                   tags=['Работа с пользователями'],
                   summary='Войти в аккаунт (выпустить токен)',
                   response_model=TokenInfo, response_model_exclude_none=True)
async def login_user(
        user: User = Depends(utils.validate_user_login)
    ) -> TokenInfo:

    access_token = utils.create_access_jwt(user)
    refresh_token = utils.create_refresh_jwt(user)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router_users.get('/users/check_auth', tags=['Работа с пользователями'], summary='Проверка авторизации')
async def check_auth(user: Annotated[User, Depends(utils.check_token_auth)]) -> Dict:
    return {'response': 200, 'name': user.name}


@router_users.post('/users/generate-access', tags=['Работа с пользователями'], summary='Перевыпуск access jwt',
                   response_model=TokenInfo, response_model_exclude_none=True)
async def generate_access_jwt(user: User = Depends(utils.check_token_auth_refresh)):
    return TokenInfo(access_token=utils.create_access_jwt(user=user))
