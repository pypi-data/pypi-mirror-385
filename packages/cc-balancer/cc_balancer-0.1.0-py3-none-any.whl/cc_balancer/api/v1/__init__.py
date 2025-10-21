"""
API v1 endpoints.
"""

from cc_balancer.api.v1.dashboard import router as dashboard_router
from cc_balancer.api.v1.providers import router as providers_router
from cc_balancer.api.v1.routing import router as routing_router
from cc_balancer.api.v1.monitoring import router as monitoring_router

__all__ = [
    "dashboard_router",
    "providers_router",
    "routing_router",
    "monitoring_router",
]
