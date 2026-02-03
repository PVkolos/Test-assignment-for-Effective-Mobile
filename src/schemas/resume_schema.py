from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, model_validator
from src.enums import Role


class CreateResume(BaseModel):
    name: Annotated[str, Field(..., title="Имя пользователя", min_length=2, max_length=100)]
    title: Annotated[str, Field(..., title="Заголовок резюме", min_length=5, max_length=300)]
    description: Annotated[str, Field(..., title="Описание резюме", min_length=4, max_length=100)]
    salary: Annotated[int, Field(..., title="Зарплатные ожидания")]


class Resume(CreateResume):
    id: int
    email: Annotated[EmailStr, Field(..., title="email создателя")]
