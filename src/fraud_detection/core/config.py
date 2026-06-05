from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fraud-detection-api"
    app_env: str = "development"
    log_level: str = "INFO"
    model_path: Path = Path("models/fraud_model.joblib")
    model_metadata_path: Path = Path("models/model_metadata.json")
    mlflow_tracking_uri: str = "file:./mlruns"
    mlflow_experiment_name: str = "fraud-detection"
    mlflow_register_model: bool = False
    fraud_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        protected_namespaces=("settings_",),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
