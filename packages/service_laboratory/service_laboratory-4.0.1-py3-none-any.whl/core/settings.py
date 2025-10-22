from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = Field(default="postgresql+asyncpg://user:password@localhost:5432/db")


settings = Settings()
