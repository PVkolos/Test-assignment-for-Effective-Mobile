from fastapi import APIRouter

from .users import router_users


router_main = APIRouter()
router_main.include_router(router_users)
