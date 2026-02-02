from datetime import timedelta
from pathlib import Path

from pydantic.v1 import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class JWTAuth(BaseModel):
    private_key_path: Path = BASE_DIR.joinpath('certs/jwt-private.pem')
    public_key_path: Path = BASE_DIR.joinpath('certs/jwt-public.pem')
    algorithm: str = 'PS256'
    access_token_expire_minutes: timedelta = timedelta(minutes=30)
    refresh_token_expire_days: timedelta = timedelta(days=30)
    # access_token_expire_minutes: int = 60


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")


class DB_Settings(ConfigBase):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self):
        # DSN
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class Roles(BaseModel):
    admin: str = 'admin'
    user: str = 'user'
    guest: str = 'guest'


class Const(BaseModel):
    TOKEN_TYPE_FIELD: str = 'token_type'
    TOKEN_ACCESS_FIELD: str = 'access'
    TOKEN_REFRESH_FIELD: str = 'refresh'


class Settings:
    db: DB_Settings = DB_Settings()
    roles: Roles = Roles()
    const = Const()
    auth_jwt: JWTAuth = JWTAuth()


settings = Settings()
# auth_jwt: JWTAuth = JWTAuth()
