import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Tabular Analytics"
    version: str = "0.1.0"
    
    # Environment
    domain: str = "finance"
    provider: str = "mock"
    log_level: str = "INFO"
    
    # Paths
    data_root: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    
    # LLM Settings
    hosted_api_key: str = "sk-REPLACE-ME"
    hosted_model: str = "gpt-4o-mini"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    
    # Infrastructure
    database_url: str = "postgresql+psycopg://user:password@localhost:5432/analytics"
    redis_url: str = "redis://localhost:6379/0"
    otel_exporter_otlp_endpoint: str = ""
    
    # Security
    api_key: str = "test-api-key"
    enable_api_key_auth: bool = False
    
    # Magic Numbers
    cache_ttl: int = 3600
    max_rows_to_llm: int = 200

    class Config:
        env_file = ".env"

settings = Settings()
