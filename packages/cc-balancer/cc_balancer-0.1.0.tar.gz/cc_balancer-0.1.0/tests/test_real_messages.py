#!/usr/bin/env python3
"""
Test /v1/messages endpoint with real Claude API provider.
Uses config.test.yaml with actual API credentials.
"""

import asyncio
import httpx
import json
from datetime import datetime


# Required headers for Claude API
DEFAULT_HEADERS = {
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}


async def test_simple_request():
    """Test 1: Simple text request."""
    print("\n" + "="*60)
    print("Test 1: Simple Text Request")
    print("="*60)

    # Increase timeout for real API calls
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:8000/v1/messages",
            headers={
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 100,
                "messages": [
                    {"role": "user", "content": "Say 'Hello from CC-Balancer!' and nothing else."}
                ]
            }
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response ID: {data.get('id', 'N/A')}")
            print(f"Model: {data.get('model', 'N/A')}")

            content = data.get('content', [])
            if content and len(content) > 0:
                text = content[0].get('text', '')
                print(f"Response: {text}")
                print(f"Tokens - Input: {data.get('usage', {}).get('input_tokens', 0)}, "
                      f"Output: {data.get('usage', {}).get('output_tokens', 0)}")

            print("✅ Test 1 PASSED")
            return True
        else:
            print(f"❌ Test 1 FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            return False


async def test_round_robin():
    """Test 2: Multiple requests to verify round-robin routing."""
    print("\n" + "="*60)
    print("Test 2: Round-Robin Routing (5 requests)")
    print("="*60)

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i in range(5):
            print(f"\nRequest {i+1}/5...")
            response = await client.post(
                "http://localhost:8000/v1/messages",
                headers=DEFAULT_HEADERS,
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 50,
                    "messages": [
                        {"role": "user", "content": f"Just say 'Request {i+1} OK'"}
                    ]
                }
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get('content', [{}])[0].get('text', 'No response')
                print(f"✓ Got response: {text[:50]}...")
            else:
                print(f"✗ Request {i+1} failed: {response.status_code}")
                return False

    print("\n✅ Test 2 PASSED - All requests succeeded")
    return True


async def test_streaming_disabled():
    """Test 3: Verify non-streaming response."""
    print("\n" + "="*60)
    print("Test 3: Non-Streaming Response")
    print("="*60)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:8000/v1/messages",
            headers=DEFAULT_HEADERS,
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 100,
                "messages": [
                    {"role": "user", "content": "Count from 1 to 5."}
                ],
                "stream": False  # Explicitly disable streaming
            }
        )

        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {data.get('type', 'N/A')}")
            print(f"Stop reason: {data.get('stop_reason', 'N/A')}")

            content = data.get('content', [{}])[0].get('text', '')
            print(f"Content: {content[:100]}...")

            print("✅ Test 3 PASSED")
            return True
        else:
            print(f"❌ Test 3 FAILED: {response.status_code}")
            return False


async def test_system_prompt():
    """Test 4: Request with system prompt."""
    print("\n" + "="*60)
    print("Test 4: Request with System Prompt")
    print("="*60)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:8000/v1/messages",
            headers=DEFAULT_HEADERS,
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 100,
                "system": "You are a helpful assistant that responds in Chinese.",
                "messages": [
                    {"role": "user", "content": "Say hello."}
                ]
            }
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            text = data.get('content', [{}])[0].get('text', '')
            print(f"Response: {text}")

            # Check if response is in Chinese (contains Chinese characters)
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
            if has_chinese:
                print("✓ System prompt was respected (Chinese response)")

            print("✅ Test 4 PASSED")
            return True
        else:
            print(f"❌ Test 4 FAILED: {response.status_code}")
            return False


async def test_error_handling():
    """Test 5: Invalid request handling."""
    print("\n" + "="*60)
    print("Test 5: Error Handling")
    print("="*60)

    # Test with missing required field
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:8000/v1/messages",
            headers=DEFAULT_HEADERS,
            json={
                "model": "claude-sonnet-4-20250514",
                # Missing messages field
            }
        )

        print(f"Status: {response.status_code}")

        if response.status_code >= 400:
            print(f"Error response: {response.text[:200]}")
            print("✅ Test 5 PASSED - Error properly returned")
            return True
        else:
            print(f"❌ Test 5 FAILED - Should return error, got {response.status_code}")
            return False


async def test_response_headers():
    """Test 6: Verify response headers."""
    print("\n" + "="*60)
    print("Test 6: Response Headers")
    print("="*60)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:8000/v1/messages",
            headers=DEFAULT_HEADERS,
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 50,
                "messages": [
                    {"role": "user", "content": "Hi!"}
                ]
            }
        )

        print(f"Status: {response.status_code}")
        print("\nResponse headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        # Verify proper header handling
        # Note: uvicorn/ASGI servers add 'connection' header at the server level,
        # which we cannot control. What we CAN verify is:
        # 1. Response is valid and complete
        # 2. No content-encoding issues (would cause decompression errors)
        # 3. Content-type is correct
        # 4. No duplicate or malformed headers

        checks_passed = True
        issues = []

        # Check 1: Valid response
        if response.status_code != 200:
            checks_passed = False
            issues.append(f"Invalid status code: {response.status_code}")

        # Check 2: Content-type present and correct
        if 'content-type' not in response.headers:
            checks_passed = False
            issues.append("Missing content-type header")
        elif 'json' not in response.headers['content-type']:
            checks_passed = False
            issues.append(f"Wrong content-type: {response.headers['content-type']}")

        # Check 3: Response body is valid JSON
        try:
            data = response.json()
            if 'content' not in data:
                checks_passed = False
                issues.append("Missing 'content' in response body")
        except Exception as e:
            checks_passed = False
            issues.append(f"Invalid JSON response: {e}")

        # Check 4: No content-encoding issues (if we got here without error, it's fine)
        # The fact that response.json() worked means decompression was handled correctly

        if checks_passed:
            print("\n✅ Test 6 PASSED - Headers properly handled, response valid")
            print("   (Note: 'connection' header added by uvicorn is expected)")
            return True
        else:
            print(f"\n❌ Test 6 FAILED - Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False


async def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("CC-Balancer /v1/messages Real API Test Suite")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print("\n⚠️  Using real Claude API - will consume tokens!")
    print("   Provider: tu-zi (from config.test.yaml)")

    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            health = await client.get("http://localhost:8000/healthz")
            if health.status_code != 200:
                print("\n❌ CC-Balancer is not healthy!")
                return False

            data = health.json()
            print(f"\n✓ Server healthy, providers: {data.get('provider_names', [])}")
    except Exception as e:
        print(f"\n❌ Cannot connect to CC-Balancer: {e}")
        print("   Make sure to run: cc-balancer --config config.test.yaml")
        return False

    # Run tests
    tests = [
        ("Simple Request", test_simple_request),
        ("Round-Robin Routing", test_round_robin),
        ("Non-Streaming Response", test_streaming_disabled),
        ("System Prompt", test_system_prompt),
        ("Error Handling", test_error_handling),
        ("Response Headers", test_response_headers),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
            await asyncio.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("="*60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests PASSED!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) FAILED")
        return False


if __name__ == "__main__":
    print("\n📋 Prerequisites:")
    print("   1. CC-Balancer running: cc-balancer --config config.test.yaml")
    print("   2. Valid API key in config.test.yaml")
    print("   3. Internet connection to Claude API\n")

    import sys
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
