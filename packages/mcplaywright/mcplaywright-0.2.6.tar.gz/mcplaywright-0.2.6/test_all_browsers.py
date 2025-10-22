#!/usr/bin/env python
"""
Test script to verify all three browsers work with MCPlaywright.
Tests: Chromium, Firefox, WebKit
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcplaywright.session_manager import get_session_manager


async def test_browser(browser_type: str) -> bool:
    """Test a specific browser type"""
    print(f"\n{'='*60}")
    print(f"Testing {browser_type.upper()}")
    print('='*60)

    try:
        # Create session with specific browser
        session_manager = get_session_manager()
        context = await session_manager.get_or_create_session(None)

        # Configure browser type
        from mcplaywright.context import BrowserType
        browser_enum = getattr(BrowserType, browser_type.upper())
        context.config.browser_type = browser_enum

        print(f"✓ Session created: {context.session_id}")

        # Get page and navigate
        page = await context.get_current_page()
        print(f"✓ Browser launched: {browser_type}")
        print(f"  Executable: {context._browser.version if hasattr(context._browser, 'version') else 'N/A'}")

        # Navigate to test page
        await page.goto("https://httpbin.org/html")
        print(f"✓ Navigation successful")

        # Get page info
        title = await page.title()
        url = page.url
        print(f"  Title: {title}")
        print(f"  URL: {url}")

        # Test basic interaction - get page content
        content = await page.content()
        has_content = len(content) > 100
        print(f"✓ Page content loaded: {len(content)} characters")

        # Test console capture
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg.text))

        await page.evaluate("console.log('Test from', navigator.userAgent)")
        await asyncio.sleep(0.5)

        if console_messages:
            print(f"✓ Console capture working: {len(console_messages)} messages")

        # Take screenshot
        screenshot_path = f"artifacts/test_{browser_type}.png"
        await page.screenshot(path=screenshot_path)

        if Path(screenshot_path).exists():
            size = Path(screenshot_path).stat().st_size
            print(f"✓ Screenshot saved: {screenshot_path} ({size} bytes)")

        # Cleanup
        await context.cleanup()
        print(f"\n✅ {browser_type.upper()} TEST PASSED")

        return True

    except Exception as e:
        print(f"\n❌ {browser_type.upper()} TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Test all three browsers"""
    print("\n" + "="*60)
    print("MCPlaywright Multi-Browser Compatibility Test")
    print("="*60)

    browsers = ["chromium", "firefox", "webkit"]
    results = {}

    for browser in browsers:
        results[browser] = await test_browser(browser)
        # Small delay between tests
        await asyncio.sleep(1)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for browser, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{browser.upper():10s}: {status}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL BROWSERS WORKING!")
        print("="*60)
        print("\nMCPlaywright successfully supports:")
        print("  • Chromium (Chrome/Edge)")
        print("  • Firefox (Gecko)")
        print("  • WebKit (Safari)")
        print("\nYou can switch browsers using:")
        print("  await configure_browser({'browser_type': 'firefox'})")
    else:
        print("⚠️  SOME BROWSERS FAILED")
        print("="*60)
        failed = [b for b, p in results.items() if not p]
        print(f"\nFailed browsers: {', '.join(failed)}")
        print("\nInstall missing browsers with:")
        print("  playwright install")

    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
