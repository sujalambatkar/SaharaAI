from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    groq_api_key: str = ""
    qdrant_url: str = "https://714c4961-d588-4990-a2a0-fc525035ee46.eu-west-1-0.aws.cloud.qdrant.io"
    qdrant_api_key: str = ""
    qdrant_collection: str = "sahara_kb"
    postgres_url: str = "postgresql+asyncpg://sahara:sahara@postgres:5432/saharadb"
    langsmith_api_key: str = ""
    langsmith_project: str = "sahara-ai"
    retrieval_mode: str = "hybrid"
    confidence_threshold: float = 0.65
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
