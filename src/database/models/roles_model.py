from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from sqlalchemy import String

if TYPE_CHECKING:
    from .rights_matrix_model import AccessRoleRule


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    rules: Mapped[List["AccessRoleRule"]] = relationship(back_populates="role")


    def __str__(self):
        return f'{self.__class__.__name__}({self.id=}, {self.name=})'
