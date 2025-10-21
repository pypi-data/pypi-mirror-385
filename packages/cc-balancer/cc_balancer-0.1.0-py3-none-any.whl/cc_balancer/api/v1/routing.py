"""
Routing configuration API endpoints.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cc_balancer.core.state import app_state

router = APIRouter(prefix="/api/v1/routing", tags=["routing"])


class RoutingConfig(BaseModel):
    """Routing configuration model."""

    strategy: str
    failure_threshold: int
    recovery_interval_seconds: int
    cache_enabled: bool
    cache_ttl_seconds: int


@router.get("/config", response_model=RoutingConfig)
async def get_routing_config() -> RoutingConfig:
    """
    Get current routing configuration.

    Returns:
        Routing configuration
    """
    if not app_state.config:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return RoutingConfig(
        strategy=app_state.config.routing.strategy,
        failure_threshold=app_state.config.error_handling.failure_threshold,
        recovery_interval_seconds=app_state.config.error_handling.recovery_interval_seconds,
        cache_enabled=app_state.config.cache.enabled,
        cache_ttl_seconds=app_state.config.cache.ttl_seconds,
    )


@router.put("/config", response_model=dict[str, Any])
async def update_routing_config(config: RoutingConfig) -> dict[str, Any]:
    """
    Update routing configuration.

    Args:
        config: New routing configuration

    Returns:
        Success message
    """
    if not app_state.config or not app_state.router:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Update configuration (in-memory for now)
    app_state.config.routing.strategy = config.strategy
    app_state.config.error_handling.failure_threshold = config.failure_threshold
    app_state.config.error_handling.recovery_interval_seconds = config.recovery_interval_seconds
    app_state.config.cache.enabled = config.cache_enabled
    app_state.config.cache.ttl_seconds = config.cache_ttl_seconds

    # TODO: Switch router strategy if changed
    # TODO: Persist to config.yaml

    return {"message": "Routing configuration updated successfully"}
