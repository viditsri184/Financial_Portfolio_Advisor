from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic import Extra
import os


class Settings(BaseSettings):
    azure_openai_endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")

    azure_openai_chat_deployment: str = Field(..., env="AZURE_OPENAI_CHAT_DEPLOYMENT")
    azure_openai_embedding_deployment: str = Field(..., env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    debug: bool = Field(True, env="DEBUG")
    allowed_origins: str = Field("*", env="ALLOWED_ORIGINS")

    class Config:
        # VERY IMPORTANT — load .env from project root
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", ".env"))
        env_file_encoding = "utf-8"
        extra = "ignore"   # <-- THIS FIXES YOUR ERROR


settings = Settings()
