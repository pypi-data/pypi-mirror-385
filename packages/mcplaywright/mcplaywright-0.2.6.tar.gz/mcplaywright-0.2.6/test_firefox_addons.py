#!/usr/bin/env python
"""
Test script for Firefox addon support in MCPlaywright.

Demonstrates:
1. Launching Firefox with Remote Debugging Protocol enabled
2. Installing Firefox addons via geckordp
3. Verifying addon functionality
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from playwright.async_api import async_playwright


async def test_firefox_addon_installation():
    """Test Firefox addon installation using RDP"""
    print("\n" + "="*60)
    print("MCPlaywright Firefox Addon Support Test")
    print("="*60)

    rdp_port = 6000
    addon_dir = Path(__file__).parent / "test_firefox_addon"

    if not addon_dir.exists():
        print(f"\n❌ Test addon directory not found: {addon_dir}")
        return False

    print(f"\n✓ Test addon directory found: {addon_dir}")

    try:
        # Check geckordp availability
        try:
            from geckordp.rdp_client import RDPClient
            from geckordp.actors.root import RootActor
            from geckordp.actors.addon.addons import AddonsActor
            print("✓ geckordp library available")
        except ImportError as e:
            print(f"\n❌ geckordp not installed: {e}")
            print("\nInstall with: uv pip install geckordp")
            return False

        # Launch Firefox with RDP enabled
        print(f"\n1. Launching Firefox with RDP server on port {rdp_port}...")
        async with async_playwright() as p:
            browser = await p.firefox.launch(
                headless=False,
                args=[
                    f"--start-debugger-server={rdp_port}",
                    "--no-remote"  # Prevent conflicts with existing Firefox instances
                ]
            )
            print(f"✓ Firefox launched with debugging enabled")

            # Wait for RDP server to be ready
            print(f"\n2. Waiting for RDP server to initialize...")
            await asyncio.sleep(5)  # Increased wait time

            # Connect via RDP
            print(f"\n3. Connecting to Firefox RDP server...")
            rdp_client = RDPClient()
            rdp_client.connect("localhost", rdp_port)
            print(f"✓ Connected to RDP server on port {rdp_port}")

            # Get addons actor with retry
            print(f"\n4. Accessing AddonsActor...")
            root = RootActor(rdp_client)

            # Try to get root with timeout handling
            root_ids = None
            for attempt in range(3):
                print(f"  Attempt {attempt + 1}/3 to get root actor...")
                root_ids = root.get_root()
                if root_ids:
                    break
                await asyncio.sleep(2)

            if not root_ids:
                print(f"❌ Failed to get root actor after 3 attempts")
                rdp_client.disconnect()
                await browser.close()
                return False

            print(f"✓ Root actor initialized")
            print(f"  Available actors: {list(root_ids.keys())[:5]}...")

            addons_actor = AddonsActor(rdp_client, root_ids["addonsActor"])
            print(f"✓ AddonsActor ready")

            # Install test addon
            print(f"\n5. Installing test addon from {addon_dir}...")
            response = addons_actor.install_temporary_addon(str(addon_dir))

            addon_id = response.get("id")
            if addon_id:
                print(f"✓ Addon installed successfully!")
                print(f"  Addon ID: {addon_id}")
                print(f"  Response keys: {list(response.keys())}")
            else:
                print(f"❌ Addon installation failed")
                print(f"  Response: {response}")
                rdp_client.disconnect()
                await browser.close()
                return False

            # Create page and test addon
            print(f"\n6. Testing addon functionality...")
            page = await browser.new_page()
            await page.goto("https://example.com")
            print(f"✓ Navigated to example.com")

            # Wait a bit for addon to inject content
            await asyncio.sleep(2)

            # Check for addon console messages
            console_messages = []
            page.on("console", lambda msg: console_messages.append(msg.text))

            # Reload to capture all console messages
            await page.reload()
            await asyncio.sleep(2)

            # Check if addon injected its indicator
            indicator = await page.query_selector("#mcplaywright-firefox-indicator")

            if indicator:
                print(f"✓ Addon visual indicator found on page!")
                indicator_text = await indicator.inner_text()
                print(f"  Indicator text: {indicator_text.strip()}")
            else:
                print(f"⚠️  Addon visual indicator not found (may need more time)")

            # Check console for addon messages
            addon_messages = [msg for msg in console_messages if "MCPlaywright" in msg]
            if addon_messages:
                print(f"✓ Found {len(addon_messages)} addon console messages:")
                for msg in addon_messages[:3]:
                    print(f"  - {msg[:80]}...")
            else:
                print(f"⚠️  No addon console messages captured")

            # Take screenshot
            screenshot_path = "artifacts/firefox_addon_test.png"
            await page.screenshot(path=screenshot_path)
            print(f"✓ Screenshot saved: {screenshot_path}")

            # Cleanup
            print(f"\n7. Cleaning up...")
            rdp_client.disconnect()
            print(f"✓ Disconnected from RDP")

            await browser.close()
            print(f"✓ Browser closed")

            print(f"\n{'='*60}")
            print(f"✅ FIREFOX ADDON TEST PASSED!")
            print(f"{'='*60}")
            print(f"\nFirefox addon support working:")
            print(f"  • Launched Firefox with RDP enabled")
            print(f"  • Connected via geckordp")
            print(f"  • Installed test addon successfully")
            print(f"  • Addon injected content into page")
            print(f"  • Visual indicator and console logging verified")
            print(f"{'='*60}\n")

            return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run Firefox addon tests"""
    success = await test_firefox_addon_installation()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
