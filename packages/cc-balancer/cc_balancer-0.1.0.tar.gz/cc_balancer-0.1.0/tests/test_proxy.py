#!/usr/bin/env python3
"""
Test script to verify proxy endpoint with mock server.
"""

import asyncio
from aiohttp import web
import httpx
import signal
import sys


# Simple mock API server
async def mock_api_handler(request):
    """Mock API endpoint that returns a simple response."""
    body = await request.json()
    print(f"✓ Mock API received request: {body.get('messages', [{}])[0].get('content', 'N/A')}")

    return web.json_response({
        "id": "msg_test123",
        "type": "message",
        "role": "assistant",
        "content": [{
            "type": "text",
            "text": "Hello! This is a test response from the mock API."
        }],
        "model": "claude-3-5-sonnet-20241022",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 20}
    })


async def start_mock_server():
    """Start mock API server on port 9000."""
    app = web.Application()
    app.router.add_post('/v1/messages', mock_api_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 9000)
    await site.start()

    print("🚀 Mock API server started on http://localhost:9000")
    return runner


async def test_proxy():
    """Test the proxy endpoint."""
    print("\n📋 Testing CC-Balancer Proxy Endpoint\n")

    # Start mock server
    runner = await start_mock_server()

    try:
        # Wait a moment for server to be ready
        await asyncio.sleep(1)

        # Test proxy endpoint
        print("📤 Sending request to proxy...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/v1/messages",
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": "Hello from proxy test!"}]
                },
                timeout=30.0
            )

            print(f"📥 Response status: {response.status_code}")
            print(f"📄 Response body: {response.json()}")

            if response.status_code == 200:
                print("\n✅ Proxy test PASSED!")
            else:
                print(f"\n❌ Proxy test FAILED: Status {response.status_code}")
                print(f"   Error: {response.text}")

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")

    finally:
        # Cleanup
        await runner.cleanup()
        print("\n🧹 Mock server stopped")


if __name__ == "__main__":
    print("=" * 60)
    print("CC-Balancer Proxy Test")
    print("=" * 60)
    print("\n⚠️  Prerequisites:")
    print("   1. CC-Balancer server must be running on port 8000")
    print("   2. Update config to use http://localhost:9000 as provider")
    print("\n   Run: cc-balancer --config config.test.yaml")
    print("=" * 60)

    try:
        asyncio.run(test_proxy())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
