"""
Konfiguracja aplikacji z wykorzystaniem Pydantic Settings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    """Ustawienia aplikacji"""
    
    # ====== PODSTAWOWE ======
    ENVIRONMENT: str = Field(default="development", description="Środowisko uruchomienia")
    DEBUG: bool = Field(default=True, description="Tryb debug")
    API_HOST: str = Field(default="0.0.0.0", description="Host API")
    API_PORT: int = Field(default=8000, description="Port API")
    
    # ====== CORS ======
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
        description="Dozwolone originy dla CORS"
    )
    
    # ====== BAZA DANYCH ======
    POSTGRES_HOST: str = Field(default="localhost", description="Host PostgreSQL")
    POSTGRES_PORT: int = Field(default=5432, description="Port PostgreSQL")
    POSTGRES_DB: str = Field(default="hackathon_local", description="Nazwa bazy danych")
    POSTGRES_USER: str = Field(default="postgres", description="Użytkownik bazy danych")
    POSTGRES_PASSWORD: str = Field(default="postgres", description="Hasło bazy danych")
    
    # Alternatywne ustawienia dla developmentu
    POSTGRES_HOST_LOCAL: str = Field(default="localhost")
    POSTGRES_DB_LOCAL: str = Field(default="hackathon_local")
    POSTGRES_USER_LOCAL: str = Field(default="postgres")
    POSTGRES_PASSWORD_LOCAL: str = Field(default="postgres")
    
    # ====== AI MODELE ======
    # OpenAI (Strategist)
    OPENAI_API_KEY: str = Field(description="Klucz API OpenAI")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="Model OpenAI dla Strategist")
    
    # Scaleway GenAI (Workforce)
    SCALEWAY_API_KEY: str = Field(description="Klucz API Scaleway")
    SCALEWAY_PROJECT_ID: str = Field(description="ID projektu Scaleway")
    SCALEWAY_GENAI_ENDPOINT: str = Field(
        default="https://api.scaleway.com/genai/v1alpha1",
        description="Endpoint Scaleway GenAI"
    )
    SCALEWAY_MODEL: str = Field(default="mistral-7b-instruct", description="Model Mistral")
    
    # ====== STORAGE ======
    SCALEWAY_ACCESS_KEY: str = Field(description="Access Key Scaleway Object Storage")
    SCALEWAY_SECRET_KEY: str = Field(description="Secret Key Scaleway Object Storage")
    SCALEWAY_BUCKET_NAME: str = Field(default="hackathon-storage", description="Nazwa bucket")
    SCALEWAY_REGION: str = Field(default="fr-par", description="Region Scaleway")
    
    # ====== SECURITY ======
    JWT_SECRET_KEY: str = Field(description="Klucz tajny JWT")
    JWT_ALGORITHM: str = Field(default="HS256", description="Algorytm JWT")
    JWT_EXPIRE_MINUTES: int = Field(default=1440, description="Czas wygaśnięcia JWT w minutach")
    
    # ====== LANGGRAPH ======
    LANGGRAPH_CHECKPOINTER: str = Field(default="postgres", description="Typ checkpointera LangGraph")
    LANGGRAPH_THREAD_TIMEOUT: int = Field(default=3600, description="Timeout wątku w sekundach")
    
    # ====== REDIS ======
    REDIS_HOST: str = Field(default="localhost", description="Host Redis")
    REDIS_PORT: int = Field(default=6379, description="Port Redis")
    REDIS_DB: int = Field(default=0, description="Numer bazy Redis")
    
    @property
    def database_url(self) -> str:
        """URL połączenia z bazą danych"""
        if self.ENVIRONMENT == "production":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return f"postgresql://{self.POSTGRES_USER_LOCAL}:{self.POSTGRES_PASSWORD_LOCAL}@{self.POSTGRES_HOST_LOCAL}:{self.POSTGRES_PORT}/{self.POSTGRES_DB_LOCAL}"
    
    @property
    def redis_url(self) -> str:
        """URL połączenia z Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Singleton instance
_settings = None

def get_settings() -> Settings:
    """Pobieranie singleton instance ustawień"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings