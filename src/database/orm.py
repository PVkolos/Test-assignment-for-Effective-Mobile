from sqlalchemy import select
from src.database.create_session import async_engine, async_session

from src.database.models.base_model import Base
from src.database.models.users_model import UserModel


class DataBase:
    @staticmethod
    async def create_table():
        async with async_engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
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