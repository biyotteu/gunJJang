from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    ADMIN_ID: str
    ADMIN_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    
    class Config:
        env_file = "../.env"

@lru_cache()
def get_settings():
    return Settings()
