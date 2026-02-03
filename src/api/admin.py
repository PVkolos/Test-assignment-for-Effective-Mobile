from fastapi import APIRouter, Body, HTTPException, status, Path, Query, Depends
from typing import Annotated, List, Dict

from src.database.orm import DataBase

from src.schemas.access_roles_rules_schema import AccessRolesRules, CreateAccessRolesRules
from src.schemas.business_element_schema import ElementBusiness
from src.schemas.role_schema import Role

from . import utils

router_admin = APIRouter(
    tags=["Администрирование системы прав доступа"],
    dependencies=[Depends(utils.check_is_admin)],
    prefix="/admin",
)


@router_admin.get('/get_business_elements', summary='Получение списка всех бизнес блоков приложения')
async def get_business_elements() -> List[ElementBusiness]:
    elements = await DataBase.get_all_business_elements()
    return elements


@router_admin.get('/get_roles', summary='Получение списка всех ролей')
async def get_roles() -> List[Role]:
    roles = await DataBase.get_all_roles()
    return roles


@router_admin.get('/get_access_roles_rules', summary='Получение списка всех прав всех групп')
async def get_access_roles_rules() -> List[AccessRolesRules]:
    elements = await DataBase.get_access_roles_rules()
    return elements


@router_admin.post('/create_new_rule', summary='Создание нового правила')
async def create_new_rule(rule: Annotated[CreateAccessRolesRules, Body(..., example={
                                                                    "role_id": "ID роли (получить id всех ролей вы можете на ...)",
                                                                    "element_id": "ID блока приложения (получить id всех блоков вы можете на /admin/get_business_elements)",
                                                                    "read_permission": "Разрешено на чтение своего",
                                                                    "read_all_permission": "Разрешено чтение общего",
                                                                    "create_permission": "Разрешено создание",
                                                                    "update_permission": "Разрешено обновление своего",
                                                                    "update_all_permission": "Разрешено обновление общего",
                                                                    "delete_permission": "Разрешено удаление своего",
                                                                    "delete_all_permission": "Разрешено удаление общего"
                                                                })]) -> dict[str, int]:
    if not await DataBase.check_role_id(rule.role_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Роли с {rule.role_id=} не найдено')
    if not await DataBase.check_element_id(rule.element_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Блока приложения с {rule.element_id=} не найдено')
    if await DataBase.check_rule_exists(rule.element_id, rule.role_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Правило с {rule.element_id=} и {rule.role_id=} уже существует')

    await DataBase.insert_rule(rule.role_id, rule.element_id, rule.read_permission, rule.read_all_permission,
                               rule.create_permission, rule.update_permission, rule.update_all_permission,
                               rule.delete_permission, rule.delete_all_permission)
    return {'response': 200}


@router_admin.delete('/delete_rule/{rule_id}', summary='Удаление правила')
async def delete_user(rule_id: Annotated[int, Path(..., title='ID правила')],
                ) -> Dict[str, int]:
    if not await DataBase.check_rule_exists(None, None, rule_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Правило с {rule_id=} не найдено')
    await DataBase.delete_rule(rule_id)
    return {'response': 200}