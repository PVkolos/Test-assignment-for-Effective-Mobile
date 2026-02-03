from fastapi import APIRouter, Depends, Path
from pydantic import EmailStr
from typing import List, Annotated

from src.database.orm import DataBase
from src.schemas.resume_schema import CreateResume, Resume
from src.database.models.resumes_model import ResumeModel
from src.database.models.users_model import UserModel

from .utils import check_permissions

router_resumes = APIRouter(tags=["Резюме"], prefix="/resumes")


@router_resumes.post("/add", summary='Создание резюме пользователю')
async def create_resume(
        resume: CreateResume,
        user: UserModel = Depends(check_permissions("resume", "create")),
    ) -> dict[str, int]:
    await DataBase.insert_resume(resume.name, resume.title, resume.description, resume.salary, user.email)

    return {'response': 200}


@router_resumes.get("/read/{email}/", summary='Чтение резюме пользователя по email')
async def read_resumes(
        email: Annotated[EmailStr, Path(..., title='email пользователя, чьи резюме читаем')],
        user: UserModel = Depends(check_permissions("user", "read")),
) -> List[Resume]:
    resumes = await DataBase.get_all_user_resumes(email)

    return resumes
