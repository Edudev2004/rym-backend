"""
Configuración centralizada de la aplicación mediante Pydantic Settings
"""
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
import os
import json

class Settings(BaseSettings):
    # App General
    PROJECT_NAME: str = "R&M Personaliza API"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"

    # Supabase Credentials
    SUPABASE_URL: str = "https://tu-proyecto.supabase.co"
    SUPABASE_ANON_KEY: str = "tu_clave_anonima_publica"
    SUPABASE_SERVICE_ROLE_KEY: str = "tu_clave_service_role_secreta"

    # PostgreSQL Direct Connection
    DATABASE_URL: str = "postgresql://postgres:tu_password@db.tu-proyecto.supabase.co:5432/postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_SSLMODE: str = "prefer"

    # Seguridad JWT
    JWT_SECRET: str = "super_secret_jwt_key_rym_personaliza_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # Modo Stubs para integraciones
    OSE_SUNAT_MODO: str = "STUB"
    CANALES_DIGITALES_MODO: str = "STUB"

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
