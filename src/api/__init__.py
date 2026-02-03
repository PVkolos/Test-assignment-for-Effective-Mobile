from fastapi import APIRouter

from .users import router_users
from .resumes import router_resumes
from .admin import router_admin


router_main = APIRouter()
router_main.include_router(router_users)
router_main.include_router(router_resumes)
router_main.include_router(router_admin)
