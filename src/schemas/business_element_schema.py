from typing import Annotated
from pydantic import BaseModel, Field


class ElementBusiness(BaseModel):
    id: int
    name: Annotated[str, Field(..., title="Название блока приложения")]
