from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base

if TYPE_CHECKING:
    from .roles_model import RoleModel
    from .business_elements_model import BusinessElementModel


# Матрица прав доступа
class AccessRoleRuleModel(Base):
    __tablename__ = "access_roles_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    element_id: Mapped[int] = mapped_column(ForeignKey("business_elements.id"))

    # Права на чтение
    read_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    read_all_permission: Mapped[bool] = mapped_column(Boolean, default=False)

    # Права на создание
    create_permission: Mapped[bool] = mapped_column(Boolean, default=False)

    # Права на обновление
    update_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    update_all_permission: Mapped[bool] = mapped_column(Boolean, default=False)

    # Права на удаление
    delete_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    delete_all_permission: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped["RoleModel"] = relationship(back_populates="rules")
    element: Mapped["BusinessElementModel"] = relationship(back_populates="rules")
