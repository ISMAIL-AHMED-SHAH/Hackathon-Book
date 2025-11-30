"""
Unit tests for core configuration Settings class (T008).

Tests cover:
- Environment variable loading and validation
- Field validators (Postgres connection string, CORS origins)
- Default values
- Boundary conditions for numeric fields
- Constitution Rule I: 100% type hints
- Constitution Rule II: 90%+ test coverage
"""

import os
from typing import Any

import pytest
from pydantic import ValidationError

from src.core.config import Settings


class TestSettingsValidation:
    """Test Settings class initialization and validation."""

    def test_settings_loads_from_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Settings loads all required environment variables."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,  # Min 32 chars
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()

        assert settings.openai_api_key == env_vars["OPENAI_API_KEY"]
        assert str(settings.qdrant_url) == env_vars["QDRANT_URL"] + "/"
        assert settings.qdrant_api_key == env_vars["QDRANT_API_KEY"]
        assert settings.neon_connection_string == env_vars["NEON_CONNECTION_STRING"]
        assert settings.better_auth_secret == env_vars["BETTER_AUTH_SECRET"]

    def test_settings_missing_required_field_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing required environment variables raise ValidationError."""
        # Clear all relevant env vars
        for key in [
            "OPENAI_API_KEY",
            "QDRANT_URL",
            "QDRANT_API_KEY",
            "NEON_CONNECTION_STRING",
            "BETTER_AUTH_SECRET",
        ]:
            monkeypatch.delenv(key, raising=False)

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        error_fields = {error["loc"][0] for error in errors}
        assert "openai_api_key" in error_fields or "OPENAI_API_KEY" in str(errors)

    def test_settings_uses_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Settings uses default values for optional fields."""
        # Set only required fields
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        # Clear optional env vars
        for key in ["REDIS_URL", "RATE_LIMIT_REQUESTS", "ENV", "LOG_LEVEL"]:
            monkeypatch.delenv(key, raising=False)

        settings = Settings()

        # Check defaults
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.rate_limit_requests == 10
        assert settings.rate_limit_window_seconds == 60
        assert settings.vector_db_timeout == 5
        assert settings.llm_timeout == 25
        assert settings.env == "development"
        assert settings.log_level == "INFO"
        assert settings.api_version == "v1"
        assert settings.llm_model == "gpt-4-turbo-preview"
        assert settings.llm_max_tokens == 1500
        assert settings.vector_collection_name == "textbook-chapters"
        assert settings.vector_score_threshold == 0.3
        assert settings.embedding_model == "text-embedding-3-small"
        assert settings.embedding_dimensions == 1536

    def test_openai_api_key_min_length(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that OPENAI_API_KEY must be at least 20 characters."""
        env_vars = {
            "OPENAI_API_KEY": "short",  # Less than 20 chars
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(
            error["loc"][0] == "OPENAI_API_KEY" and "at least 20 characters" in error["msg"]
            for error in errors
        )

    def test_better_auth_secret_min_length(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that BETTER_AUTH_SECRET must be at least 32 characters."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "short",  # Less than 32 chars
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(
            error["loc"][0] == "BETTER_AUTH_SECRET" and "at least 32 characters" in error["msg"]
            for error in errors
        )

    def test_neon_connection_string_postgres_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that NEON_CONNECTION_STRING must start with postgres:// or postgresql://."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "mysql://user:pass@host:5432/db",  # Wrong prefix
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any("must start with postgres://" in error["msg"] for error in errors)

    def test_neon_connection_string_postgresql_prefix_valid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that postgresql:// prefix is accepted for NEON_CONNECTION_STRING."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgresql://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()
        assert settings.neon_connection_string.startswith("postgresql://")

    def test_cors_origins_parses_json_array_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that CORS_ORIGINS parses JSON array string into list."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "CORS_ORIGINS": '["http://localhost:3000", "http://localhost:8000", "https://example.com"]',
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()
        assert settings.cors_origins == [
            "http://localhost:3000",
            "http://localhost:8000",
            "https://example.com",
        ]

    def test_rate_limit_requests_boundary_min(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that RATE_LIMIT_REQUESTS accepts minimum value of 1."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "RATE_LIMIT_REQUESTS": "1",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()
        assert settings.rate_limit_requests == 1

    def test_rate_limit_requests_boundary_max(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that RATE_LIMIT_REQUESTS accepts maximum value of 1000."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "RATE_LIMIT_REQUESTS": "1000",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()
        assert settings.rate_limit_requests == 1000

    def test_rate_limit_requests_below_min_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that RATE_LIMIT_REQUESTS below 1 raises ValidationError."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "RATE_LIMIT_REQUESTS": "0",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(
            error["loc"][0] == "RATE_LIMIT_REQUESTS"
            and "greater than or equal to 1" in error["msg"]
            for error in errors
        )

    def test_vector_db_timeout_boundary_min(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that VECTOR_DB_TIMEOUT accepts minimum value of 1."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "VECTOR_DB_TIMEOUT": "1",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()
        assert settings.vector_db_timeout == 1

    def test_llm_timeout_boundary_max(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that LLM_TIMEOUT accepts maximum value of 60."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "LLM_TIMEOUT": "60",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()
        assert settings.llm_timeout == 60

    def test_vector_score_threshold_boundary_min(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that VECTOR_SCORE_THRESHOLD accepts minimum value of 0.0."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "VECTOR_SCORE_THRESHOLD": "0.0",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()
        assert settings.vector_score_threshold == 0.0

    def test_vector_score_threshold_boundary_max(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that VECTOR_SCORE_THRESHOLD accepts maximum value of 1.0."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "VECTOR_SCORE_THRESHOLD": "1.0",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        settings = Settings()
        assert settings.vector_score_threshold == 1.0

    def test_env_accepts_valid_literal_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ENV accepts only valid literal values."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        # Test each valid environment
        for env_value in ["development", "staging", "production"]:
            monkeypatch.setenv("ENV", env_value)
            settings = Settings()
            assert settings.env == env_value

    def test_env_rejects_invalid_literal_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ENV rejects invalid literal values."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
            "ENV": "invalid",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "ENV" for error in errors)

    def test_log_level_accepts_valid_literal_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that LOG_LEVEL accepts only valid literal values."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        # Test each valid log level
        for log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            monkeypatch.setenv("LOG_LEVEL", log_level)
            settings = Settings()
            assert settings.log_level == log_level

    def test_qdrant_api_key_min_length(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that QDRANT_API_KEY must be at least 20 characters."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "short",  # Less than 20 chars
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any(
            error["loc"][0] == "QDRANT_API_KEY" and "at least 20 characters" in error["msg"]
            for error in errors
        )

    def test_better_auth_issuer_and_audience_defaults(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that BETTER_AUTH_ISSUER and BETTER_AUTH_AUDIENCE use default values."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        # Clear optional auth fields
        monkeypatch.delenv("BETTER_AUTH_ISSUER", raising=False)
        monkeypatch.delenv("BETTER_AUTH_AUDIENCE", raising=False)

        settings = Settings()
        assert settings.better_auth_issuer == "better-auth"
        assert settings.better_auth_audience == "physical-ai-platform"

    def test_get_settings_function_returns_singleton(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_settings() returns a singleton Settings instance."""
        from src.core.config import get_settings

        env_vars = {
            "OPENAI_API_KEY": "sk-test1234567890abcdef",
            "QDRANT_URL": "https://qdrant.example.com",
            "QDRANT_API_KEY": "qdrant-test-key-12345",
            "NEON_CONNECTION_STRING": "postgres://user:pass@host:5432/db",
            "BETTER_AUTH_SECRET": "a" * 32,
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        # Reset singleton
        import src.core.config as config_module

        config_module._settings = None

        # Get settings twice and verify it's the same instance
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2
        assert isinstance(settings1, Settings)
        assert settings1.env in ["development", "staging", "production"]
