from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
import secrets
from pathlib import Path

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Iqraa Library Management System"
    
    # Debug mode
    DEBUG: bool = False
    
    # Database settings
    POSTGRES_DB: str = "iqraa_db"
    POSTGRES_USER: str = "iqraa_user"
    POSTGRES_PASSWORD: str = "iqraa_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # CORS Configuration
    CORS_ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://localhost:8080"

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError("CORS_ALLOWED_ORIGINS must be a string or list")

    # Django settings
    DJANGO_SECRET_KEY: str = secrets.token_urlsafe(32)
    ALLOWED_HOSTS: Union[str, List[str]] = "localhost,127.0.0.1"

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError("ALLOWED_HOSTS must be a string or list")

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # File Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # ML Model
    MODEL_DIR: Path = Path("models")
    RECOMMENDATION_THRESHOLD: float = 0.5
    MAX_RECOMMENDATIONS: int = 10

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 