from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users_model import UserModel


class ResumeModel(Base):
    __tablename__ = 'resumes'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    salary: Mapped[int] = mapped_column(nullable=False)

    email: Mapped[str] = mapped_column(ForeignKey("users.email"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="resumes")

    def __str__(self):
        return f'{self.__class__.__name__}({self.id=}, {self.email=}, {self.role=})'
