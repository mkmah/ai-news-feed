from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    youtube_channels: List[str] = ["UC0m81bQuthaQZmFbXEY9QSw"]

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    youtube_proxy_username: Optional[str] = None
    youtube_proxy_password: Optional[str] = None

    openai_api_key: Optional[str] = None

    model_config = {
        "env_file": "app/.env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
