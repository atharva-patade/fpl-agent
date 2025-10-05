"""
Configuration management for FPL Agent.
Handles environment variables and application settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI Configuration
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_api_host: str = Field(..., alias="OPENAI_API_HOST")
    openai_api_version: str = Field(default="2024-07-01-preview")
    openai_deployment: str = Field(default="gpt-4.1")
    
    # FPL API Configuration
    fpl_base_url: str = Field(default="https://fantasy.premierleague.com/api")
    
    # Cache Configuration
    cache_ttl_seconds: int = Field(default=900)  # 15 minutes
    enable_cache: bool = Field(default=True)
    
    # Agent Configuration
    agent_temperature: float = Field(default=0.7)
    agent_max_iterations: int = Field(default=15)
    agent_verbose: bool = Field(default=True)
    
    # Application
    log_level: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
