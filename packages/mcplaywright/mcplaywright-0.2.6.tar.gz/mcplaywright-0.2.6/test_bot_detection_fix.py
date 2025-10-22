#!/usr/bin/env python
"""
Test that MCPlaywright no longer triggers bot detection.

Tests the fix for custom user agent causing rendering issues on websites
that detect and block automation tools.
"""

import asyncio
import sys
sys.path.insert(0, 'src')


async def test_default_user_agent():
    """Test that default configuration uses standard user agent."""
    from mcplaywright.server_comprehensive import server

    print("=" * 70)
    print("Testing Bot Detection Fix")
    print("=" * 70)

    # Initialize browser
    print("\n📋 Initializing MCPlaywright browser...")
    await server.ensure_browser_context()

    page = await server.get_current_page()

    # Get actual user agent
    user_agent = await page.evaluate("navigator.userAgent")

    print(f"\n🌐 User Agent: {user_agent}\n")

    # Verify it's NOT the custom MCPlaywright user agent
    if "MCPlaywright" in user_agent:
        print("❌ FAIL: Custom 'MCPlaywright' user agent detected!")
        print("   This will trigger bot detection on many websites.")
        return False
    else:
        print("✅ PASS: Using standard Chrome-like user agent")
        print("   This should avoid bot detection issues.")

    # Test navigation to a common website
    test_urls = [
        "https://httpbin.org/user-agent",
        "https://example.com"
    ]

    print("\n📊 Testing navigation to common websites...")
    for url in test_urls:
        try:
            print(f"\n  • Navigating to {url}")
            await page.goto(url, wait_until="networkidle", timeout=10000)

            # Check for bot detection indicators
            content = await page.content()

            if "MCPlaywright" in content:
                print("    ⚠️  Page content shows 'MCPlaywright' - may trigger bot detection")
            else:
                print("    ✅ Page loaded successfully")

        except Exception as e:
            print(f"    ❌ Error: {e}")

    # Close browser
    await server.close_browser()

    print("\n" + "=" * 70)
    print("✅ Test Complete")
    print("=" * 70)

    return True


async def test_custom_user_agent():
    """Test that custom user agent can still be set if needed."""
    from mcplaywright.server_comprehensive import server

    print("\n" + "=" * 70)
    print("Testing Custom User Agent Configuration")
    print("=" * 70)

    print("\n📋 Configuring custom user agent...")
    result = await server.configure_browser(
        user_agent="MyCustomBot/1.0 (Testing)"
    )

    print(f"Configuration result: {result}")

    page = await server.get_current_page()
    user_agent = await page.evaluate("navigator.userAgent")

    print(f"\n🌐 User Agent: {user_agent}\n")

    if "MyCustomBot" in user_agent:
        print("✅ PASS: Custom user agent applied successfully")
    else:
        print("❌ FAIL: Custom user agent not applied")

    # Reset to default
    print("\n📋 Resetting to default user agent...")
    await server.configure_browser(user_agent="")

    page = await server.get_current_page()
    user_agent = await page.evaluate("navigator.userAgent")

    print(f"🌐 User Agent: {user_agent}\n")

    if "MyCustomBot" not in user_agent and "Chrome" in user_agent:
        print("✅ PASS: Reset to default user agent successfully")
    else:
        print("❌ FAIL: Failed to reset user agent")

    await server.close_browser()

    print("\n" + "=" * 70)
    print("✅ Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    print("\n🧪 MCPlaywright Bot Detection Fix Test Suite\n")

    # Test 1: Default user agent
    asyncio.run(test_default_user_agent())

    # Test 2: Custom user agent
    asyncio.run(test_custom_user_agent())

    print("\n🎉 All tests complete!\n")
