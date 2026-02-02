from sqlalchemy import select
from src.database.create_session import async_engine, async_session

from src.database.models.base_model import Base
from src.database.models.users_model import UserModel

from sqlalchemy.orm import selectinload, contains_eager, joinedload


class DataBase:
    @staticmethod
    async def create_table():
        async with async_engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            print("Database table dropped")
            await connection.run_sync(Base.metadata.create_all)
            print("Database table created")
