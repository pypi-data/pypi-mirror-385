"""
Application state container.
"""

from pathlib import Path

from cc_balancer.config import AppConfig
from cc_balancer.providers import ProviderRegistry
from cc_balancer.router import RouterEngine


class AppState:
    """Application state container."""

    def __init__(self) -> None:
        self.config: AppConfig | None = None
        self.provider_registry: ProviderRegistry | None = None
        self.router: RouterEngine | None = None
        self.config_path: Path | None = None


# Global singleton instance
app_state = AppState()
