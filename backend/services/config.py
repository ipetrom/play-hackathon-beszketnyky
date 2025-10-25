"""
Configuration settings for the Telecom News Multi-Agent System
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import dotenv

dotenv.load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
SCALEWAY_API_KEY = os.getenv("SCALEWAY_API_KEY", "")


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    serper_api_key: str = SERPER_API_KEY
    perplexity_api_key: str = PERPLEXITY_API_KEY
    scaleway_api_key: str = SCALEWAY_API_KEY
    scaleway_project_id: str = ""
    
    # Database
    database_url: str = "postgresql://root:cXf2dtQlN8m6*{tef,]B@151.115.13.23:12061/rdb"
    
    # Scaleway Object Storage
    scaleway_access_key: str = ""
    scaleway_secret_key: str = ""
    bucket_name: str = ""
    region: str = ""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    
    # Agent Configuration
    max_concurrent_agents: int = 5
    request_timeout: int = 30
    max_retries: int = 3
    
    # Serper Configuration
    serper_base_url: str = "https://google.serper.dev"
    max_search_results: int = 20
    
    # Perplexity Configuration
    perplexity_base_url: str = "https://api.perplexity.ai"
    perplexity_model: str = "sonar"
    
    # Scaleway Configuration
    scaleway_base_url: str = "https://api.scaleway.ai/f515e043-422b-48bf-95a7-2da7063d7858/v1"
    scaleway_model: str = "qwen3-235b-a22b-instruct-2507"
    scaleway_temperature: float = 0.7
    
    # Telecom-specific settings
    telecom_operators: List[str] = ["Play", "Orange", "T-Mobile", "Plus"]
    telecom_regulators: List[str] = ["UKE", "UOKiK"]
    telecom_ministries: List[str] = ["Ministerstwo Cyfryzacji", "Ministerstwo Rozwoju"]
    
    # Search domains
    domains: List[str] = ["prawo", "polityka", "financial"]
    
    # Content filtering
    min_content_length: int = 100
    max_content_length: int = 10000
    
    # Impact assessment
    impact_levels: List[str] = ["low", "medium", "high"]
    time_horizons: List[str] = ["immediate", "near", "medium"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
