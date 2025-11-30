"""
Core configuration for RAG Pipeline Query Endpoint.

Settings class loads all environment variables using Pydantic BaseSettings
per Constitution Rule V (Secure credential management).
"""

from typing import Literal

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    Per Constitution Rule V, credentials must never be hardcoded.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra env vars not defined in model
        env_parse_enums=True,  # Parse enums from strings
    )

    # OpenAI API Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for embeddings and LLM",
        min_length=20,
        alias="OPENAI_API_KEY",
    )

    # Qdrant Cloud Configuration
    qdrant_url: HttpUrl = Field(
        ...,
        description="Qdrant Cloud instance URL",
        alias="QDRANT_URL",
    )

    qdrant_api_key: str = Field(
        ...,
        description="Qdrant Cloud API key",
        min_length=20,
        alias="QDRANT_API_KEY",
    )

    # Neon Postgres Configuration
    neon_connection_string: str = Field(
        ...,
        description="Neon Postgres connection string (postgres://...)",
        alias="NEON_CONNECTION_STRING",
    )

    # Better-Auth Configuration
    better_auth_secret: str = Field(
        ...,
        description="Better-Auth JWT secret for token validation",
        min_length=32,
        alias="BETTER_AUTH_SECRET",
    )

    better_auth_issuer: str = Field(
        default="better-auth",
        description="Expected JWT issuer claim",
        alias="BETTER_AUTH_ISSUER",
    )

    better_auth_audience: str = Field(
        default="physical-ai-platform",
        description="Expected JWT audience claim",
        alias="BETTER_AUTH_AUDIENCE",
    )

    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for rate limiting",
        alias="REDIS_URL",
    )

    # Rate Limiting Configuration
    rate_limit_requests: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Maximum requests per user per minute",
        alias="RATE_LIMIT_REQUESTS",
    )

    rate_limit_window_seconds: int = Field(
        default=60,
        ge=1,
        le=3600,
        description="Rate limit window in seconds",
        alias="RATE_LIMIT_WINDOW_SECONDS",
    )

    # Timeout Configuration
    vector_db_timeout: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Qdrant vector database timeout in seconds (FR-015)",
        alias="VECTOR_DB_TIMEOUT",
    )

    llm_timeout: int = Field(
        default=25,
        ge=5,
        le=60,
        description="OpenAI LLM timeout in seconds (FR-015)",
        alias="LLM_TIMEOUT",
    )

    # Application Configuration
    env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
        alias="ENV",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
        alias="LOG_LEVEL",
    )

    # API Configuration
    api_version: str = Field(
        default="v1",
        description="API version prefix",
        alias="API_VERSION",
    )

    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
        alias="CORS_ORIGINS",
    )

    # LLM Configuration
    llm_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI LLM model to use",
        alias="LLM_MODEL",
    )

    llm_max_tokens: int = Field(
        default=1500,
        ge=100,
        le=4000,
        description="Maximum tokens for LLM response",
        alias="LLM_MAX_TOKENS",
    )

    # Vector Search Configuration
    vector_collection_name: str = Field(
        default="textbook-chapters",
        description="Qdrant collection name",
        alias="VECTOR_COLLECTION_NAME",
    )

    vector_score_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for vector search (FR-003)",
        alias="VECTOR_SCORE_THRESHOLD",
    )

    # Embedding Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model",
        alias="EMBEDDING_MODEL",
    )

    embedding_dimensions: int = Field(
        default=1536,
        description="Embedding dimensions",
        alias="EMBEDDING_DIMENSIONS",
    )

    @field_validator("neon_connection_string")
    @classmethod
    def validate_postgres_connection_string(cls, v: str) -> str:
        """Validate Postgres connection string format."""
        if not v.startswith("postgres://") and not v.startswith("postgresql://"):
            raise ValueError("NEON_CONNECTION_STRING must start with postgres:// or postgresql://")
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            # Handle comma-separated string or JSON array string
            if v.startswith("["):
                import json

                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


# Singleton instance (lazy initialization to allow testing)
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get singleton Settings instance.

    Returns cached instance if available, otherwise creates new one.
    This allows testing with different configurations via monkeypatch.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience instance for non-test code
# Note: This will fail if required env vars are missing
# In tests, use get_settings() after setting env vars
try:
    settings = Settings()
except Exception:
    # Allow import to succeed even if env vars are missing (for testing)
    settings = None  # type: ignore[assignment]
