import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'dev')}", 
        extra="ignore",
    )
    database_url : str = "postgresql+asyncpg://carduser:cardpass@db:5432/carddb"
    cors_origins : list[str] = ["http://localhost:5173"]
    environment  : str = "dev"

settings = Settings()