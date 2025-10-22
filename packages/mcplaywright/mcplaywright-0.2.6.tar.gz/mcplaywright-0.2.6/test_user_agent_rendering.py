#!/usr/bin/env python
"""
Test rendering differences between custom and standard user agents.
Reproduces the UPC LLC rendering bug caused by bot detection.
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from playwright.async_api import async_playwright


async def test_rendering_with_different_user_agents():
    """Test the same page with MCPlaywright user agent vs standard Chrome user agent."""

    test_url = "https://www.t-upc.llc/product/647"

    async with async_playwright() as p:
        print("=" * 70)
        print("Testing User Agent Impact on Page Rendering")
        print("=" * 70)

        # Test 1: MCPlaywright user agent (current behavior)
        print("\n🤖 Test 1: MCPlaywright custom user agent (bot detection)")
        print("-" * 70)

        browser1 = await p.chromium.launch(headless=False)
        context1 = await browser1.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="MCPlaywright/1.0 (FastMCP)"  # Custom bot UA
        )
        page1 = await context1.new_page()

        print(f"User Agent: MCPlaywright/1.0 (FastMCP)")
        await page1.goto(test_url, wait_until="networkidle")
        await page1.wait_for_timeout(2000)

        # Check for layout issues
        product_image = await page1.query_selector(".product-image, img[alt*='Angle'], .main-image")
        if product_image:
            is_visible = await product_image.is_visible()
            print(f"Product image visible: {is_visible}")
        else:
            print("Product image NOT FOUND (layout broken)")

        print("\nPress Enter to continue...")
        input()

        await browser1.close()

        # Test 2: Standard Chrome user agent
        print("\n🌐 Test 2: Standard Chrome user agent (normal user)")
        print("-" * 70)

        browser2 = await p.chromium.launch(headless=False)
        context2 = await browser2.new_context(
            viewport={"width": 1280, "height": 720}
            # No custom user_agent - uses standard Chrome UA
        )
        page2 = await context2.new_page()

        user_agent = await page2.evaluate("navigator.userAgent")
        print(f"User Agent: {user_agent[:80]}...")
        await page2.goto(test_url, wait_until="networkidle")
        await page2.wait_for_timeout(2000)

        # Check for layout issues
        product_image = await page2.query_selector(".product-image, img[alt*='Angle'], .main-image")
        if product_image:
            is_visible = await product_image.is_visible()
            print(f"Product image visible: {is_visible}")
        else:
            print("Product image NOT FOUND")

        print("\nPress Enter to close...")
        input()

        await browser2.close()

        print("\n" + "=" * 70)
        print("✅ Test Complete")
        print("=" * 70)
        print("\nConclusion:")
        print("If Test 1 shows broken layout and Test 2 works correctly,")
        print("the issue is BOT DETECTION via custom user agent.")
        print("\nSolution: Use standard user agent instead of 'MCPlaywright/1.0'")


if __name__ == "__main__":
    asyncio.run(test_rendering_with_different_user_agents())
