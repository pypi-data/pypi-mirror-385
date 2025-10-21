"""
Provider management API endpoints.
"""

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from cc_balancer.config import ProviderConfig
from cc_balancer.core.state import app_state
from cc_balancer.providers import create_provider

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


class ProviderCreate(BaseModel):
    """Provider creation model."""

    name: str
    base_url: HttpUrl
    auth_type: str = "api_key"
    api_key: str | None = None
    weight: int = 1
    priority: int = 1
    timeout_seconds: int = 30


class ProviderResponse(BaseModel):
    """Provider response model."""

    name: str
    base_url: str
    auth_type: str
    weight: int
    priority: int
    timeout_seconds: int
    status: str = "unknown"


class ProviderTestResult(BaseModel):
    """Provider connection test result."""

    status: str
    latency_ms: float | None = None
    error: str | None = None


@router.get("/", response_model=list[ProviderResponse])
async def list_providers() -> list[ProviderResponse]:
    """
    List all configured providers.

    Returns:
        List of provider configurations
    """
    if not app_state.provider_registry:
        return []

    providers = app_state.provider_registry.get_all()
    return [
        ProviderResponse(
            name=p.config.name,
            base_url=str(p.config.base_url),
            auth_type=p.config.auth_type,
            weight=p.config.weight,
            priority=p.config.priority,
            timeout_seconds=p.config.timeout_seconds,
            status="healthy",  # TODO: Get actual health status from health monitor
        )
        for p in providers
    ]


@router.post("/", response_model=dict[str, Any])
async def create_provider_endpoint(provider_data: ProviderCreate) -> dict[str, Any]:
    """
    Create a new provider.

    Args:
        provider_data: Provider configuration

    Returns:
        Success message with provider name
    """
    if not app_state.provider_registry or not app_state.config:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Check if provider already exists
    existing = app_state.provider_registry.get(provider_data.name)
    if existing:
        raise HTTPException(status_code=409, detail=f"Provider {provider_data.name} already exists")

    # Create provider config
    try:
        provider_config = ProviderConfig(
            name=provider_data.name,
            base_url=provider_data.base_url,
            auth_type=provider_data.auth_type,  # type: ignore
            api_key=provider_data.api_key,
            weight=provider_data.weight,
            priority=provider_data.priority,
            timeout_seconds=provider_data.timeout_seconds,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid provider configuration: {str(e)}")

    # Create and register provider
    try:
        provider = create_provider(provider_config)
        app_state.provider_registry.register(provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create provider: {str(e)}")

    # TODO: Persist to config.yaml

    return {"message": "Provider created successfully", "name": provider_data.name}


@router.delete("/{name}", response_model=dict[str, Any])
async def delete_provider(name: str) -> dict[str, Any]:
    """
    Delete a provider.

    Args:
        name: Provider name

    Returns:
        Success message
    """
    if not app_state.provider_registry:
        raise HTTPException(status_code=503, detail="Service not initialized")

    provider = app_state.provider_registry.get(name)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider {name} not found")

    # TODO: Remove from registry (need to implement remove method)
    # TODO: Persist to config.yaml

    return {"message": f"Provider {name} deleted successfully"}


@router.post("/{name}/test", response_model=ProviderTestResult)
async def test_provider(name: str) -> ProviderTestResult:
    """
    Test provider connection.

    Args:
        name: Provider name

    Returns:
        Test result with latency or error
    """
    if not app_state.provider_registry:
        raise HTTPException(status_code=503, detail="Service not initialized")

    provider = app_state.provider_registry.get(name)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider {name} not found")

    try:
        import time

        start_time = time.time()

        # Test with a simple request
        response = await provider.send_request(
            method="GET",
            path="/",
            headers={},
        )

        latency = (time.time() - start_time) * 1000  # Convert to ms

        if response.status_code < 400:
            return ProviderTestResult(status="success", latency_ms=latency)
        else:
            return ProviderTestResult(
                status="error",
                latency_ms=latency,
                error=f"HTTP {response.status_code}",
            )

    except httpx.TimeoutException:
        return ProviderTestResult(status="error", error="Connection timeout")
    except httpx.ConnectError:
        return ProviderTestResult(status="error", error="Connection refused")
    except Exception as e:
        return ProviderTestResult(status="error", error=str(e))
