# Firefox Remote Debugging Protocol (RDP) DevTools Integration

## Executive Summary

This document provides comprehensive documentation on MCPlaywright's Firefox Remote Debugging Protocol (RDP) integration, which parallels the Chromium CDP implementation but uses Mozilla's geckordp library for Firefox-specific debugging capabilities.

## Overview

Firefox RDP provides equivalent functionality to Chrome DevTools Protocol but requires a different connection approach:

- **Chromium CDP**: Direct integration through Playwright's `page.context().new_cdp_session()`
- **Firefox RDP**: External connection via `geckordp.RDPClient()` to debugger server

## Key Differences from Chromium CDP

### Connection Architecture

**Chromium CDP**:
```python
# Integrated directly through Playwright
cdp_session = await page.context().new_cdp_session(page)
await cdp_session.send('Debugger.enable')
```

**Firefox RDP**:
```python
# Requires external geckordp library and explicit connection
from geckordp.rdp_client import RDPClient
from geckordp.actors.root import RootActor

rdp_client = RDPClient()
rdp_client.connect("localhost", 6000)  # RDP port
root = RootActor(rdp_client)
root_ids = root.get_root()
```

### Browser Launch Requirements

**Firefox must be launched with debugger server enabled**:
```python
await playwright.firefox.launch_persistent_context(
    user_data_dir=profile_dir,
    headless=False,
    args=[
        "--start-debugger-server=6000",  # Enable RDP server
        "--no-remote"  # Prevent connection to existing instances
    ]
)
```

### Security Configuration

Firefox shows a security prompt for remote debugging connections by default. This can be bypassed by configuring Firefox preferences:

```javascript
// prefs.js in Firefox profile directory
user_pref("devtools.debugger.remote-enabled", true);
user_pref("devtools.chrome.enabled", true);
user_pref("devtools.debugger.prompt-connection", false);  // Skip connection prompt
user_pref("devtools.debugger.force-local", false);  // Allow remote connections
```

## Firefox RDP Actor Hierarchy

### Browser-Level Actors (Root Level)

Accessed directly from `root.get_root()`:

- **preferenceActor** - Browser preferences management
- **addonsActor** - Extension/addon management
- **deviceActor** - Device information
- **heapSnapshotFileActor** - Memory profiling
- **perfActor** - Performance monitoring
- **parentAccessibilityActor** - Accessibility features
- **screenshotActor** - Screenshot capabilities

### Tab-Level Actors (Page Level)

Accessed through tab descriptor chain: `root.list_tabs()` → `TabActor` → `getTarget()`:

- **consoleActor** - JavaScript console and evaluation
- **inspectorActor** - DOM inspection
- **threadActor** - JavaScript debugging (breakpoints, stepping)
- **networkParentActor** - Network monitoring
- **memoryActor** - Memory analysis
- **storageActor** - LocalStorage, cookies, etc.

## Actor Access Pattern

### Step 1: Connect to RDP Server

```python
from geckordp.rdp_client import RDPClient
from geckordp.actors.root import RootActor

rdp_client = RDPClient()
rdp_client.connect("localhost", 6000)

root = RootActor(rdp_client)
root_ids = root.get_root()  # Get browser-level actors
```

### Step 2: Navigate to Tab-Level Actors

```python
from geckordp.actors.descriptors.tab import TabActor

# List all tabs
tabs = root.list_tabs()
first_tab = tabs[0] if isinstance(tabs, list) else tabs

# Get tab descriptor
tab_actor_id = first_tab.get('actor') if isinstance(first_tab, dict) else first_tab
tab_descriptor = TabActor(rdp_client, tab_actor_id)

# Get page-level target with consoleActor, inspectorActor, etc.
tab_target = tab_descriptor.get_target()
```

### Step 3: Use Page-Level Actors

```python
from geckordp.actors.web_console import WebConsoleActor
from geckordp.actors.inspector import InspectorActor

# JavaScript evaluation
console_actor_id = tab_target.get('consoleActor')
web_console = WebConsoleActor(rdp_client, console_actor_id)
result = web_console.evaluate_js_async("2 + 2")

# DOM inspection
inspector_actor_id = tab_target.get('inspectorActor')
inspector = InspectorActor(rdp_client, inspector_actor_id)
walker_id = inspector.get_walker()
```

## Available RDP Actors and Capabilities

### WebConsoleActor

**Purpose**: JavaScript execution and console message capture

**Key Methods**:
- `evaluate_js_async(text, eager=False)` - Execute JavaScript expressions
- `start_listeners(listeners)` - Begin capturing console messages
- `stop_listeners(listeners)` - Stop capturing messages
- `get_cached_messages(message_types)` - Retrieve console history

**Listener Types**:
- `WebConsoleActor.Listeners.CONSOLE_API` - console.log, console.warn, etc.
- `WebConsoleActor.Listeners.PAGE_ERROR` - JavaScript errors
- `WebConsoleActor.Listeners.FILE_ACTIVITY` - File operations
- `WebConsoleActor.Listeners.REFLOW_ACTIVITY` - Layout changes

**Example**:
```python
web_console = WebConsoleActor(rdp_client, console_actor_id)

# Evaluate JavaScript
result = web_console.evaluate_js_async("document.title")

# Start console capture
web_console.start_listeners([
    WebConsoleActor.Listeners.CONSOLE_API,
    WebConsoleActor.Listeners.PAGE_ERROR
])

# Get captured messages
messages = web_console.get_cached_messages([
    WebConsoleActor.MessageTypes.CONSOLE_API,
    WebConsoleActor.MessageTypes.PAGE_ERROR
])
```

### ThreadActor

**Purpose**: JavaScript debugging with breakpoints and execution control

**Key Methods**:
- `attach(pause_on_exceptions=False, ...)` - Enable debugger
- `resume(resume_limit=ResumeLimit.NONE)` - Resume execution
- `pause()` - Pause execution
- `set_breakpoint(location, options)` - Set breakpoints

**Resume Limits** (stepping control):
- `ThreadActor.ResumeLimit.NONE` - Resume normally
- `ThreadActor.ResumeLimit.NEXT` - Step to next line
- `ThreadActor.ResumeLimit.STEP` - Step into function
- `ThreadActor.ResumeLimit.FINISH` - Step out of function

**Example**:
```python
thread = ThreadActor(rdp_client, thread_actor_id)

# Attach debugger
thread.attach(pause_on_exceptions=True)

# Set breakpoint
thread.set_breakpoint({"line": 42, "url": "https://example.com/script.js"})

# Step through code
thread.resume(resume_limit=ThreadActor.ResumeLimit.NEXT)
```

### InspectorActor & WalkerActor

**Purpose**: DOM tree inspection and manipulation

**Key Methods**:
- `inspector.get_walker()` - Get DOM walker
- `walker.document()` - Get document root
- `walker.querySelector(node, selector)` - Find elements
- `walker.children(node)` - Get child nodes

**Example**:
```python
from geckordp.actors.inspector import InspectorActor
from geckordp.actors.walker import WalkerActor

inspector = InspectorActor(rdp_client, inspector_actor_id)
walker_id = inspector.get_walker()
walker = WalkerActor(rdp_client, walker_id)

# Get document root
document = walker.document()

# Find elements
results = walker.querySelector(document, "#app")
```

### SourceActor

**Purpose**: Source code access and breakpoint position management

**Key Methods**:
- `get_breakpoint_positions(start_line, start_column, end_line, end_column)` - Get valid breakpoint locations
- `get_source()` - Retrieve source code
- `set_breakpoint(line, column, condition)` - Set breakpoint with condition

**Example**:
```python
from geckordp.actors.source import SourceActor

source = SourceActor(rdp_client, source_actor_id)

# Get valid breakpoint positions
positions = source.get_breakpoint_positions(
    start_line=0,
    start_column=0,
    end_line=100,
    end_column=0
)

# Set conditional breakpoint
source.set_breakpoint(line=42, condition="x > 10")
```

## MCPlaywright Firefox DevTools API

### Enable Firefox DevTools

```python
from mcplaywright.tools.firefox_devtools import browser_firefox_dev_tools_enable

result = await browser_firefox_dev_tools_enable({
    "session_id": None,  # Optional, uses current session
    "rdp_port": 6000  # RDP server port
})
```

**Response**:
```json
{
    "status": "success",
    "message": "Firefox DevTools enabled successfully",
    "session_id": "abc123",
    "rdp_port": 6000,
    "enabled_tools": [
        "browser_firefox_dev_tools_disable",
        "browser_firefox_evaluate_js",
        "browser_firefox_set_breakpoint",
        "browser_firefox_resume_execution",
        "browser_firefox_get_console_logs",
        "browser_firefox_inspect_dom"
    ],
    "available_actors": ["preferenceActor", "addonsActor", "..."]
}
```

### JavaScript Evaluation

```python
from mcplaywright.tools.firefox_devtools import browser_firefox_evaluate_js

result = await browser_firefox_evaluate_js({
    "expression": "document.title",
    "session_id": None,
    "eager": False
})
```

### Console Log Capture

```python
from mcplaywright.tools.firefox_devtools import browser_firefox_get_console_logs

logs = await browser_firefox_get_console_logs({
    "session_id": None,
    "message_types": ["PageError", "ConsoleAPI"]
})
```

### DOM Inspection

```python
from mcplaywright.tools.firefox_devtools import browser_firefox_inspect_dom

dom_info = await browser_firefox_inspect_dom({
    "selector": "#app",
    "session_id": None
})
```

## Best Practices

### 1. Isolated Firefox Profiles

Always use isolated profiles to prevent RDP connection interference:

```python
import tempfile

profile_dir = tempfile.mkdtemp(prefix="mcplaywright_firefox_")

context = await playwright.firefox.launch_persistent_context(
    user_data_dir=profile_dir,
    headless=False,
    args=["--start-debugger-server=6001", "--no-remote"]
)
```

### 2. Unique RDP Ports

Use unique RDP ports per session to avoid conflicts:

```python
# Session 1: Port 6001
# Session 2: Port 6002
# Session 3: Port 6003
```

### 3. Security Prompt Bypass

Configure Firefox preferences before launch:

```python
import os

prefs_content = """
user_pref("devtools.debugger.remote-enabled", true);
user_pref("devtools.debugger.prompt-connection", false);
"""

prefs_path = os.path.join(profile_dir, "prefs.js")
with open(prefs_path, "w") as f:
    f.write(prefs_content)
```

### 4. Tab-Level Actor Access

Always navigate through tab descriptors for page-level actors:

```python
# Get tabs
tabs = root.list_tabs()

# Get tab target
tab_descriptor = TabActor(rdp_client, tabs[0]['actor'])
tab_target = tab_descriptor.get_target()

# Now access consoleActor, inspectorActor, etc.
console_actor_id = tab_target.get('consoleActor')
```

### 5. Proper Cleanup

Always disconnect RDP client:

```python
try:
    # Use RDP actors
    pass
finally:
    rdp_client.disconnect()
    await context.close()
```

## Comparison: Firefox RDP vs Chromium CDP

| Feature | Firefox RDP | Chromium CDP |
|---------|-------------|--------------|
| **Connection** | External geckordp library | Integrated in Playwright |
| **Launch Flag** | `--start-debugger-server` | No special flag needed |
| **Security Prompt** | Requires prefs.js bypass | No prompt |
| **Actor Hierarchy** | Root → Tab → Target | Flat session structure |
| **JavaScript Eval** | WebConsoleActor | Runtime.evaluate |
| **Breakpoints** | ThreadActor + SourceActor | Debugger.setBreakpoint |
| **Console** | WebConsoleActor | Console domain |
| **DOM** | InspectorActor + WalkerActor | DOM domain |
| **Network** | NetworkParentActor | Network domain |

## Troubleshooting

### RDP Connection Timeout

**Symptom**: `getRoot()` times out

**Solutions**:
1. Increase wait time after launch: `await asyncio.sleep(8)`
2. Add retry logic with 3-5 attempts
3. Check Firefox is launched with `--start-debugger-server` flag
4. Verify no other Firefox instance is using the RDP port

### Missing Console/Inspector Actors

**Symptom**: `consoleActor` or `inspectorActor` not in `root.get_root()`

**Solution**: These are tab-level actors, access via tab descriptor:
```python
tabs = root.list_tabs()
tab_target = TabActor(rdp_client, tabs[0]['actor']).get_target()
console_actor_id = tab_target.get('consoleActor')
```

### Security Prompt Blocking Connection

**Symptom**: RDP connects but `getRoot()` never returns

**Solution**: Configure Firefox preferences to bypass prompt:
```javascript
user_pref("devtools.debugger.prompt-connection", false);
```

### Port Already in Use

**Symptom**: `Failed to connect to Firefox RDP server on port 6000`

**Solution**: Use a unique port per session:
```python
rdp_port = 6001  # or 6002, 6003, etc.
```

## Integration Example

Complete end-to-end example:

```python
import asyncio
import tempfile
import os
from pathlib import Path

from playwright.async_api import async_playwright
from geckordp.rdp_client import RDPClient
from geckordp.actors.root import RootActor
from geckordp.actors.descriptors.tab import TabActor
from geckordp.actors.web_console import WebConsoleActor


async def firefox_rdp_example():
    # Create isolated profile
    profile_dir = tempfile.mkdtemp(prefix="mcplaywright_")

    # Configure Firefox preferences
    prefs = """
user_pref("devtools.debugger.remote-enabled", true);
user_pref("devtools.debugger.prompt-connection", false);
"""
    Path(profile_dir).joinpath("prefs.js").write_text(prefs)

    async with async_playwright() as p:
        # Launch Firefox with RDP enabled
        context = await p.firefox.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=[
                "--start-debugger-server=6001",
                "--no-remote"
            ]
        )

        # Wait for RDP server
        await asyncio.sleep(8)

        # Connect via RDP
        rdp_client = RDPClient()
        rdp_client.connect("localhost", 6001)

        # Get root actor
        root = RootActor(rdp_client)
        root_ids = root.get_root()

        # Navigate to page
        page = await context.new_page()
        await page.goto("https://example.com")
        await asyncio.sleep(2)

        # Get tab-level actors
        tabs = root.list_tabs()
        tab_target = TabActor(rdp_client, tabs[0]['actor']).get_target()

        # JavaScript evaluation
        console_actor_id = tab_target.get('consoleActor')
        web_console = WebConsoleActor(rdp_client, console_actor_id)
        result = web_console.evaluate_js_async("document.title")
        print(f"Page title: {result}")

        # Cleanup
        rdp_client.disconnect()
        await context.close()


if __name__ == "__main__":
    asyncio.run(firefox_rdp_example())
```

## Future Enhancements

Planned Firefox RDP features:

1. **Breakpoint Management** - Full ThreadActor integration
2. **Network Monitoring** - NetworkParentActor for request inspection
3. **Memory Profiling** - HeapSnapshot and MemoryActor integration
4. **Performance Analysis** - PerfActor for CPU profiling
5. **Storage Management** - StorageActor for cookies, localStorage
6. **Addon Integration** - AddonsActor for extension management

## References

- **geckordp Documentation**: https://github.com/jpramosi/geckordp
- **Firefox RDP Specification**: https://firefox-source-docs.mozilla.org/devtools/backend/protocol.html
- **MCPlaywright CDP Equivalent**: `/docs/guides/PLAYWRIGHT_CDP_DEBUGGER_RESEARCH.md`
- **Test Implementation**: `/test_firefox_devtools.py`
