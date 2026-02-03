from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, model_validator
from src.enums import Role


class CreateUser(BaseModel):
    name: Annotated[str, Field(..., title="Имя пользователя", min_length=2, max_length=100)]
    surname: Annotated[str, Field(..., title="Фамилия пользователя", min_length=2, max_length=100)]
    middle_name: Annotated[str, Field(..., title="Отчество пользователя", min_length=4, max_length=100)]
    password: Annotated[str, Field(..., title="Пароль пользователя", max_length=50, min_length=5, repr=False)]
    password_again: Annotated[str, Field(..., title="Повтор пароля пользователя", max_length=50, min_length=5, repr=False)]
    email: Annotated[EmailStr, Field(..., title="email пользователя")]
    role: Annotated[str, Field(..., title='Роль пользователя')]

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'CreateUser':
        password1 = self.password
        password2 = self.password_again

        if password1 is not None and password2 is not None and password1 != password2:
            raise ValueError('Пароли не совпадают')
        return self


class User(CreateUser):
    id: int
    is_active: bool
