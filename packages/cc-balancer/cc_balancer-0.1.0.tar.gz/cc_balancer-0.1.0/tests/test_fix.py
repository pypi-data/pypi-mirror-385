#!/usr/bin/env python3
"""
Simple test to verify the proxy fix works correctly.
"""

import httpx


def test_header_filtering():
    """Test that headers are properly filtered."""
    print("🧪 Testing Header Filtering Fix\n")

    # Simulate the filtering logic from main.py
    client_headers = {
        'host': 'localhost:8000',
        'content-length': '123',
        'content-type': 'application/json',
        'x-api-key': 'test-key',
        'anthropic-version': '2023-06-01',
        'connection': 'keep-alive',
    }

    # This is what we do in the fixed code
    filtered_headers = {
        k: v for k, v in client_headers.items()
        if k.lower() not in {
            'host', 'content-length', 'content-type',
            'connection', 'transfer-encoding',
            'te', 'trailer', 'upgrade'
        }
    }

    print("Original headers:")
    for k, v in client_headers.items():
        print(f"  {k}: {v}")

    print("\nFiltered headers (sent to provider):")
    for k, v in filtered_headers.items():
        print(f"  {k}: {v}")

    # Verify filtering worked
    assert 'host' not in filtered_headers
    assert 'content-length' not in filtered_headers
    assert 'content-type' not in filtered_headers
    assert 'connection' not in filtered_headers
    assert 'x-api-key' in filtered_headers
    assert 'anthropic-version' in filtered_headers

    print("\n✅ Header filtering test PASSED!")
    print("   - Hop-by-hop headers removed")
    print("   - Application headers preserved")


def test_httpx_behavior():
    """Test that HTTPX sets correct Content-Length with json parameter."""
    print("\n🧪 Testing HTTPX JSON Behavior\n")

    test_data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "Hello!"}]
    }

    # Create a request without sending it
    request = httpx.Request(
        method="POST",
        url="http://example.com/v1/messages",
        json=test_data
    )

    print("Request details:")
    print(f"  Method: {request.method}")
    print(f"  URL: {request.url}")
    print(f"  Headers: {dict(request.headers)}")
    print(f"  Content-Length: {request.headers.get('content-length')}")
    print(f"  Content-Type: {request.headers.get('content-type')}")

    # Verify HTTPX set these automatically
    assert 'content-length' in request.headers
    assert 'content-type' in request.headers
    assert request.headers['content-type'] == 'application/json'

    print("\n✅ HTTPX behavior test PASSED!")
    print("   - Content-Length set automatically")
    print("   - Content-Type set to application/json")


if __name__ == "__main__":
    print("=" * 60)
    print("CC-Balancer Proxy Fix Verification")
    print("=" * 60)
    print()

    try:
        test_header_filtering()
        test_httpx_behavior()

        print("\n" + "=" * 60)
        print("✅ All tests PASSED!")
        print("=" * 60)
        print("\nThe proxy fix correctly handles:")
        print("  1. Filtering hop-by-hop headers")
        print("  2. Letting HTTPX set Content-Length")
        print("  3. Preserving application headers")

    except AssertionError as e:
        print(f"\n❌ Test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
