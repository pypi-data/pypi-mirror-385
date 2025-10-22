# Troubleshooting MCP Parameter Issues

## Issue: Input Validation Errors

### Symptoms

When calling MCPlaywright tools from MCP clients (Claude Desktop, etc.), you may encounter:

```
● mcplaywright - browser_navigate (MCP)(params: "{\"url\": \"https://example.com/\"}")
  ⎿  Error: Input validation error: 'url' is a required property

● mcplaywright - browser_snapshot (MCP)(params: "{}")
  ⎿  Error: Error calling tool 'browser_snapshot': 1 validation error for call[get_page_snapshot]
     params
       Unexpected keyword argument [type=unexpected_keyword_argument, input_value='{}', input_type=str]
```

### Root Cause

The MCP client is sending parameters as **JSON strings** instead of **parsed JSON objects**:

- ❌ Incorrect: `params: "{\"url\": \"https://example.com\"}"` (STRING)
- ✅ Correct: `params: {"url": "https://example.com"}` (OBJECT)

### Verification

The MCPlaywright server is working correctly. Testing shows:

```bash
# Test with correct dict parameters
$ uv run python test_mcp_protocol.py

Test 1: browser_navigate with dict arguments (correct)
  ✓ Result: {"status":"success","url":"https://example.com/","title":"Example Domain"}

Test 2: browser_navigate with JSON STRING (incorrect)
  ✗ Error: AttributeError: 'str' object has no attribute 'copy'

Test 3: browser_snapshot with empty dict (correct)
  ✓ Result: {"status":"success","url":"https://example.com/","snapshot":{...}}
```

**Tool schemas are valid**:
```json
{
  "name": "browser_navigate",
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": {"type": "string"},
      "wait_until": {"type": "string", "default": "load"}
    },
    "required": ["url"]
  }
}
```

## Solution

### Option 1: Update MCP Client Configuration (Recommended)

Ensure your MCP client is configured to send parsed JSON objects, not strings.

**For Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mcplaywright": {
      "command": "uvx",
      "args": ["mcplaywright"]
    }
  }
}
```

**For Claude Code** (`.claude/mcp.json` or user-level config):
```json
{
  "mcpServers": {
    "mcplaywright": {
      "command": "uvx",
      "args": ["mcplaywright"]
    }
  }
}
```

### Option 2: Verify FastMCP Version

Ensure you're using FastMCP 2.12.5 or later:

```bash
uv pip install --upgrade "fastmcp>=2.12.5"
```

### Option 3: Check MCP Client Version

Some older MCP clients have parameter parsing bugs. Update to the latest version:

- **Claude Desktop**: Check for updates
- **Claude Code**: Update to latest version
- **Custom clients**: Ensure MCP SDK is up to date

### Option 4: Manual Parameter Wrapping (Workaround)

If you're building a custom MCP client, ensure parameters are sent as objects:

```python
# Python MCP client example
import json

# ❌ Don't do this
params = '{"url": "https://example.com"}'  # String
result = await client.call_tool("browser_navigate", params)

# ✅ Do this
params = {"url": "https://example.com"}  # Dict/Object
result = await client.call_tool("browser_navigate", params)
```

```javascript
// JavaScript MCP client example
// ❌ Don't do this
const params = JSON.stringify({url: "https://example.com"});  // String
await client.callTool("browser_navigate", params);

// ✅ Do this
const params = {url: "https://example.com"};  // Object
await client.callTool("browser_navigate", params);
```

## Testing Your Setup

### Test 1: Direct Server Test

```bash
# Clone the repo
git clone https://github.com/anthropics/mcplaywright.git
cd mcplaywright

# Run parameter test
uv run python test_mcp_protocol.py
```

Expected output:
```
Test 1: browser_navigate with dict arguments (correct)
  ✓ Result: {"status":"success",...}

Test 3: browser_snapshot with empty dict (correct)
  ✓ Result: {"status":"success",...}
```

### Test 2: MCP Client Test

Restart your MCP client and try:

```
Navigate to https://example.com
```

If successful, you should see navigation complete without errors.

## Debugging Steps

### Step 1: Check Server Logs

Enable debug logging in your MCP server:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Run server
uvx mcplaywright
```

### Step 2: Inspect Tool Schemas

```bash
# View all tool schemas
uv run python inspect_tools.py
```

Look for the `browser_navigate` and `browser_snapshot` schemas. They should show:
- `browser_navigate`: `required: ["url"]`
- `browser_snapshot`: `properties: {}`

### Step 3: Test with MCP Inspector

Use the MCP Inspector tool to test tools directly:

```bash
npx @modelcontextprotocol/inspector uvx mcplaywright
```

### Step 4: Check Client-Side Logs

Enable client-side logging to see what parameters are being sent:

- **Claude Desktop**: Check `~/Library/Logs/Claude/mcp-server-mcplaywright.log`
- **Claude Code**: Check output panel for MCP logs

## Common Causes

### 1. Outdated MCP Client

**Symptom**: Parameters sent as strings
**Solution**: Update MCP client to latest version

### 2. Custom JSON Serialization

**Symptom**: Double-encoded JSON
**Solution**: Remove custom serialization, let MCP protocol handle it

### 3. Middleware Interference

**Symptom**: Parameters modified by middleware
**Solution**: Check middleware configuration

### 4. Protocol Version Mismatch

**Symptom**: Incompatible parameter formats
**Solution**: Ensure client and server use same MCP protocol version

## Verification Checklist

- [ ] FastMCP version ≥ 2.12.5
- [ ] MCP client updated to latest version
- [ ] Tool schemas are valid (check with `inspect_tools.py`)
- [ ] Parameters sent as objects, not strings
- [ ] Server logs show no parameter parsing errors
- [ ] Direct tool invocation works (`test_mcp_protocol.py`)

## Getting Help

If issues persist:

1. **File an issue**: https://github.com/anthropics/mcplaywright/issues
   - Include server version (`uvx mcplaywright --version`)
   - Include client version and type
   - Include full error message and logs
   - Include MCP configuration

2. **Discord**: Join the Anthropic Discord for MCP support

3. **Documentation**: Check https://modelcontextprotocol.io for MCP protocol details

## Related Issues

- FastMCP parameter handling: https://github.com/jlowin/fastmcp/issues
- MCP protocol spec: https://spec.modelcontextprotocol.io

## Summary

The MCPlaywright server is working correctly. Parameter validation errors are caused by MCP clients sending JSON strings instead of parsed objects. Update your MCP client configuration or client version to resolve the issue.
