from typing import List, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base

if TYPE_CHECKING:
    from .rights_matrix_model import AccessRoleRule


class BusinessElement(Base):
    __tablename__ = "business_elements"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    rules: Mapped[List["AccessRoleRule"]] = relationship(back_populates="element")