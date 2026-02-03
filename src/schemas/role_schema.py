from typing import Annotated, List
from pydantic import BaseModel, Field

from src.schemas.access_roles_rules_schema import AccessRolesRules


class Role(BaseModel):
    id: int
    name: Annotated[str, Field(..., title="Название роли")]


class RoleRelationship(BaseModel):
    id: int
    name: Annotated[str, Field(..., title="Название роли")]
    rules: List[AccessRolesRules]
