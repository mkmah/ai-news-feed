from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    youtube_channels: List[str] = ["UC0m81bQuthaQZmFbXEY9QSw"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
