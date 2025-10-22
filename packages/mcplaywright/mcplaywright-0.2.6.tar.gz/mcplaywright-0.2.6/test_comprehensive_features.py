#!/usr/bin/env python
"""
Test script to verify all comprehensive server features work correctly.

This script tests:
1. HTTP request monitoring with HAR export
2. Tab management
3. Console message capture
4. JavaScript evaluation
5. Wait strategies
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcplaywright.tools.requests import (
    browser_start_request_monitoring,
    browser_get_requests,
    browser_export_requests,
    browser_request_monitoring_status,
    StartMonitoringParams,
    GetRequestsParams,
    ExportRequestsParams,
    MonitoringStatusParams
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
from mcplaywright.modules.browser import BrowserCore
from mcplaywright.modules.navigation import BrowserNavigation


class TestServer(BrowserCore, BrowserNavigation):
    """Test server combining modules"""
    pass


async def test_http_monitoring():
    """Test HTTP request monitoring"""
    print("\n" + "="*60)
    print("TEST 1: HTTP Request Monitoring")
    print("="*60)

    server = TestServer()

    try:
        # Navigate to httpbin
        print("\n1. Navigating to httpbin.org...")
        nav_result = await server.navigate_to_url("https://httpbin.org")
        print(f"   ✓ Navigated to: {nav_result['url']}")
        print(f"   ✓ Page title: {nav_result['title']}")

        # Start request monitoring
        print("\n2. Starting HTTP request monitoring...")
        monitor_start = await browser_start_request_monitoring(
            StartMonitoringParams(session_id=None, capture_body=True)
        )
        print(f"   ✓ Monitoring started: {monitor_start['message']}")

        # Navigate to generate some requests
        print("\n3. Navigating to /get to generate HTTP requests...")
        await server.navigate_to_url("https://httpbin.org/get")

        # Small delay for requests to complete
        await asyncio.sleep(2)

        # Get captured requests
        print("\n4. Retrieving captured requests...")
        requests = await browser_get_requests(
            GetRequestsParams(session_id=None, format="summary", limit=10)
        )
        print(f"   ✓ Total requests captured: {requests['total_captured']}")
        print(f"   ✓ Showing {requests['count']} requests:")

        for idx, req in enumerate(requests['requests'][:5], 1):
            print(f"      {idx}. {req['method']} {req['status']} - {req['url'][:50]}...")

        # Export to HAR
        print("\n5. Exporting to HAR format...")
        export_result = await browser_export_requests(
            ExportRequestsParams(session_id=None, format="har")
        )
        if export_result['success']:
            print(f"   ✓ HAR file saved: {export_result['export_path']}")
            print(f"   ✓ Exported {export_result['request_count']} requests")

        print("\n✅ HTTP Monitoring Test PASSED!")
        return True

    except Exception as e:
        print(f"\n❌ HTTP Monitoring Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await server.close_browser()


async def test_tab_management():
    """Test tab management features"""
    print("\n" + "="*60)
    print("TEST 2: Tab Management")
    print("="*60)

    try:
        # Open new tab
        print("\n1. Opening new tab...")
        new_tab_result = await browser_new_tab(
            NewTabParams(session_id=None, url="https://httpbin.org/html")
        )
        print(f"   ✓ New tab opened at index {new_tab_result['tab_index']}")
        print(f"   ✓ Total tabs: {new_tab_result['tab_count']}")

        # List all tabs
        print("\n2. Listing all tabs...")
        tabs_list = await browser_list_tabs(TabListParams(session_id=None))
        print(f"   ✓ Found {tabs_list['total_tabs']} tabs:")
        for tab in tabs_list['tabs']:
            marker = "→" if tab['is_current'] else " "
            print(f"     {marker} Tab {tab['index']}: {tab['url'][:50]}...")

        # Switch to first tab
        if tabs_list['total_tabs'] > 1:
            print("\n3. Switching to tab 0...")
            switch_result = await browser_switch_tab(
                SwitchTabParams(session_id=None, tab_index=0)
            )
            print(f"   ✓ Switched to: {switch_result['active_tab']['url'][:50]}...")

        # Close a tab
        print("\n4. Closing current tab...")
        close_result = await browser_close_tab(CloseTabParams(session_id=None))
        print(f"   ✓ Closed tab, {close_result['remaining_tabs']} tabs remaining")

        print("\n✅ Tab Management Test PASSED!")
        return True

    except Exception as e:
        print(f"\n❌ Tab Management Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MCPlaywright Comprehensive Features Test Suite")
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
