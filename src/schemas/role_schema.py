from typing import Annotated
from pydantic import BaseModel, Field


class Role(BaseModel):
    id: int
    name: Annotated[str, Field(..., title="Название роли")]
