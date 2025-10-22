# MCPlaywright 🎭

**Browser Automation for Model Context Protocol**

A FastMCP 2.0-based server providing comprehensive browser automation with video recording, HTTP request monitoring, tab management, and console capture. Complete Python implementation achieving full feature parity with the TypeScript Playwright MCP reference, plus AI-human collaboration capabilities including voice communication, interactive messaging, and mathematical mouse precision.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12%2B-green)](https://gofastmcp.com)
[![Playwright](https://img.shields.io/badge/Playwright-1.55%2B-orange)](https://playwright.dev)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## ✨ Key Features

### 🎬 Smart Video Recording System
- **Multi-mode Recording**: Smart, continuous, action-only, and segment modes
- **Automatic Viewport Matching**: Eliminates gray borders by matching browser viewport to video size
- **Action-Aware Recording**: Automatically pause/resume based on browser interactions
- **Session-Based Management**: Persistent recording state across MCP calls

### 📊 Advanced HTTP Request Monitoring
- **Comprehensive Capture**: Headers, bodies, timing, and failure information
- **Advanced Filtering**: URL patterns, status codes, performance thresholds
- **Export Capabilities**: JSON, HAR, CSV formats with detailed analysis
- **Real-time Monitoring**: Live request tracking with performance metrics
- **HAR Export**: Chrome DevTools-compatible format for deep analysis

### 🗂️ Tab Management & Multi-Page Workflows
- **Dynamic Tab Creation**: Open new tabs with optional URL navigation
- **Tab Enumeration**: List all open tabs with titles, URLs, and active status
- **Tab Switching**: Seamlessly switch between multiple browser tabs
- **Tab Cleanup**: Close tabs with automatic focus management
- **Session Isolation**: Each tab maintains independent state and context

### 📝 Console Message Capture & Analysis
- **Persistent Storage**: Circular buffer with 1000 message capacity prevents memory leaks
- **Message Filtering**: Filter by type (log, error, warning, info), text search, and severity
- **Source Location Tracking**: File paths, line numbers, and column information
- **Paginated Retrieval**: Efficient access to large console logs with cursor-based navigation
- **Real-time Monitoring**: Automatic capture from page load through automation lifecycle

### 🎨 Browser UI Customization
- **Visual Demonstration**: slowMo delays for training videos and demos
- **DevTools Integration**: Automatic Chrome DevTools opening
- **Theme Customization**: Dark mode, custom browser arguments
- **Container Support**: Sandbox control for deployment environments

### 🧩 Chrome Extension Management
- **Real Browser Restart**: Automatic browser context restart with extensions loaded
- **Popular Extensions Catalog**: React/Vue/Redux DevTools, Lighthouse, axe, and more
- **Functional Demo Extensions**: Content scripts with visual indicators and detection
- **Chrome Channel Validation**: Warnings and guidance for optimal extension support

### 🤖 AI-Human Collaboration
- **Real-Time Visual Messaging**: Cyberpunk-themed notifications with mcpNotify API
- **Interactive User Dialogs**: Direct user confirmation with mcpPrompt for automation decisions
- **Visual Element Inspector**: Interactive element selection with mcpInspector for precise targeting
- **Voice Communication**: Browser-native text-to-speech and speech recognition using Web Speech API
- **Secure V8 Injection**: Comprehensive error boundaries with page.addInitScript() for safety

### 🎨 Professional Theme System
- **5 Built-in Themes**: Minimal, Corporate, Hacker, Glassmorphism, High Contrast designs
- **Accessibility Compliance**: WCAG contrast ratios from 5.2:1 to 21:1
- **47 CSS Custom Properties**: Complete theming control with CSS variables
- **Dynamic Theme Switching**: Real-time theme changes with persistence across sessions
- **Custom Theme Creation**: Extensible theme architecture for brand-specific styling

### 🖱️ Mathematical Mouse Precision
- **Subpixel Precision**: Coordinate-based interactions with mathematical interpolation
- **Smooth Easing Functions**: Hermite interpolation and bezier curves for natural movement
- **Complex Gesture Patterns**: Multi-waypoint paths with customizable timing and acceleration
- **Arc-Based Movement**: Circular and elliptical mouse paths for sophisticated interactions
- **Bezier Curves**: Quadratic bezier curves and smooth step functions for fluid motion

### 📄 Enterprise-Grade Pagination System
- **Session-Scoped Cursors**: Server-side cursor management with security isolation
- **Bidirectional Navigation**: Navigate forward and backward through large result sets
- **Adaptive Optimization**: Machine learning-like chunk size adaptation for optimal performance
- **Query State Fingerprinting**: Automatic parameter change detection and cursor invalidation
- **Performance Insights**: Real-time monitoring with optimization recommendations

### 🗃️ Advanced Artifacts Management
- **Session-Based Organization**: Intelligent file storage with 9 supported artifact types
- **Comprehensive Analytics**: Real-time statistics tracking with file size and type analysis
- **Intelligent Cleanup**: Configurable retention policies with automatic space management
- **Performance Monitoring**: Artifact creation tracking with detailed metadata
- **Multi-Format Support**: Screenshots, videos, PDFs, JSON, CSV, HAR, logs, reports, custom files

### 🎭 Debug Toolbar & Client Identification
- **Django-Style Debug Toolbar**: Visual identification of which MCP client controls the browser
- **Live Session Tracking**: Real-time session ID, timestamp, and client information display
- **Custom Code Injection**: Inject JavaScript/CSS for debugging and testing
- **Multi-Client Support**: Perfect for parallel development and testing workflows
- **Auto-Persistence**: Toolbar survives page navigation and browser refreshes

### 🔧 Session-Based Architecture
- **Persistent Contexts**: Browser state maintained across MCP calls
- **State Management**: Video recording, request monitoring, UI settings, pagination cursors
- **Artifact Management**: Centralized file storage and organization
- **Multi-Session Support**: Concurrent isolated browser sessions

## 🆕 Recent Improvements (v0.2.4-v0.2.5)

### Security Enhancements
- **Code Injection Validation**: Comprehensive security checks prevent malicious JavaScript/CSS injection
  - Pattern detection for dangerous constructs (eval, Function, __proto__, etc.)
  - Input length limits (50KB max) and character whitelisting
  - Defense-in-depth with multiple validation layers
- **XSS Prevention**: HTML and JavaScript escaping in debug toolbar generation
  - Context-aware escaping for user-supplied values
  - Protection against injection attacks in session IDs and project names

### Performance Improvements
- **Async SQLite Migration**: Non-blocking I/O with aiosqlite eliminates 200-1000ms event loop blocking
  - Concurrent operation processing for multiple MCP clients
  - Replaced synchronous sqlite3 with async aiosqlite throughout storage layer
  - Migrated threading.RLock to asyncio.Lock for proper async coordination
- **Console Message Memory Optimization**: Circular buffer prevents unbounded memory growth
  - collections.deque with maxlen=1000 for automatic FIFO eviction
  - Dropped message tracking with warning logs
  - Prevents memory leaks in long-running browser sessions

### Dependency Simplification
- **Redis Removal**: Eliminated external Redis dependency for simpler deployment
  - SQLite and in-memory storage sufficient for most use cases
  - Reduced infrastructure requirements and attack surface
  - Streamlined Docker configuration without Redis service

### Complete Feature Parity
- **40+ MCP Tools Exposed**: All TypeScript playwright-mcp features now available in Python
- **HTTP Request Monitoring**: Comprehensive capture with HAR export for Chrome DevTools
- **Tab Management**: Full multi-page workflow support with session isolation
- **Console Capture**: Persistent message storage with advanced filtering

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended) or pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcplaywright

# Install with uv (recommended)
make install-dev
make playwright

# Or with pip
pip install -e ".[dev]"
playwright install chromium firefox webkit
```

### Development Setup

```bash
# Set up complete development environment
make setup

# Start development server with hot-reload
make dev
```

### Production Setup

```bash
# Install production dependencies only
make install

# Start production server
make serve
```

## 🛠️ Usage

### Adding to Claude Code

To use MCPlaywright with Claude Code, add it as an MCP server:

```bash
# Using the installed script (recommended after pip/uv install)
claude mcp add mcplaywright -- mcplaywright

# With uv run (for local development)
claude mcp add mcplaywright -- uv run python -m mcplaywright.server

# With Python module (alternative)
claude mcp add mcplaywright -- python -m mcplaywright.server

# With environment variables
claude mcp add mcplaywright --env BROWSER_TYPE=chromium --env VIDEO_RECORDING_MODE=smart \
  -- mcplaywright
```

### Running the Server

```bash
# Default: stdio transport (standard MCP)
uvx mcplaywright

# With different log level
uvx mcplaywright --log-level DEBUG

# HTTP transport (automatically enabled when port specified)
uvx mcplaywright --port 8001

# HTTP with custom host
uvx mcplaywright --host 0.0.0.0 --port 8000

# Using uv directly from source
uv run python -m mcplaywright.server
```

### Available Tools

MCPlaywright provides comprehensive browser automation tools through FastMCP:

#### Core Browser Tools
- `navigate` - Navigate to URLs with session management
- `take_screenshot` - Capture screenshots with various options  
- `click_element` - Click elements using CSS selectors
- `get_page_info` - Get current page information

#### 🤖 AI-Human Collaboration Tools
- `browser_notify_user` - Real-time visual messaging with cyberpunk theming
- `browser_prompt_user` - Interactive user confirmation dialogs
- `browser_start_inspector` - Visual element selection with detailed inspection
- `browser_enable_voice_collaboration` - Voice communication with text-to-speech and speech recognition
- `browser_speak_message` - AI speaks to user during automation
- `browser_listen_for_voice` - Capture user voice responses
- `browser_stop_voice_collaboration` - Disable voice features

#### 🎨 Theme & Visual Tools
- `browser_mcp_theme_list` - List all available professional themes
- `browser_mcp_theme_set` - Apply themes (minimal, corporate, hacker, glassmorphism, high contrast)
- `browser_mcp_theme_create` - Create custom themes with CSS variables
- `browser_mcp_theme_get` - Get current theme configuration
- `browser_mcp_theme_reset` - Reset to default minimal theme

#### 🖱️ Mathematical Mouse Tools
- `browser_mouse_move_smooth` - Smooth mouse movement with bezier curves
- `browser_mouse_move_arc` - Circular/elliptical mouse movement patterns
- `browser_mouse_draw_gesture` - Complex multi-waypoint gesture patterns
- `browser_mouse_trace_element` - Trace element boundaries with mathematical precision

#### 🗃️ Advanced Artifacts Management
- `browser_get_artifact_paths` - Reveal artifact storage locations
- `browser_list_artifacts` - List artifacts with comprehensive analytics
- `browser_analyze_artifacts` - Detailed artifact analysis and statistics
- `browser_cleanup_artifacts` - Intelligent cleanup with retention policies

#### Tab Management Tools
- `browser_tab_new` - Open new browser tabs with optional URL navigation
- `browser_tab_list` - List all tabs with detailed information (title, URL, active status)
- `browser_tab_select` - Switch to different tabs by index
- `browser_tab_close` - Close tabs with automatic focus management

#### Video Recording Tools
- `browser_start_video_recording` - Start recording with multiple modes (smart, continuous, action-only, segment)
- `browser_stop_video_recording` - Stop recording and save video files with session artifacts

#### Wait Strategy Tools
- `browser_wait_text` - Wait for specific text to appear on page
- `browser_wait_text_gone` - Wait for text to disappear from page
- `browser_wait_element` - Wait for element states (visible, hidden, attached, detached)
- `browser_wait_load` - Wait for page load states (load, domcontentloaded, networkidle)
- `browser_wait_timeout` - Wait for specific duration with smart video pause
- `browser_wait_network` - Wait for network requests matching URL patterns

#### JavaScript & Dialog Tools
- `browser_js_evaluate` - Execute JavaScript in page or element context with return values
- `browser_dialog_handle` - Handle browser dialogs (alert, confirm, prompt)
- `browser_file_chooser_dismiss` - Dismiss file chooser dialogs gracefully
- `browser_keyboard_press` - Press keyboard keys with modifier support
- `browser_keyboard_type` - Type text with configurable delays

#### Data & Monitoring Tools
- `browser_monitoring_start` - Start comprehensive HTTP request/response monitoring
- `browser_monitoring_get` - Retrieve captured requests with advanced filtering
- `browser_monitoring_export` - Export to HAR, JSON, or summary formats
- `browser_monitoring_clear` - Clear captured request data
- `browser_monitoring_status` - Check monitoring status and configuration
- `browser_console_messages` - Paginated console message retrieval with filtering
- `browser_clear_console` - Clear all stored console messages

#### Debug & Development Tools
- `browser_enable_debug_toolbar` - Enable visual debug toolbar for client identification
- `browser_disable_debug_toolbar` - Disable the debug toolbar
- `browser_inject_custom_code` - Inject custom JavaScript/CSS for debugging
- `browser_list_injections` - List all active code injections
- `browser_clear_injections` - Clear custom injections (optional: keep toolbar)

#### Configuration Tools
- `configure_browser` - Advanced browser configuration and UI customization
- `list_sessions` - List all active browser sessions
- `get_session_info` - Get detailed session information
- `close_session` - Close sessions and clean up resources

#### System Tools
- `health_check` - Server health and status information
- `server_info` - Detailed server capabilities and information
- `test_playwright_installation` - Verify Playwright setup

### Tab Management Examples

```python
# Open new tab with URL
new_tab = await browser_tab_new({
    "url": "https://example.com/products",
    "session_id": None  # Use current session
})
print(f"Opened tab {new_tab['tab_index']} with {new_tab['tab_count']} total tabs")

# List all open tabs
tabs = await browser_tab_list({"session_id": None})
for tab in tabs['tabs']:
    marker = "→" if tab['is_current'] else " "
    print(f"{marker} Tab {tab['index']}: {tab['title']} - {tab['url']}")

# Switch to specific tab
await browser_tab_select({
    "tab_index": 0,
    "session_id": None
})

# Close current tab
await browser_tab_close({"session_id": None})
```

### Console Message Monitoring

```python
# Get console messages with filtering
messages = await browser_console_messages({
    "type_filter": "error",  # log, error, warning, info, or all
    "search": "API",         # Text search filter
    "limit": 50,
    "session_id": None
})

print(f"Found {messages['total_messages']} console messages")
for msg in messages['messages']:
    print(f"[{msg['type']}] {msg['text']}")
    if msg['location']:
        print(f"  at {msg['location']['url']}:{msg['location']['line_number']}")

# Clear console history
await browser_clear_console()
```

### HTTP Request Monitoring Examples

```python
# Start monitoring with body capture
await browser_monitoring_start({
    "session_id": None,
    "capture_body": True,
    "url_filter": "/api/*"
})

# Navigate and generate requests
await navigate({"url": "https://api.example.com"})

# Retrieve captured requests with filtering
requests = await browser_monitoring_get({
    "session_id": None,
    "filter_type": "success",  # all, failed, slow, errors, success
    "domain": "api.example.com",
    "limit": 50
})

print(f"Captured {requests['total_captured']} requests")
for req in requests['requests']:
    print(f"{req['method']} {req['status']} - {req['url']} ({req['duration']}ms)")

# Export to HAR for Chrome DevTools
har_export = await browser_monitoring_export({
    "session_id": None,
    "format": "har"  # har, json, or summary
})
print(f"Exported to: {har_export['export_path']}")
```

### Basic Browser Automation Examples

```python
# Example: Configure browser with UI customization
await configure_browser({
    "headless": False,
    "slow_mo": 500,          # 500ms delays for demo recording
    "devtools": True,        # Open DevTools automatically
    "viewport_width": 1920,  
    "viewport_height": 1080,
    "args": [
        "--force-dark-mode",
        "--start-maximized"
    ]
})

# Navigate and take screenshot
await navigate({"url": "https://example.com"})
await take_screenshot({
    "filename": "example-page.png",
    "full_page": True
})

# Click an element
await click_element({
    "selector": "button.primary",
    "button": "left"
})

# Paginated request monitoring
response = await browser_get_requests({
    "limit": 50,
    "filter": "success",
    "domain": "api.example.com"
})

# Continue pagination with cursor
if response.get("has_more"):
    next_page = await browser_get_requests({
        "cursor_id": response["cursor_id"],
        "limit": 50
    })
```

### 🤖 AI-Human Collaboration Examples

```python
# Enable voice communication for interactive automation
await browser_enable_voice_collaboration({
    "enabled": True,
    "voice_options": {
        "rate": 1.0,
        "pitch": 1.0,
        "volume": 1.0,
        "lang": "en-US"
    },
    "listen_options": {
        "timeout": 10000,
        "continuous": False,
        "lang": "en-US"
    }
})

# AI speaks to user during automation
await browser_speak_message({
    "message": "I found the login form. Should I proceed with authentication?",
    "options": {
        "rate": 1.0,
        "pitch": 1.0,
        "volume": 0.8
    }
})

# Get user confirmation with voice or visual dialog
confirmation = await browser_prompt_user({
    "message": "Found multiple payment options. Which would you like to use?",
    "options": ["Credit Card", "PayPal", "Apple Pay"],
    "timeout": 30000,
    "allow_voice": True
})

# Interactive element selection with detailed inspection
element_data = await browser_start_inspector({
    "instruction": "Please click on the main navigation menu",
    "show_details": True,
    "highlight_on_hover": True
})

# Real-time visual notifications during automation
await browser_notify_user({
    "message": "Processing payment... This may take a moment.",
    "type": "info",
    "duration": 3000,
    "position": "top-right"
})

# Mathematical precision mouse movement with bezier curves
await browser_mouse_move_smooth({
    "target_x": 500,
    "target_y": 300,
    "duration": 1000,
    "easing": "bezier",
    "control_points": [
        {"x": 200, "y": 100},
        {"x": 400, "y": 250}
    ]
})

# Apply professional glassmorphism theme
await browser_mcp_theme_set({
    "theme_id": "glassmorphism",
    "persist": True
})

# Advanced artifacts analysis
artifacts = await browser_analyze_artifacts({
    "session_id": "current",
    "include_analytics": True,
    "group_by": "type"
})
```

### 🎨 Advanced Theme System Examples

```python
# Create custom brand theme
await browser_mcp_theme_create({
    "id": "company-brand",
    "name": "Company Brand Theme",
    "description": "Corporate brand colors with high accessibility",
    "base_theme": "corporate",
    "variables": {
        "--mcp-primary-color": "#2563eb",
        "--mcp-secondary-color": "#64748b", 
        "--mcp-accent-color": "#f59e0b",
        "--mcp-background-color": "#ffffff",
        "--mcp-text-color": "#1e293b",
        "--mcp-border-radius": "8px",
        "--mcp-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    }
})

# List all available themes with categories
themes = await browser_mcp_theme_list({
    "filter": "all",  # all, builtin, custom
    "include_details": True
})
```

## 🧪 Testing

MCPlaywright includes comprehensive testing with enhanced HTML reports:

```bash
# Run all tests
make test

# Run fast tests only (exclude slow/integration)
make test-fast

# Run tests in watch mode
make test-watch

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m browser

# Generate detailed test report
make test-report
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Complete workflow testing
- **Browser Tests**: Real browser automation testing
- **Performance Tests**: Benchmarking and performance validation

## 🐳 Docker Development

```bash
# Build Docker images
make docker-build

# Start containerized development
make docker-dev

# Run tests in Docker
make docker-test
```

## 📋 Development Commands

```bash
# Setup and Installation
make install         # Install dependencies
make install-dev     # Install with dev dependencies  
make playwright      # Install Playwright browsers
make setup          # Complete dev environment setup

# Development
make dev            # Start dev server with hot-reload
make serve          # Start production server
make health         # Check server health
make info           # Show server information

# Testing
make test           # Run full test suite
make test-fast      # Run fast tests only
make test-watch     # Run tests in watch mode
make benchmark      # Run performance benchmarks

# Code Quality
make lint           # Run linting and type checking
make format         # Format code with black/isort
make security       # Security vulnerability check

# Utilities
make clean          # Clean build artifacts
make build          # Build distribution packages
```

## 🏗️ Architecture

### Core Components

- **Context Class**: Browser context management with persistent sessions
- **Session Manager**: Multi-session handling with isolation and cleanup
- **Video Recording**: Smart recording system with multiple modes
- **Request Monitoring**: Advanced HTTP request/response capture
- **Artifact Management**: Centralized file storage and organization

### Beyond Standard Playwright

1. **🤖 AI-Human Collaboration**: Real-time voice communication and interactive messaging
2. **🎨 Professional Theme System**: 5 built-in themes with accessibility compliance and 47 CSS variables
3. **🖱️ Mathematical Mouse Precision**: Bezier curves, smooth interpolation, and complex gesture patterns
4. **🗃️ Advanced Artifacts Management**: Session-based organization with 9 artifact types and intelligent cleanup
5. **📄 Enterprise Pagination**: Cursor-based navigation with adaptive optimization and query fingerprinting
6. **🔒 Secure V8 Injection**: Comprehensive error boundaries with page.addInitScript() safety plus code validation
7. **🎬 Smart Video Recording**: Automatic pause/resume based on browser activity with viewport matching
8. **🔄 Session Persistence**: Browser contexts survive across MCP calls with multi-session isolation
9. **📊 Advanced Request Monitoring**: Beyond basic Playwright network events with HAR/JSON/CSV export
10. **🗂️ Tab Management**: Multi-page workflows with dynamic creation, switching, and cleanup
11. **📝 Console Message Capture**: Persistent storage with circular buffer and advanced filtering
12. **🎭 Debug Toolbar**: Django-style visual client identification and debugging
13. **🎨 UI Customization**: Professional demo recording capabilities with slowMo and DevTools
14. **🧩 Chrome Extension Management**: Real browser restart with functional demo extensions
15. **⏱️ Advanced Wait Strategies**: Text, element, network, and load state waiting with smart video pause
16. **🔐 Enhanced Security**: Code injection validation, XSS prevention, and input sanitization
17. **⚡ Async Performance**: Non-blocking SQLite I/O and optimized circular buffers

### Technology Stack

- **FastMCP 2.0**: Modern MCP server framework with advanced features
- **Playwright**: Cross-browser automation with Chromium, Firefox, WebKit
- **Pydantic**: Type validation and configuration management
- **pytest**: Comprehensive testing with enhanced HTML reports
- **Docker**: Containerized development and deployment

## 🎯 Advanced Features

### Video Recording Modes

```python
# Smart mode - auto-pause during waits
{"mode": "smart"}

# Continuous mode - record everything
{"mode": "continuous"} 

# Action-only mode - minimal recording
{"mode": "action-only"}

# Segment mode - separate files per action
{"mode": "segment"}
```

### UI Customization Options

```python
{
    "slow_mo": 500,           # Visual delays for demos
    "devtools": True,         # Auto-open DevTools
    "args": [
        "--force-dark-mode",  # Dark theme
        "--start-maximized"   # Full screen
    ],
    "chromium_sandbox": False # Container deployment
}
```

### Request Monitoring

```python
# Enable comprehensive request monitoring
await enable_request_monitoring({
    "capture_bodies": True,
    "url_filter": "/api/*",
    "export_format": "har"
})
```

### Debug Toolbar & Client Identification

Perfect for multi-developer environments and debugging browser automation:

```python
# Enable debug toolbar with custom branding
await browser_enable_debug_toolbar({
    "project_name": "Alice-Auth-Testing",
    "position": "bottom-right",  # top-left, top-right, bottom-left, bottom-right
    "theme": "dark",            # dark or light
    "opacity": 0.9,             # 0.1 to 1.0
    "minimized": False,         # Start expanded
    "show_details": True        # Show session details
})

# Inject custom debugging code
await browser_inject_custom_code({
    "name": "performance_monitor",
    "code": """
        window.perfStart = performance.now();
        window.logPerf = () => console.log('Runtime:', performance.now() - window.perfStart);
    """,
    "type": "javascript",
    "auto_inject": True  # Re-inject on page navigation
})

# Add visual test environment indicator
await browser_inject_custom_code({
    "name": "test_indicator",
    "code": """
        body::before { 
            content: 'TEST ENVIRONMENT'; 
            position: fixed; top: 0; right: 0; 
            background: orange; color: white; 
            padding: 5px 10px; z-index: 999999; 
        }
    """,
    "type": "css",
    "auto_inject": True
})

# List all active injections
injections = await browser_list_injections()
print(f"Active: {injections['injection_count']} injections")

# Clear custom code but keep toolbar
await browser_clear_injections({"include_toolbar": False})
```

**Visual Debug Toolbar Features:**
- 🟢 Live connection status indicator (pulsing green dot)
- 📊 Real-time session ID and timestamp
- 🎭 Custom project/client identification
- 🔢 Active injection counter
- 🎛️ Minimize/expand toggle
- ⏰ Live clock updated every second

### Chrome Extension Management

```python
# Install popular extension with functional demo
await browser_install_popular_extension({
    "extension": "react-devtools"
})

# Install from local directory
await browser_install_extension({
    "path": "/path/to/extension",
    "name": "My Extension"
})
```

See [EXTENSION_IMPLEMENTATION.md](EXTENSION_IMPLEMENTATION.md) for detailed documentation on the Chrome extension management system.

## 📊 Performance & Optimization

### Feature Set
- Complete feature parity with TypeScript Playwright MCP plus AI-human collaboration
- Lean dependency tree: 15 core packages focused on browser automation
- Mathematical precision: Subpixel mouse control with bezier curve interpolation
- Security: Comprehensive error boundaries and code validation
- Memory efficient: Python's async handling with optimized circular buffers

### Development Benefits
- Python expressiveness for rapid development
- Concurrent sessions with independent isolation
- Browser-native speech APIs with no external dependencies
- 5 built-in themes with WCAG accessibility compliance
- Cursor-based pagination with adaptive optimization

### Dependency Optimization
- **Before**: 45+ dependencies including pandas, numpy, asyncio-throttle
- **After**: 15 core dependencies for browser automation
- **Impact**: ~30MB footprint reduction, faster startup, smaller attack surface

## 🔧 Configuration

### Environment Variables

```bash
# Server Configuration
DOMAIN=mcplaywright.local
HOST=0.0.0.0
PORT=8000

# Browser Configuration  
BROWSER_TYPE=chromium
DEFAULT_HEADLESS=true
DEFAULT_VIEWPORT_WIDTH=1280
DEFAULT_VIEWPORT_HEIGHT=720

# Video Recording
VIDEO_RECORDING_MODE=smart
VIDEO_OUTPUT_DIR=./artifacts/videos

# Request Monitoring
HTTP_MONITORING_ENABLED=true
REQUEST_CAPTURE_BODIES=true

# Development
DEBUG_LEVEL=INFO
DEVELOPMENT_MODE=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `make test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

- Follow Python typing and use Pydantic models
- Add comprehensive tests for new features
- Update documentation for API changes
- Run `make lint` before committing
- Ensure all tests pass with `make test`

## 📚 Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[Features](docs/features/)**: Detailed feature capabilities and implementations
- **[Implementation Guides](docs/guides/)**: Development workflows and technical guides
- **[API Documentation](docs/api/)**: Technical references and implementation details
- **[Examples](docs/examples/)**: Practical examples and detailed test reports

For quick navigation, see the [Documentation Index](docs/README.md).

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original TypeScript Playwright MCP implementation
- FastMCP framework for modern MCP development
- Playwright team for excellent browser automation
- Python community for outstanding async tooling

---

**Made with ❤️ for the MCP community**