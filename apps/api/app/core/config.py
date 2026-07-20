from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Website Builder"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    # Default to SQLite for zero-deps local demo; override with Postgres in .env / Compose
    database_url: str = "sqlite:///./ai_builder.db"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    artifact_root: str = "./artifacts"
    generated_projects_root: str = "./generated_projects"
    preview_build_timeout_seconds: int = 120
    ai_base_url: str = "https://api.openai.com/v1"
    ai_api_key: str = ""
    ai_model: str = "local-website-ai-v1"
    ai_provider: str = "local"  # local | openai — local needs no API key
    ai_mock: bool = True
    worker_poll_interval_seconds: float = 2.0
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
