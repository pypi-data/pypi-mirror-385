#!/usr/bin/env python
"""
Inspect MCPlaywright tool schemas to debug parameter issues.
"""

import asyncio
import sys
import json

sys.path.insert(0, 'src')

from mcplaywright.server import app


async def main():
    # Get all tools - returns a dict keyed by tool name
    tools = await app.get_tools()

    print(f'Total tools: {len(tools)}\n')

    # Find the problematic tools
    problem_tools = ['browser_navigate', 'browser_snapshot']

    for tool_name in problem_tools:
        tool = tools.get(tool_name)
        if tool:
            print(f'{"=" * 70}')
            print(f'Tool: {tool_name}')
            print(f'Description: {tool.description}')

            # Check parameters
            print(f'\nParameters attribute:')
            print(f'  Type: {type(tool.parameters)}')
            if tool.parameters:
                print(f'  Value: {tool.parameters}')

            # Check to_mcp_tool output
            print(f'\nMCP Tool representation:')
            mcp_tool = tool.to_mcp_tool()
            print(f'  Name: {mcp_tool.name}')
            print(f'  Description: {mcp_tool.description}')
            print(f'  Input Schema:')
            print(json.dumps(mcp_tool.inputSchema, indent=4))
            print()


if __name__ == "__main__":
    asyncio.run(main())
