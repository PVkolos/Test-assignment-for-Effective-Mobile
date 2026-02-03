from typing import Annotated
from pydantic import BaseModel, Field


class CreateAccessRolesRules(BaseModel):
    role_id: Annotated[int, Field(..., title="ID роли")]
    element_id: Annotated[int, Field(..., title="ID бизнес блока приложения")]

    read_permission: Annotated[bool, Field(..., title="Разрешено чтение своего")]
    read_all_permission: Annotated[bool, Field(..., title="Разрешено чтение общего")]
    create_permission: Annotated[bool, Field(..., title="Разрешено создание")]
    update_permission: Annotated[bool, Field(..., title="Разрешено обновление своего")]
    update_all_permission: Annotated[bool, Field(..., title="Разрешено обновление общего")]
    delete_permission: Annotated[bool, Field(..., title="Разрешено удаление своего")]
    delete_all_permission: Annotated[bool, Field(..., title="Разрешено удаление общего")]


class AccessRolesRules(CreateAccessRolesRules):
    id: int
