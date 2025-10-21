#!/usr/bin/env python3
"""
Simple startup test for CC-Balancer.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cc_balancer.config_loader import load_config
from cc_balancer.providers import ProviderRegistry, create_provider
from cc_balancer.router import RoundRobinStrategy, RouterEngine


async def test_startup():
    """Test application startup sequence."""
    print("🚀 Testing CC-Balancer startup...")

    # Load configuration
    print("\n1. Loading configuration...")
    config = load_config("config.test.yaml")
    print(f"   ✓ Configuration loaded")
    print(f"   ✓ Server: {config.server.host}:{config.server.port}")
    print(f"   ✓ Routing strategy: {config.routing.strategy}")
    print(f"   ✓ Providers configured: {len(config.providers)}")

    # Initialize provider registry
    print("\n2. Initializing provider registry...")
    registry = ProviderRegistry()
    for provider_config in config.providers:
        provider = create_provider(provider_config)
        registry.register(provider)
        print(f"   ✓ Registered: {provider.name} ({provider_config.auth_type})")

    # Initialize routing engine
    print("\n3. Initializing routing engine...")
    if config.routing.strategy == "round-robin":
        strategy = RoundRobinStrategy()
    else:
        from cc_balancer.router import WeightedStrategy
        strategy = WeightedStrategy()
    router = RouterEngine(strategy)
    print(f"   ✓ Router initialized with {config.routing.strategy} strategy")

    # Test provider selection
    print("\n4. Testing provider selection...")
    providers = registry.get_all()
    for i in range(5):
        selected = router.select_provider(providers)
        print(f"   Request {i+1} → {selected.name}")

    # Cleanup
    print("\n5. Cleanup...")
    await registry.close_all()
    print("   ✓ All connections closed")

    print("\n✅ CC-Balancer startup test completed successfully!")
    print("\nReady to start server with: cc-balancer --config config.test.yaml")


if __name__ == "__main__":
    asyncio.run(test_startup())
