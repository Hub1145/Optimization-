import json
import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    PROJECT_NAME: str = "StrategyOptimizer API"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "strategy_optimizer"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    REDIS_URL: str = "redis://localhost:6379/0"

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "secret"

    @classmethod
    def load(cls):
        config_data = {}
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_data = json.load(f)

        # Override with environment variables if present
        for field in cls.model_fields:
            env_val = os.getenv(field.upper())
            if env_val:
                config_data[field] = env_val

        return cls(**config_data)

    @property
    def database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings.load()
