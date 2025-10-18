from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    api_key: str = Field(..., env="API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()