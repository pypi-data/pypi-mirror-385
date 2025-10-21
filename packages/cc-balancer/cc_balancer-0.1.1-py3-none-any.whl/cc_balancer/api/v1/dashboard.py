"""
Dashboard API endpoints for summary statistics and metrics.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from cc_balancer.core.metrics import metrics_collector

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


class DashboardSummary(BaseModel):
    """Dashboard summary statistics."""

    total_requests: int
    success_rate: float
    avg_latency_ms: float
    requests_per_minute: list[int]


class DashboardMetrics(BaseModel):
    """Detailed dashboard metrics."""

    requests_timeline: list[dict]
    provider_distribution: list[dict]
    latency_buckets: dict[str, float]


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary() -> DashboardSummary:
    """
    Get dashboard summary statistics.

    Returns:
        Summary statistics including request counts, success rate, latency
    """
    return DashboardSummary(
        total_requests=metrics_collector.total_requests,
        success_rate=metrics_collector.success_rate,
        avg_latency_ms=metrics_collector.avg_latency_ms,
        requests_per_minute=metrics_collector.get_requests_per_minute(60),
    )


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics() -> DashboardMetrics:
    """
    Get detailed dashboard metrics.

    Returns:
        Detailed metrics including timeline, distribution, and latency stats
    """
    return DashboardMetrics(
        requests_timeline=metrics_collector.get_requests_timeline(hours=24, interval_minutes=15),
        provider_distribution=metrics_collector.get_provider_stats(),
        latency_buckets=metrics_collector.get_latency_stats(),
    )
