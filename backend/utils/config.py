from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Scaleway ---
    SCALEWAY_API_URL: str
    SCALEWAY_API_KEY: str

    # --- Database ---
    DB_URL: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # ✅ Nowy styl konfiguracji (Pydantic v2)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()