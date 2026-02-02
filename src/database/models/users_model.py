from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import Base
from sqlalchemy import String
from src.enums import Role


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    middle_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(String(300), unique=True, nullable=False)
    role: Mapped[Role] = mapped_column(nullable=False, server_default="user")

    def __str__(self):
        return f'{self.__class__.__name__}({self.id=}, {self.name=}, {self.age=}, {self.role=})'
