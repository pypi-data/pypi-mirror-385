"""
Tests for routing strategies.
"""

import pytest

from cc_balancer.config import ProviderConfig
from cc_balancer.providers import APIKeyProvider
from cc_balancer.router import (
    RoundRobinStrategy,
    RouterEngine,
    WeightedStrategy,
)


@pytest.fixture
def test_providers():
    """Create test providers."""
    configs = [
        ProviderConfig(
            name=f"provider-{i}",
            base_url=f"https://api{i}.example.com",
            auth_type="api_key",
            api_key=f"key-{i}",
            weight=i + 1,
        )
        for i in range(3)
    ]
    return [APIKeyProvider(config) for config in configs]


def test_round_robin_selection(test_providers):
    """Test round-robin provider selection."""
    strategy = RoundRobinStrategy()
    router = RouterEngine(strategy)

    # Should cycle through providers
    assert router.select_provider(test_providers).name == "provider-0"
    assert router.select_provider(test_providers).name == "provider-1"
    assert router.select_provider(test_providers).name == "provider-2"
    assert router.select_provider(test_providers).name == "provider-0"


def test_round_robin_reset(test_providers):
    """Test round-robin strategy reset."""
    strategy = RoundRobinStrategy()
    router = RouterEngine(strategy)

    router.select_provider(test_providers)
    router.select_provider(test_providers)

    router.reset()
    assert router.select_provider(test_providers).name == "provider-0"


def test_weighted_selection(test_providers):
    """Test weighted provider selection."""
    strategy = WeightedStrategy()
    router = RouterEngine(strategy)

    # Collect selections
    selections = []
    for _ in range(6):  # Sum of weights: 1+2+3=6
        provider = router.select_provider(test_providers)
        selections.append(provider.name)

    # Count occurrences
    counts = {name: selections.count(name) for name in set(selections)}

    # Should respect weights: 1:2:3 ratio
    assert counts["provider-0"] == 1
    assert counts["provider-1"] == 2
    assert counts["provider-2"] == 3


def test_no_providers_error():
    """Test that empty provider list raises error."""
    strategy = RoundRobinStrategy()
    router = RouterEngine(strategy)

    with pytest.raises(ValueError, match="No providers available"):
        router.select_provider([])
