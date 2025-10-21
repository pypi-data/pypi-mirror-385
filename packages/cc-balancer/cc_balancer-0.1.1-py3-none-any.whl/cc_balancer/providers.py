"""
Provider abstraction layer for different authentication types.
"""

from abc import ABC, abstractmethod
from typing import Any

import httpx

from cc_balancer.config import ProviderConfig


class Provider(ABC):
    """Abstract base class for API providers."""

    def __init__(self, config: ProviderConfig) -> None:
        """
        Initialize provider with configuration.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.name = config.name
        self._client: httpx.AsyncClient | None = None

    @abstractmethod
    def get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers for requests.

        Returns:
            Dictionary of HTTP headers
        """
        pass

    async def get_client(self) -> httpx.AsyncClient:
        """
        Get or create async HTTP client.

        Returns:
            Configured HTTPX async client
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=str(self.config.base_url),
                timeout=httpx.Timeout(self.config.timeout_seconds),
                follow_redirects=True,
            )
        return self._client

    async def send_request(
        self,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """
        Send HTTP request to provider.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            headers: Optional additional headers
            json_data: Optional JSON body

        Returns:
            HTTP response
        """
        client = await self.get_client()

        # Merge authentication headers with request headers
        # Request headers first, then auth headers (auth headers take priority)
        merged_headers = {}
        if headers:
            merged_headers.update(headers)
        auth_headers = self.get_auth_headers()
        merged_headers.update(auth_headers)

        # Debug: log the actual headers being sent
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Provider {self.name}: Sending request to {path}")
        logger.info(f"Provider {self.name}: Headers = {merged_headers}")
        logger.info(f"Provider {self.name}: Body keys = {list(json_data.keys()) if json_data else 'None'}")

        response = await client.request(
            method=method,
            url=path,
            headers=merged_headers,
            json=json_data,
        )

        logger.info(f"Provider {self.name}: Response status = {response.status_code}")
        logger.info(f"Provider {self.name}: Response body = {response.text[:200]}")

        return response

    async def health_check(self) -> bool:
        """
        Perform health check on provider.

        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            client = await self.get_client()
            # Simple HEAD request to base URL
            response = await client.head("/", timeout=5.0)
            return response.status_code < 500
        except Exception:
            return False

    async def close(self) -> None:
        """Close HTTP client connections."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()


class APIKeyProvider(Provider):
    """Provider using API key authentication."""

    def get_auth_headers(self) -> dict[str, str]:
        """Get API key authentication headers."""
        if not self.config.api_key:
            raise ValueError(f"Provider {self.name}: API key not configured")

        # Anthropic API uses x-api-key header (case-sensitive)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Provider {self.name}: API key = {self.config.api_key[:20]}...")

        return {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
        }


class OAuthProvider(Provider):
    """Provider using OAuth 2.0 authentication."""

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize OAuth provider."""
        super().__init__(config)
        self._access_token: str | None = None

    def get_auth_headers(self) -> dict[str, str]:
        """Get OAuth authentication headers."""
        if not self._access_token:
            raise ValueError(f"Provider {self.name}: OAuth token not acquired")

        return {
            "Authorization": f"Bearer {self._access_token}",
            "anthropic-version": "2023-06-01",
        }

    async def acquire_token(self) -> None:
        """
        Acquire OAuth access token.

        Note: This is a placeholder for OAuth flow implementation.
        Full OAuth 2.0 flow will be implemented in Phase 6.
        """
        # TODO: Implement full OAuth 2.0 flow
        raise NotImplementedError(
            f"OAuth flow not yet implemented for provider {self.name}. "
            "Use api_key auth_type for MVP."
        )


class ProviderRegistry:
    """Registry for managing provider instances."""

    def __init__(self) -> None:
        """Initialize empty provider registry."""
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        """
        Register a provider.

        Args:
            provider: Provider instance to register
        """
        self._providers[provider.name] = provider

    def unregister(self, name: str) -> None:
        """
        Unregister a provider.

        Args:
            name: Provider name to unregister
        """
        self._providers.pop(name, None)

    def get(self, name: str) -> Provider | None:
        """
        Get provider by name.

        Args:
            name: Provider name

        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(name)

    def get_all(self) -> list[Provider]:
        """
        Get all registered providers.

        Returns:
            List of all providers
        """
        return list(self._providers.values())

    def get_healthy(self) -> list[Provider]:
        """
        Get all healthy providers.

        Note: Health tracking will be implemented in Phase 3.
        For now, returns all providers.

        Returns:
            List of healthy providers
        """
        # TODO: Implement health filtering in Phase 3
        return self.get_all()

    async def close_all(self) -> None:
        """Close all provider connections."""
        for provider in self._providers.values():
            await provider.close()


def create_provider(config: ProviderConfig) -> Provider:
    """
    Factory function to create provider from configuration.

    Args:
        config: Provider configuration

    Returns:
        Configured provider instance

    Raises:
        ValueError: If auth_type is invalid
    """
    if config.auth_type == "api_key":
        return APIKeyProvider(config)
    elif config.auth_type == "oauth":
        return OAuthProvider(config)
    else:
        raise ValueError(f"Unknown auth_type: {config.auth_type}")
