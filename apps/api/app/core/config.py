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
    # Generation v2 flags — additive; legacy emitters stay default path
    generation_pipeline: str = "legacy"  # legacy | v2
    gen_v2_planner: bool = True  # Phase 1: write WebsitePlan artifact (safe)
    gen_v2_theme: bool = True  # Phase 2: ThemeEngine → CSS variables
    gen_v2_components: bool = True  # Phase 3: shell variants
    gen_v2_content: bool = True  # Phase 4: niche copy
    gen_v2_validator: bool = True  # Phase 5: semantic checks + niche dispatch
    gen_v2_images: bool = True  # Phase 6: image collections
    gen_v2_ai_planner: bool = False  # Phase 7: optional LLM plan enrich
    # TinyGPT hybrid — localhost:8100; soft-fails to rule generators
    tinygpt_base_url: str = "http://127.0.0.1:8100"
    tinygpt_hybrid: bool = True
    tinygpt_timeout_seconds: float = 45.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
