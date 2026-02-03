from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.orm import DataBase
from src.schemas.resume_schema import CreateResume
from src.database.models.resumes_model import ResumeModel
from src.database.models.users_model import UserModel

from .utils import check_permissions  # наша проверка прав

router_resumes = APIRouter(tags=["Резюме"])


@router_resumes.post("/resumes/add")
async def create_resume(
        resume: CreateResume,
        user: UserModel = Depends(check_permissions("resume", "create")),
) -> dict[str, int]:
    await DataBase.insert_resume(resume.name, resume.title, resume.description, resume.salary, user.email)

    return {'response': 200}


@router_resumes.post("/resumes/read{user_email}")
async def create_resume(
        resume: CreateResume,
        user: UserModel = Depends(check_permissions("resume", "read")),
) -> dict[str, int]:
    await DataBase.insert_resume(resume.name, resume.title, resume.description, resume.salary, user.email)

    return {'response': 200}
