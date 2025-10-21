"""
Routing engine for provider selection with multiple strategies.
"""

from abc import ABC, abstractmethod
from typing import Protocol

from cc_balancer.config import ProviderConfig


class Provider(Protocol):
    """Protocol for provider interface."""

    config: ProviderConfig
    name: str


class RoutingStrategy(ABC):
    """Abstract base class for routing strategies."""

    @abstractmethod
    def select_provider(self, providers: list[Provider]) -> Provider:
        """
        Select next provider from available pool.

        Args:
            providers: List of available healthy providers

        Returns:
            Selected provider

        Raises:
            ValueError: If no providers available
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset strategy state."""
        pass


class RoundRobinStrategy(RoutingStrategy):
    """Round-robin provider selection strategy."""

    def __init__(self) -> None:
        self._current_index = 0

    def select_provider(self, providers: list[Provider]) -> Provider:
        """Select next provider in round-robin order."""
        if not providers:
            raise ValueError("No providers available for routing")

        provider = providers[self._current_index % len(providers)]
        self._current_index = (self._current_index + 1) % len(providers)
        return provider

    def reset(self) -> None:
        """Reset round-robin counter."""
        self._current_index = 0


class WeightedStrategy(RoutingStrategy):
    """Weighted provider selection strategy."""

    def __init__(self) -> None:
        self._current_index = 0
        self._weighted_pool: list[Provider] = []

    def select_provider(self, providers: list[Provider]) -> Provider:
        """Select provider based on weights."""
        if not providers:
            raise ValueError("No providers available for routing")

        # Rebuild weighted pool if providers changed
        if not self._weighted_pool or set(self._weighted_pool) != set(providers):
            self._build_weighted_pool(providers)

        provider = self._weighted_pool[self._current_index % len(self._weighted_pool)]
        self._current_index = (self._current_index + 1) % len(self._weighted_pool)
        return provider

    def _build_weighted_pool(self, providers: list[Provider]) -> None:
        """Build weighted pool with providers repeated by weight."""
        self._weighted_pool = []
        for provider in providers:
            weight = provider.config.weight
            self._weighted_pool.extend([provider] * weight)
        self._current_index = 0

    def reset(self) -> None:
        """Reset weighted strategy state."""
        self._current_index = 0
        self._weighted_pool = []


class RouterEngine:
    """Main routing engine for provider selection."""

    def __init__(self, strategy: RoutingStrategy) -> None:
        """
        Initialize router with strategy.

        Args:
            strategy: Routing strategy instance
        """
        self.strategy = strategy

    def select_provider(self, providers: list[Provider]) -> Provider:
        """
        Select next provider using configured strategy.

        Args:
            providers: List of available providers

        Returns:
            Selected provider

        Raises:
            ValueError: If no providers available
        """
        if not providers:
            raise ValueError("No providers available for routing")

        return self.strategy.select_provider(providers)

    def set_strategy(self, strategy: RoutingStrategy) -> None:
        """
        Change routing strategy.

        Args:
            strategy: New routing strategy
        """
        self.strategy = strategy

    def reset(self) -> None:
        """Reset router state."""
        self.strategy.reset()
