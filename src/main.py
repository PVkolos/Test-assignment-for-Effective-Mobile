from contextlib import asynccontextmanager
from tkinter.font import names

import uvicorn
from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def root() -> str:
    return 'Тестовый проект, демонстрирующий навыки работы со стеком FastAPI + PostrgreSQL + Docker для компании Effective Mobile'


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
