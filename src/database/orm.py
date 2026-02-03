from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.schemas.resume_schema import Resume
from src.schemas.access_roles_rules_schema import AccessRolesRules
from src.schemas.business_element_schema import ElementBusiness
from src.schemas.role_schema import Role, RoleRelationship
from src.schemas.user_schema import UserRelationship

from src.database.create_session import async_engine, async_session

from src.database.models.base_model import Base
from src.database.models.users_model import UserModel
from src.database.models.roles_model import RoleModel
from src.database.models.rights_matrix_model import AccessRoleRuleModel
from src.database.models.business_elements_model import BusinessElementModel
from src.database.models.resumes_model import ResumeModel


class DataBase:
    @staticmethod
    async def create_table():
        async with async_engine.begin() as connection:
            await connection.run_sync(
                Base.metadata.drop_all,
                tables=[ResumeModel.__table__, UserModel.__table__, AccessRoleRuleModel.__table__]
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
    async def insert_rule(role_id, element_id, read_permission, read_all_permission, create_permission, update_permission, update_all_permission, delete_permission, delete_all_permission):
        rule = AccessRoleRuleModel(
            role_id=role_id,
            element_id=element_id,
            read_permission=read_permission,
            read_all_permission=read_all_permission,
            create_permission=create_permission,
            update_permission=update_permission,
            update_all_permission=update_all_permission,
            delete_permission=delete_permission,
            delete_all_permission=delete_all_permission
        )
        async with async_session() as session:
            session.add(rule)
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
                select(BusinessElementModel.id)
                .where(BusinessElementModel.name == element_name)
            )
            res = await session.execute(query)
            result = res.scalars().first()
            return result

    @staticmethod
    async def get_rule(user, element_id):
        async with async_session() as session:
            role_stmt = (
                select(RoleModel.id)
                .where(RoleModel.name == user.role)
            )
            role = await session.execute(role_stmt)
            user_role = role.scalars().first()
            query = (
                select(AccessRoleRuleModel)
                .where(
                    AccessRoleRuleModel.role_id == user_role,
                    AccessRoleRuleModel.element_id == element_id
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

    @staticmethod
    async def get_all_resumes():
        async with async_session() as session:
            query = (
                select(UserModel)
                .options(selectinload(UserModel.resumes))
            )
            res = await session.execute(query)
            result = res.unique().scalars().all()
            return [UserRelationship.model_validate(var, from_attributes=True) for var in result]

    @staticmethod
    async def get_all_business_elements():
        async with async_session() as session:
            query = (
                select(BusinessElementModel)
            )
            res = await session.execute(query)
            result = res.unique().scalars().all()
            return [ElementBusiness.model_validate(var, from_attributes=True) for var in result]


    @staticmethod
    async def get_access_roles_rules():
        async with async_session() as session:
            query = (
                select(RoleModel)
                .options(selectinload(RoleModel.rules))
            )
            res = await session.execute(query)
            result = res.unique().scalars().all()
            return [RoleRelationship.model_validate(var, from_attributes=True) for var in result]

    @staticmethod
    async def check_role_id(role_id):
        async with async_session() as session:
            query = (
                select(RoleModel)
                .where(RoleModel.id == role_id)
            )
            res = await session.execute(query)
            result = res.scalars().one_or_none()
            return result

    @staticmethod
    async def check_element_id(element_id):
        async with async_session() as session:
            query = (
                select(BusinessElementModel)
                .where(BusinessElementModel.id == element_id)
            )
            res = await session.execute(query)
            result = res.scalars().one_or_none()
            return result

    @staticmethod
    async def check_rule_exists(element_id, role_id, rule_id=None):
        async with async_session() as session:
            if not rule_id:
                query = (
                    select(AccessRoleRuleModel)
                    .where(
                        AccessRoleRuleModel.element_id == element_id,
                        AccessRoleRuleModel.role_id == role_id
                    )
                )
                res = await session.execute(query)
                result = res.scalars().one_or_none()
                return result
            else:
                rule = await session.get(AccessRoleRuleModel, rule_id)
                return rule

    @staticmethod
    async def delete_rule(rule_id):
        async with async_session() as session:
            rule = await session.get(AccessRoleRuleModel, rule_id)
            await session.delete(rule)
            await session.commit()

    @staticmethod
    async def get_all_roles():
        async with async_session() as session:
            query = (
                select(RoleModel)
            )
            res = await session.execute(query)
            result = res.unique().scalars().all()
            return [Role.model_validate(var, from_attributes=True) for var in result]

    @staticmethod
    async def user_exist(email):
        async with async_session() as session:
            query = (
                select(UserModel)
                .where(UserModel.email == email)
            )
            res = await session.execute(query)
            result = res.scalars().one_or_none()
            return result
