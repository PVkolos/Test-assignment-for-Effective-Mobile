from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .resumes_model import ResumeModel


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    middle_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=False)
    # role: Mapped[Role] = mapped_column(nullable=False, server_default="user")

    role: Mapped[str] = mapped_column(ForeignKey("roles.name"), nullable=False) # todo
    is_active: Mapped[bool] = mapped_column(server_default="True")

    resumes: Mapped[list["ResumeModel"]] = relationship(back_populates="user")

    def __str__(self):
        return f'{self.__class__.__name__}({self.id=}, {self.email=}, {self.role=})'
