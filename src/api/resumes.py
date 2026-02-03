from fastapi import APIRouter, Depends, Path
from pydantic import EmailStr
from typing import List, Annotated

from src.database.orm import DataBase
from src.schemas.resume_schema import CreateResume, Resume
from src.schemas.user_schema import User

from src.database.models.resumes_model import ResumeModel
from src.database.models.users_model import UserModel


from .utils import check_permissions

router_resumes = APIRouter(tags=["Резюме"], prefix="/resumes")


@router_resumes.post("/add", summary='Создание резюме пользователю')
async def create_resume(
        resume: CreateResume,
        user: UserModel = Depends(check_permissions("resume", "create")),
    ) -> dict[str, int]:
    ''' Создание резюме. Получаем pydantic схему резюме и создателя (провалидированного на права) '''

    await DataBase.insert_resume(resume.name, resume.title, resume.description, resume.salary, user.email)
    return {'response': 200}


@router_resumes.get("/read/all/", summary='Все пользователи с их резюме')
async def read_all_resumes(
        user: Annotated[User, Depends(check_permissions("resume", "read", all_action=True))]
    ):
    ''' Чтение всех пользователей с их relationship - resumes. all_action=True т.к. чтение не своего резюме, а всех '''
    users = await DataBase.get_all_resumes()
    return users


@router_resumes.get("/read/{email}/", summary='Чтение резюме пользователя по email')
async def read_resumes_user(
        email: Annotated[EmailStr, Path(..., title='email пользователя, чьи резюме читаем')],
        user: UserModel = Depends(check_permissions("user", "read")),
    ) -> List[Resume]:
    ''' Получение резюме пользователя, email которого принимаем '''

    resumes = await DataBase.get_all_user_resumes(email)
    return resumes
