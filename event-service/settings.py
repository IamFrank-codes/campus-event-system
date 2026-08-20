"""Runtime configuration loaded from environment variables."""
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-this-in-production")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./events.db")
    user_service_url: str = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8001")
    event_service_url: str = os.getenv("EVENT_SERVICE_URL", "http://127.0.0.1:8002")
    allowed_hosts: str = os.getenv("ALLOWED_HOSTS", "*")

    def validate(self) -> None:
        if self.environment.lower() in {"production", "prod"}:
            if len(self.jwt_secret_key) < 32 or self.jwt_secret_key == "dev-only-secret-change-this-in-production":
                raise RuntimeError("JWT_SECRET_KEY must be a strong 32+ character secret in production")
            if self.database_url.startswith("sqlite://"):
                raise RuntimeError("DATABASE_URL must use a server database in production")

settings = Settings()
settings.validate()
