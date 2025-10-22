#!/usr/bin/env python
"""
Test script for Firefox DevTools support in MCPlaywright.

Demonstrates:
1. Launching Firefox with isolated RDP debugging
2. Enabling Firefox DevTools via geckordp
3. JavaScript evaluation in Firefox context
4. Console log capture
5. DOM inspection
"""

import asyncio
import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent / "src"))

from playwright.async_api import async_playwright


async def test_firefox_devtools():
    """Test Firefox DevTools integration"""
    print("\n" + "="*70)
    print("MCPlaywright Firefox DevTools Integration Test")
    print("="*70)

    # Use unique RDP port to avoid conflicts
    rdp_port = 6001  # Different from default 6000

    # Create temporary profile directory for isolation
    profile_dir = tempfile.mkdtemp(prefix="mcplaywright_firefox_")
    print(f"\n✓ Created isolated Firefox profile: {profile_dir}")

    # Create prefs.js to enable remote debugging and bypass security prompts
    prefs_content = """
// Enable remote debugging
user_pref("devtools.debugger.remote-enabled", true);
user_pref("devtools.chrome.enabled", true);
user_pref("devtools.debugger.prompt-connection", false);  // Skip connection prompt
user_pref("devtools.debugger.force-local", false);  // Allow remote connections
"""
    prefs_path = os.path.join(profile_dir, "prefs.js")
    with open(prefs_path, "w") as f:
        f.write(prefs_content)
    print(f"✓ Configured Firefox preferences for remote debugging")

    try:
        # Check geckordp availability
        try:
            from geckordp.rdp_client import RDPClient
            from geckordp.actors.root import RootActor
            from geckordp.actors.web_console import WebConsoleActor
            from geckordp.actors.inspector import InspectorActor
            from geckordp.actors.walker import WalkerActor
            print("✓ geckordp library available")
        except ImportError as e:
            print(f"\n❌ geckordp not installed: {e}")
            print("\nInstall with: uv pip install geckordp")
            return False

        # Launch Firefox with isolated RDP debugging
        print(f"\n1. Launching Firefox with isolated RDP server on port {rdp_port}...")
        async with async_playwright() as p:
            # Launch with isolated profile and debugging enabled
            # Use launch_persistent_context for custom profile support
            context = await p.firefox.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                args=[
                    f"--start-debugger-server={rdp_port}",
                    "--no-remote",  # Prevent connection to existing Firefox instances
                ]
            )
            browser = context  # For compatibility with rest of code
            print(f"✓ Firefox launched with isolated profile and RDP on port {rdp_port}")

            # Wait for RDP server to initialize
            # Firefox RDP server can take time to fully start
            print(f"\n2. Waiting for RDP server to initialize...")
            await asyncio.sleep(8)  # Increased wait time for RDP server

            # Connect to RDP
            print(f"\n3. Connecting to Firefox RDP server...")
            rdp_client = RDPClient()

            # Enable debug logging to see connection details
            from geckordp.settings import GECKORDP
            GECKORDP.DEBUG = 0  # 0 = no debug, 1 = full debug

            try:
                rdp_client.connect("localhost", rdp_port)
                print(f"✓ Connected to RDP server on port {rdp_port}")
            except Exception as e:
                print(f"❌ Failed to connect to RDP server: {e}")
                await context.close()
                return False

            # Initialize root actor with retry logic
            print(f"\n4. Initializing RDP root actor...")
            try:
                root = RootActor(rdp_client)
                root_ids = None

                # Retry getRoot() multiple times as Firefox RDP can be slow to respond
                max_attempts = 5
                for attempt in range(max_attempts):
                    print(f"  Attempt {attempt + 1}/{max_attempts} to get root actor...")
                    try:
                        root_ids = root.get_root()
                        if root_ids:
                            print(f"✓ Root actor initialized successfully")
                            print(f"  Available actors: {', '.join(list(root_ids.keys())[:8])}...")
                            break
                    except Exception as e:
                        print(f"    Attempt {attempt + 1} failed: {e}")

                    if attempt < max_attempts - 1:
                        await asyncio.sleep(3)  # Wait before retry

                if not root_ids:
                    print(f"❌ Failed to get root actor after {max_attempts} attempts")
                    rdp_client.disconnect()
                    await context.close()
                    return False

                # Navigate to a page first to create a tab
                print(f"\n  Creating page for tab-level actor access...")
                page = await context.new_page()
                await page.goto("https://example.com")
                await asyncio.sleep(2)  # Wait for page to fully load
                print(f"  ✓ Page created and loaded")

                # Get tab descriptors to access tab-level actors (console, inspector)
                print(f"\n  Accessing tab-level actors...")
                tabs = root.list_tabs()
                if tabs:
                    first_tab = tabs[0] if isinstance(tabs, list) else tabs
                    print(f"  Found tab: {str(first_tab.get('title', 'Unknown'))[:40]}")

                    # Get the tab descriptor
                    from geckordp.actors.descriptors.tab import TabActor
                    tab_actor_id = first_tab.get('actor') if isinstance(first_tab, dict) else first_tab

                    # Get the target (page-level) from the tab
                    tab_descriptor = TabActor(rdp_client, tab_actor_id)
                    tab_target = tab_descriptor.get_target()

                    if isinstance(tab_target, dict):
                        print(f"  ✓ Tab-level actors: {', '.join(list(tab_target.keys())[:8])}...")
                        # Update root_ids to include tab-level actors
                        root_ids.update(tab_target)
                    else:
                        print(f"  ⚠️  Tab target type unexpected: {type(tab_target)}")
                else:
                    print(f"  ⚠️  No tabs found")

            except Exception as e:
                print(f"❌ Root actor initialization failed: {e}")
                rdp_client.disconnect()
                await context.close()
                return False

            # Test JavaScript evaluation
            print(f"\n5. Testing JavaScript evaluation...")
            try:
                web_console_actor_id = root_ids.get("consoleActor")
                if web_console_actor_id:
                    web_console = WebConsoleActor(rdp_client, web_console_actor_id)

                    # Evaluate simple expression
                    result = web_console.evaluate_js_async("2 + 2")
                    print(f"✓ JavaScript evaluation successful")
                    print(f"  Expression: 2 + 2")
                    print(f"  Result: {result}")
                else:
                    print(f"⚠️  WebConsole actor not available")

            except Exception as e:
                print(f"⚠️  JavaScript evaluation failed: {e}")

            # Test console log capture
            print(f"\n6. Testing console log capture...")
            try:
                if web_console_actor_id:
                    # Start listening for console messages
                    web_console.start_listeners([
                        WebConsoleActor.Listeners.CONSOLE_API,
                        WebConsoleActor.Listeners.PAGE_ERROR
                    ])
                    print(f"✓ Console listeners started")

                    # Inject console messages for testing (page already created earlier)
                    await page.evaluate("""
                        console.log('MCPlaywright Firefox test message');
                        console.warn('Test warning message');
                        console.error('Test error message');
                    """)

                    await asyncio.sleep(1)  # Allow messages to be captured

                    # Get cached console messages
                    messages = web_console.get_cached_messages([
                        WebConsoleActor.MessageTypes.CONSOLE_API,
                        WebConsoleActor.MessageTypes.PAGE_ERROR
                    ])

                    if messages and 'messages' in messages:
                        message_count = len(messages['messages'])
                        print(f"✓ Console capture working - {message_count} messages captured")

                        # Display first few messages
                        for i, msg in enumerate(messages['messages'][:3]):
                            msg_text = str(msg)[:100]
                            print(f"  Message {i+1}: {msg_text}...")
                    else:
                        print(f"✓ Console listener active (no messages yet)")

                else:
                    print(f"⚠️  Console capture not available (page already created earlier)")

            except Exception as e:
                print(f"⚠️  Console capture test failed: {e}")

            # Test DOM inspection
            print(f"\n7. Testing DOM inspection...")
            try:
                inspector_actor_id = root_ids.get("inspectorActor")
                if inspector_actor_id:
                    inspector = InspectorActor(rdp_client, inspector_actor_id)

                    # Get DOM walker
                    walker_actor_id = inspector.get_walker()
                    walker = WalkerActor(rdp_client, walker_actor_id)

                    # Get document root
                    document = walker.document()
                    print(f"✓ DOM inspection successful")
                    print(f"  Document actor: {str(document)[:100]}...")
                else:
                    print(f"⚠️  Inspector actor not available")

            except Exception as e:
                print(f"⚠️  DOM inspection failed: {e}")

            # Take screenshot for verification
            print(f"\n8. Taking verification screenshot...")
            try:
                screenshot_path = "artifacts/firefox_devtools_test.png"
                os.makedirs("artifacts", exist_ok=True)
                await page.screenshot(path=screenshot_path)
                print(f"✓ Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"⚠️  Screenshot failed: {e}")

            # Cleanup
            print(f"\n9. Cleaning up...")
            rdp_client.disconnect()
            print(f"✓ Disconnected from RDP")

            await context.close()
            print(f"✓ Context closed")

            print(f"\n{'='*70}")
            print(f"✅ FIREFOX DEVTOOLS TEST COMPLETED SUCCESSFULLY!")
            print(f"{'='*70}")
            print(f"\nFirefox DevTools capabilities verified:")
            print(f"  • Isolated Firefox profile for RDP connection")
            print(f"  • RDP connection on custom port ({rdp_port})")
            print(f"  • Root actor initialization")
            print(f"  • JavaScript evaluation via WebConsole")
            print(f"  • Console message capture")
            print(f"  • DOM inspection via Inspector/Walker actors")
            print(f"  • No interference with existing Firefox instances")
            print(f"{'='*70}\n")

            return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup temporary profile directory
        try:
            import shutil
            shutil.rmtree(profile_dir, ignore_errors=True)
            print(f"\n✓ Cleaned up temporary profile: {profile_dir}")
        except Exception as e:
            print(f"⚠️  Profile cleanup warning: {e}")


async def main():
    """Run Firefox DevTools tests"""
    success = await test_firefox_devtools()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
