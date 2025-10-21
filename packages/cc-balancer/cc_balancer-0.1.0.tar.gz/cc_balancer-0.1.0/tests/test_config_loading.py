#!/usr/bin/env python3
"""
Test configuration loading with different config files.
"""

import subprocess
import time
import sys
import httpx


def test_config_file(config_file: str, expected_providers: list[str]):
    """Test that specific config file is loaded correctly."""
    print(f"\n📋 Testing: {config_file}")
    print("=" * 60)

    # Start server with specific config
    process = subprocess.Popen(
        ["cc-balancer", "--config", config_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)

        # Check health endpoint
        print("🔍 Checking health endpoint...")
        response = httpx.get("http://localhost:8000/healthz", timeout=5.0)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"📦 Providers: {data['providers']}")
            print(f"📝 Provider names: {data['provider_names']}")

            # Verify expected providers
            actual_names = set(data['provider_names'])
            expected_names = set(expected_providers)

            if actual_names == expected_names:
                print(f"✅ Correct providers loaded!")
                return True
            else:
                print(f"❌ Wrong providers!")
                print(f"   Expected: {expected_names}")
                print(f"   Got: {actual_names}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    finally:
        # Stop server
        print("🛑 Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        time.sleep(1)


if __name__ == "__main__":
    print("=" * 60)
    print("CC-Balancer Configuration Loading Test")
    print("=" * 60)

    tests = [
        ("config.test.yaml", ["tu-zi", "test-provider-2"]),
        ("config.mock.yaml", ["mock-provider-1", "mock-provider-2"]),
    ]

    results = []
    for config_file, expected_providers in tests:
        success = test_config_file(config_file, expected_providers)
        results.append((config_file, success))

    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)

    all_passed = True
    for config_file, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {config_file}")
        if not success:
            all_passed = False

    if all_passed:
        print("\n🎉 All configuration tests PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED")
        sys.exit(1)
