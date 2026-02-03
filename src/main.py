from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from src.database.orm import DataBase

from src.api import router_main


@asynccontextmanager
async def create_db_table(app: FastAPI):
    # await DataBase.create_table()
    yield


app = FastAPI(lifespan=create_db_table)
app.include_router(router_main)


@app.get("/")
async def root() -> str:
    return 'Тестовый проект, демонстрирующий навыки работы со стеком FastAPI + PostrgreSQL для компании Effective Mobile'


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
