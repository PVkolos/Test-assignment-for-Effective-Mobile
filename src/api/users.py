from fastapi import APIRouter, Body, HTTPException, status
from typing import Annotated, List, Dict, TYPE_CHECKING

from src.database.orm import DataBase

router_users = APIRouter()


@router_users.post('/users/add', tags=['Работа с пользователями'], summary='Добавление пользователя в бд')
async def add_user():
    return {'response': 200, }
