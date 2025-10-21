#!/usr/bin/env python
"""
Simplified test script using standalone functions with proper session management.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcplaywright.session_manager import get_session_manager
from mcplaywright.tools.requests import (
    browser_start_request_monitoring,
    browser_get_requests,
    browser_export_requests,
    StartMonitoringParams,
    GetRequestsParams,
    ExportRequestsParams,
)
from mcplaywright.tools.tabs import (
    browser_new_tab,
    browser_list_tabs,
    browser_switch_tab,
    browser_close_tab,
    NewTabParams,
    TabListParams,
    SwitchTabParams,
    CloseTabParams
)
from mcplaywright.modules.navigation import BrowserNavigation
from mcplaywright.modules.browser import BrowserCore


async def test_http_monitoring():
    """Test HTTP request monitoring with proper session management"""
    print("\n" + "="*60)
    print("TEST 1: HTTP Request Monitoring")
    print("="*60)

    try:
        # Create session
        session_manager = get_session_manager()
        context = await session_manager.get_or_create_session(None)
        session_id = context.session_id

        print(f"\n✓ Created session: {session_id}")

        # Navigate to httpbin using the context
        print("\n1. Navigating to httpbin.org...")
        page = await context.get_current_page()
        await page.goto("https://httpbin.org")
        print(f"   ✓ Navigated to: {page.url}")
        print(f"   ✓ Page title: {await page.title()}")

        # Start request monitoring
        print("\n2. Starting HTTP request monitoring...")
        monitor_start = await browser_start_request_monitoring(
            StartMonitoringParams(session_id=session_id, capture_body=True)
        )
        print(f"   ✓ Monitoring started: {monitor_start['message']}")

        # Navigate to generate requests
        print("\n3. Navigating to /get to generate HTTP requests...")
        await page.goto("https://httpbin.org/get")

        # Small delay for requests to complete
        await asyncio.sleep(2)

        # Get captured requests
        print("\n4. Retrieving captured requests...")
        requests = await browser_get_requests(
            GetRequestsParams(session_id=session_id, format="summary", limit=10)
        )

        if requests['success']:
            print(f"   ✓ Total requests captured: {requests['total_captured']}")
            print(f"   ✓ Showing {requests['count']} requests:")

            for idx, req in enumerate(requests['requests'][:5], 1):
                print(f"      {idx}. {req['method']} {req['status']} - {req['url'][:50]}...")

            # Export to HAR
            print("\n5. Exporting to HAR format...")
            export_result = await browser_export_requests(
                ExportRequestsParams(session_id=session_id, format="har")
            )
            if export_result['success']:
                print(f"   ✓ HAR file saved: {export_result['export_path']}")
                print(f"   ✓ Exported {export_result['request_count']} requests")
        else:
            print(f"   ✗ Failed to get requests: {requests.get('error', 'Unknown error')}")
            return False

        print("\n✅ HTTP Monitoring Test PASSED!")

        # Cleanup
        await context.cleanup()
        return True

    except Exception as e:
        print(f"\n❌ HTTP Monitoring Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tab_management():
    """Test tab management features with proper session management"""
    print("\n" + "="*60)
    print("TEST 2: Tab Management")
    print("="*60)

    try:
        # Create session
        session_manager = get_session_manager()
        context = await session_manager.get_or_create_session(None)
        session_id = context.session_id

        print(f"\n✓ Created session: {session_id}")

        # Open new tab
        print("\n1. Opening new tab...")
        new_tab_result = await browser_new_tab(
            NewTabParams(session_id=session_id, url="https://httpbin.org/html")
        )

        if new_tab_result['success']:
            print(f"   ✓ New tab opened at index {new_tab_result['tab_index']}")
            print(f"   ✓ Total tabs: {new_tab_result['tab_count']}")
        else:
            print(f"   ✗ Failed to open new tab: {new_tab_result.get('error', 'Unknown error')}")
            return False

        # List all tabs
        print("\n2. Listing all tabs...")
        tabs_list = await browser_list_tabs(TabListParams(session_id=session_id))

        if tabs_list['success']:
            print(f"   ✓ Found {tabs_list['total_tabs']} tabs:")
            for tab in tabs_list['tabs']:
                marker = "→" if tab['is_current'] else " "
                print(f"     {marker} Tab {tab['index']}: {tab['url'][:50]}...")
        else:
            print(f"   ✗ Failed to list tabs: {tabs_list.get('error', 'Unknown error')}")
            return False

        # Switch to first tab
        if tabs_list['total_tabs'] > 1:
            print("\n3. Switching to tab 0...")
            switch_result = await browser_switch_tab(
                SwitchTabParams(session_id=session_id, tab_index=0)
            )
            if switch_result['success']:
                print(f"   ✓ Switched to: {switch_result['active_tab']['url'][:50]}...")
            else:
                print(f"   ✗ Failed to switch tab: {switch_result.get('error', 'Unknown error')}")
                return False

        # Close a tab
        print("\n4. Closing current tab...")
        close_result = await browser_close_tab(CloseTabParams(session_id=session_id))

        if close_result['success']:
            print(f"   ✓ Closed tab, {close_result['remaining_tabs']} tabs remaining")
        else:
            print(f"   ✗ Failed to close tab: {close_result.get('error', 'Unknown error')}")
            return False

        print("\n✅ Tab Management Test PASSED!")

        # Cleanup
        await context.cleanup()
        return True

    except Exception as e:
        print(f"\n❌ Tab Management Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MCPlaywright Standalone Features Test Suite")
    print("="*60)

    results = []

    # Test HTTP monitoring
    results.append(("HTTP Monitoring", await test_http_monitoring()))

    # Test tab management
    results.append(("Tab Management", await test_tab_management()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
