from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.schemas.resume_schema import Resume

from src.database.create_session import async_engine, async_session

from src.database.models.base_model import Base
from src.database.models.users_model import UserModel
from src.database.models.roles_model import Role
from src.database.models.rights_matrix_model import AccessRoleRule
from src.database.models.business_elements_model import BusinessElement
from src.database.models.resumes_model import ResumeModel


class DataBase:
    @staticmethod
    async def create_table():
        async with async_engine.begin() as connection:
            await connection.run_sync(
                Base.metadata.drop_all,
                tables=[ResumeModel.__table__]
            )
            print("Database table dropped")
            await connection.run_sync(Base.metadata.create_all)
            print("Database table created")

    @staticmethod
    async def insert_user(name, surname, middle_name, email, password, role):
        user = UserModel(name=name, surname=surname, middle_name=middle_name, email=email, password=password, role=role)
        async with async_session() as session:
            session.add(user)
            await session.commit()

    @staticmethod
    async def insert_resume(name, title, description, salary, email):
        resume = ResumeModel(name=name, email=email, title=title, description=description, salary=salary)
        async with async_session() as session:
            session.add(resume)
            await session.commit()

    @staticmethod
    async def delete_user(email):
        async with async_session() as session:
            query = select(UserModel).where(UserModel.email == email)
            result = await session.execute(query)
            user = result.scalars().first()
            user.is_active = False
            await session.commit()

    @staticmethod
    async def update_user(email, name, surname, middle_name):
        async with async_session() as session:
            query = select(UserModel).where(UserModel.email == email)
            result = await session.execute(query)
            user = result.scalars().first()
            if name is not None: user.name = name
            if surname is not None: user.surname = surname
            if middle_name is not None: user.middle_name = middle_name

            await session.commit()

    @staticmethod
    async def get_user(email):
        async with async_session() as session:
            query = (
                select(UserModel)
                .where(UserModel.email == email)
            )
            res = await session.execute(query)
            result = res.scalars().first()
            return result

    @staticmethod
    async def get_business_element_id(element_name):
        async with async_session() as session:
            query = (
                select(BusinessElement.id)
                .where(BusinessElement.name == element_name)
            )
            res = await session.execute(query)
            result = res.scalars().first()
            return result

    @staticmethod
    async def get_rule(user, element_id):
        async with async_session() as session:
            role_stmt = (
                select(Role.id)
                .where(Role.name == user.role)
            )
            role = await session.execute(role_stmt)
            user_role = role.scalars().first()
            query = (
                select(AccessRoleRule)
                .where(
                    AccessRoleRule.role_id == user_role,
                    AccessRoleRule.element_id == element_id
                )
            )
            res = await session.execute(query)
            result = res.scalars().first()
            return result

    @staticmethod
    async def get_owner_resume(resume_id):
        async with async_session() as session:
            query = (
                select(ResumeModel.email)
                .where(ResumeModel.id == resume_id)
            )
            res = await session.execute(query)
            result = res.scalars().first()
            return result

    @staticmethod
    async def get_all_user_resumes(email):
        async with async_session() as session:
            query = (
                select(ResumeModel)
                .where(ResumeModel.email == email)
            )
            res = await session.execute(query)
            result = res.unique().scalars().all()
            return [Resume.model_validate(var, from_attributes=True) for var in result]
