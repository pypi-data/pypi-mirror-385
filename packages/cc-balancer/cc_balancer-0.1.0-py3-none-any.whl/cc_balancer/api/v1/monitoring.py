"""
Monitoring and request history API endpoints.
"""

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from cc_balancer.core.metrics import metrics_collector

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


class LatencyStats(BaseModel):
    """Latency percentile statistics."""

    p50: float
    p95: float
    p99: float


class RequestHistoryResponse(BaseModel):
    """Request history response."""

    requests: list[dict[str, Any]]
    total: int


@router.get("/latency", response_model=LatencyStats)
async def get_latency_stats() -> LatencyStats:
    """
    Get latency percentile statistics.

    Returns:
        Latency stats (p50, p95, p99)
    """
    stats = metrics_collector.get_latency_stats()
    return LatencyStats(**stats)


@router.get("/requests", response_model=RequestHistoryResponse)
async def get_request_history(
    limit: int = Query(default=100, ge=1, le=1000, description="Number of requests to return")
) -> RequestHistoryResponse:
    """
    Get request history.

    Args:
        limit: Number of recent requests to return

    Returns:
        Request history with metadata
    """
    requests = metrics_collector.get_latest(limit=limit)
    return RequestHistoryResponse(
        requests=requests,
        total=metrics_collector.total_requests,
    )
