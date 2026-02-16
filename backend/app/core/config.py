from pydantic import computed_field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Literal
from enum import Enum

class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # App
    APP_ENV: AppEnv = AppEnv.DEVELOPMENT
    PROJECT_NAME: str = "ClinicCare Mini EMR"

    # Admin
    ADMIN_NAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # PostgreSQL
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
        )
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    REDIS_USERNAME: str | None = None
    REDIS_USE_SSL: bool = False

    @computed_field
    def REDIS_DSN(self) -> RedisDsn:
        """Build Redis DSN from components"""
        scheme = "rediss" if self.REDIS_USE_SSL else "redis"

        return RedisDsn.build(
            scheme=scheme,
            username=self.REDIS_USERNAME,
            password=self.REDIS_PASSWORD,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(self.REDIS_DB),
        )
    
    # Auth
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    @computed_field
    def CORS_ORIGINS_LIST(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings() # type: ignore
