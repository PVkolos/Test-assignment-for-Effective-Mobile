from fastapi import APIRouter

from .users import router_users
from .resumes import router_resumes
from .admin import router_admin


router_main = APIRouter()
router_main.include_router(router_users) # Подключаем роутер группы "users"
router_main.include_router(router_resumes) # Подключаем роутер группы "resumes"
router_main.include_router(router_admin) # Подключаем роутер группы "resumes"
