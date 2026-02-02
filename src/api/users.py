from fastapi import APIRouter, Body, HTTPException, status
from typing import Annotated, List, Dict, TYPE_CHECKING

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
    await DataBase.insert_user(user.name, user.surname, user.middle_name, user.email, utils.hash_password(user.password), user.role)
    return {'response': user.name, }
