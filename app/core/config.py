from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LeadPing SaaS"
    environment: str = "development"
    debug: bool = False
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24

    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/leadping"
    redis_url: str = "redis://redis:6379/0"

    default_plan_name: str = "starter"
    starter_monthly_limit: int = 200
    growth_monthly_limit: int = 2000
    pro_monthly_limit: int = 20000

    rate_limit_per_minute: int = 60

    admin_email: str = "admin@example.com"
    admin_password: str = "admin12345"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
