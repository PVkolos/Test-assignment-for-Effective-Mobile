from fastapi import APIRouter, Body, HTTPException, status, Path, Query
from typing import Annotated, List, Dict, TYPE_CHECKING
from sqlalchemy.exc import IntegrityError

from src.database.orm import DataBase
from src.schemas.user_schema import CreateUser
from . import utils
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
                   ):
    try:
        await DataBase.insert_user(user.name, user.surname, user.middle_name, user.email, utils.hash_password(user.password), user.role)
    except IntegrityError as error:
        raise HTTPException(401, 'Такой еmail уже зарегистрирован')
    return {'response': user.name, }


@router_users.post('/users/delete/{email}', tags=['Работа с пользователями'], summary='Дезактивация пользователя')
async def delete_user(email: Annotated[str, Path(..., title='email пользователя для удаления')]
                ) -> Dict[str, int]:
    await DataBase.delete_user(email)
    return {'response': 200}


@router_users.post('/users/change/{email}', tags=['Работа с пользователями'], summary='Изменение данных пользователя')
async def change_data(email: Annotated[str, Path(..., title='email пользователя для удаления')],
                      name: Annotated[str | None, Query(title='Новое имя')] = None,
                      surname: Annotated[str | None, Query(title='Новое фамилия')] = None,
                      middle_name: Annotated[str | None, Query(title='Новое отчество')] = None,
                ) -> Dict[str, int]:
    await DataBase.update_user(email, name, surname, middle_name)
    return {'response': 200}
