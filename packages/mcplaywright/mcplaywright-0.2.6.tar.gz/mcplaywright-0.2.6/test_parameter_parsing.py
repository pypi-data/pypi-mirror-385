#!/usr/bin/env python
"""
Test parameter parsing in FastMCP to diagnose the issue.
"""

from fastmcp import FastMCP
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastMCP("Test Parameter Parsing")


@app.tool()
async def test_required_param(url: str) -> Dict[str, Any]:
    """Test tool with required parameter."""
    return {
        "status": "success",
        "received_url": url,
        "url_type": str(type(url))
    }


@app.tool()
async def test_no_params() -> Dict[str, Any]:
    """Test tool with no parameters."""
    return {
        "status": "success",
        "message": "No params tool works"
    }


@app.tool()
async def test_optional_param(value: str = "default") -> Dict[str, Any]:
    """Test tool with optional parameter."""
    return {
        "status": "success",
        "received_value": value,
        "value_type": str(type(value))
    }


if __name__ == "__main__":
    print("FastMCP Parameter Test Server")
    print("=" * 50)
    print("\nTools registered:")
    print("  1. test_required_param(url: str)")
    print("  2. test_no_params()")
    print("  3. test_optional_param(value: str = 'default')")
    print("\n" + "=" * 50)
    print("\nStarting server...\n")

    app.run()
