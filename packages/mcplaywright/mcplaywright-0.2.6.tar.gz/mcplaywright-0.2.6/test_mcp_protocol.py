#!/usr/bin/env python
"""
Test MCP protocol communication directly to diagnose parameter issues.
"""

import asyncio
import json
import sys

sys.path.insert(0, 'src')

from mcplaywright.server import app


async def test_mcp_calls():
    """Simulate MCP protocol calls to test parameter handling."""

    print("=" * 70)
    print("Testing MCP Protocol Parameter Handling")
    print("=" * 70)

    # Test 1: browser_navigate with dict arguments (correct)
    print("\nTest 1: browser_navigate with dict arguments (correct)")
    try:
        tools = await app.get_tools()
        navigate_tool = tools.get('browser_navigate')

        # Correct: pass dict as `arguments` parameter
        params = {"url": "https://example.com"}
        print(f"  Calling with arguments dict: {params}")

        result = await navigate_tool.run(params)
        # Result is a ToolResult object
        result_data = result.content[0].text if hasattr(result, 'content') else str(result)
        print(f"  ✓ Result: {type(result)} - {str(result_data)[:100]}")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")

    # Test 2: browser_navigate with JSON string (incorrect - what might be happening)
    print("\nTest 2: browser_navigate with JSON STRING (incorrect)")
    try:
        # This simulates potential bug - sending JSON string instead of dict
        params_str = '{"url": "https://example.com"}'
        print(f"  Calling with JSON string: {params_str}")

        result = await navigate_tool.run(params_str)
        print(f"  ✓ Result: {result.get('status')}")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")

    # Test 3: browser_snapshot with empty dict (correct for no-param tool)
    print("\nTest 3: browser_snapshot with empty dict (correct)")
    try:
        snapshot_tool = tools.get('browser_snapshot')
        print(f"  Calling with empty dict: {{}}")

        result = await snapshot_tool.run({})
        result_data = result.content[0].text if hasattr(result, 'content') else str(result)
        print(f"  ✓ Result: {type(result)} - {str(result_data)[:100]}")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")

    # Test 4: browser_snapshot with None (test edge case)
    print("\nTest 4: browser_snapshot with None")
    try:
        result = await snapshot_tool.run(None)
        print(f"  ✓ Result: {result.get('status')}")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")

    # Test 5: browser_snapshot with JSON string (incorrect)
    print("\nTest 5: browser_snapshot with JSON STRING (incorrect)")
    try:
        params_str = '{}'
        print(f"  Calling with JSON string: {params_str}")

        result = await snapshot_tool.run(params_str)
        print(f"  ✓ Result: {result.get('status')}")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(test_mcp_calls())
