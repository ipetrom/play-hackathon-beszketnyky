from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Centralna konfiguracja aplikacji ładowana ze zmiennych środowiskowych
    i pliku .env.
    """
    
    # Ładowanie z pliku .env w głównym folderze projektu
    # (../.env względem folderu backend/utils)
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding='utf-8', extra='ignore')

    # Klucze API
    OPENAI_API_KEY: str = "brak_klucza_openai"
    SCALEWAY_API_KEY: str = "a3c535e8-93ba-46bf-847e-7115853dcc0e"

    # URL dla API Scaleway (możesz je tu trzymać)
    SCALEWAY_API_URL: str = "https://api.scaleway.ai/f515e043-422b-48bf-95a7-2da7063d7858/v1"

# Tworzymy jedną, globalną instancję ustawień,
# którą inne moduły będą mogły importować.
settings = Settings()

# Testowe wydrukowanie, aby sprawdzić, czy klucze się ładują
# (Usuń to w wersji produkcyjnej)
# print(f"Załadowano klucz OpenAI: ...{settings.OPENAI_API_KEY[-4:]}")
# print(f"Załadowano klucz Scaleway: ...{settings.SCALEWAY_API_KEY[-4:]}")