"""
Configuration models for CC-Balancer using Pydantic v2.
"""

import os
import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")
    reload: bool = Field(default=False, description="Auto-reload on code changes (dev only)")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper


class RoutingConfig(BaseModel):
    """Routing strategy configuration."""

    strategy: Literal["round-robin", "weighted"] = Field(
        default="weighted", description="Routing strategy"
    )


class CacheConfig(BaseModel):
    """Request caching configuration."""

    enabled: bool = Field(default=True, description="Enable request deduplication cache")
    ttl_seconds: int = Field(
        default=60, ge=1, le=3600, description="Cache time-to-live in seconds"
    )
    max_size: int = Field(
        default=1000, ge=10, le=10000, description="Maximum cache entries"
    )


class ErrorHandlingConfig(BaseModel):
    """Error handling and failover configuration."""

    failure_threshold: int = Field(
        default=3, ge=1, le=10, description="Consecutive failures before circuit opens"
    )
    recovery_interval_seconds: int = Field(
        default=30, ge=5, le=300, description="Health check interval in seconds"
    )
    retry_backoff: list[int] = Field(
        default=[1, 2, 4, 8, 30],
        description="Retry backoff intervals in seconds",
    )


class ProviderConfig(BaseModel):
    """Individual provider configuration."""

    name: str = Field(..., min_length=1, description="Unique provider name")
    base_url: HttpUrl = Field(..., description="Provider base URL")
    auth_type: Literal["oauth", "api_key"] = Field(
        default="api_key", description="Authentication type"
    )
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    oauth_client_id: Optional[str] = Field(default=None, description="OAuth client ID")
    oauth_client_secret: Optional[str] = Field(default=None, description="OAuth client secret")
    weight: int = Field(default=1, ge=1, le=100, description="Provider weight for routing")
    priority: int = Field(default=1, ge=1, le=10, description="Provider priority")
    timeout_seconds: int = Field(
        default=30, ge=1, le=300, description="Request timeout in seconds"
    )

    @field_validator("api_key", "oauth_client_id", "oauth_client_secret")
    @classmethod
    def expand_env_vars(cls, v: Optional[str]) -> Optional[str]:
        """Expand environment variables in format ${VAR_NAME}."""
        if v is None:
            return None

        def replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return re.sub(r"\$\{([^}]+)\}", replacer, v)

    def model_post_init(self, __context: object) -> None:
        """Validate provider configuration after initialization."""
        if self.auth_type == "api_key" and not self.api_key:
            raise ValueError(f"Provider {self.name}: api_key required for api_key auth_type")
        if self.auth_type == "oauth" and (
            not self.oauth_client_id or not self.oauth_client_secret
        ):
            raise ValueError(
                f"Provider {self.name}: oauth_client_id and oauth_client_secret "
                "required for oauth auth_type"
            )


class AppConfig(BaseModel):
    """Complete application configuration."""

    server: ServerConfig = Field(default_factory=ServerConfig)
    routing: RoutingConfig = Field(default_factory=RoutingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    error_handling: ErrorHandlingConfig = Field(default_factory=ErrorHandlingConfig)
    providers: list[ProviderConfig] = Field(
        default_factory=list, min_length=1, description="List of provider configurations"
    )

    @field_validator("providers")
    @classmethod
    def validate_unique_names(cls, v: list[ProviderConfig]) -> list[ProviderConfig]:
        """Ensure provider names are unique."""
        names = [p.name for p in v]
        if len(names) != len(set(names)):
            duplicates = [name for name in names if names.count(name) > 1]
            raise ValueError(f"Duplicate provider names found: {set(duplicates)}")
        return v
