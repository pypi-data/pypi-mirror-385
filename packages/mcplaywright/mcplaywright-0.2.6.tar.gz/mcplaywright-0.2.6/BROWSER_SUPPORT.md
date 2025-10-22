# Browser Support Status

MCPlaywright supports all three Playwright browser engines with varying compatibility based on your operating system.

## ✅ Fully Supported Browsers

### Chromium (Chrome/Edge)
- **Status**: ✅ Fully supported on all platforms
- **Version**: 140.0.7339.16 (Playwright build v1187)
- **Features**: All MCPlaywright features including Chrome extensions
- **Testing**: ✅ Validated working

### Firefox (Gecko Engine)
- **Status**: ✅ Fully supported on all platforms
- **Version**: 141.0 (Playwright build v1490)
- **Features**: All MCPlaywright features except Chrome-specific extensions
- **Testing**: ✅ Validated working

## ⚠️ Platform-Specific Issues

### WebKit (Safari Engine)
- **Status**: ⚠️ Works on macOS/Windows, limited on Linux
- **Version**: Playwright build v2092
- **Linux Issue**: Requires older system libraries (ICU 66, libffi 7)
  - Modern rolling-release Linux (Arch, Fedora) have newer versions
  - Ubuntu 20.04 LTS and older work without issues
  - Newer Ubuntu (22.04+) may have similar issues
- **macOS/Windows**: ✅ Full support expected

## Recommended Configuration

For **maximum compatibility**, use:
1. **Chromium** - Default, best feature support
2. **Firefox** - Cross-browser testing alternative

For **iOS/Safari testing**, use WebKit on macOS or Windows hosts.

## Installation

```bash
# Install all browsers
uv run playwright install

# Install specific browser
uv run playwright install chromium
uv run playwright install firefox

# On Linux, install system dependencies
# Ubuntu/Debian
sudo playwright install-deps

# Arch Linux (manual)
sudo pacman -S icu libxml2 libwebp libffi
```

## Testing Browser Support

Run the compatibility test:

```bash
uv run python test_all_browsers.py
```

This will test all three browsers and report which ones work on your system.

## Switching Browsers

### Via Configuration

```python
await configure_browser({
    "browser_type": "firefox"  # chromium, firefox, webkit
})
```

### Via Environment Variable

```bash
export BROWSER_TYPE=firefox
uvx mcplaywright
```

### Via MCP Config

```bash
claude mcp add mcplaywright --env BROWSER_TYPE=firefox -- uvx mcplaywright
```

## Feature Matrix

| Feature | Chromium | Firefox | WebKit |
|---------|----------|---------|--------|
| Basic Automation | ✅ | ✅ | ✅ |
| Video Recording | ✅ | ✅ | ✅ |
| HTTP Monitoring | ✅ | ✅ | ✅ |
| Tab Management | ✅ | ✅ | ✅ |
| Console Capture | ✅ | ✅ | ✅ |
| Chrome Extensions | ✅ | ❌ | ❌ |
| Debug Toolbar | ✅ | ✅ | ✅ |
| AI Collaboration | ✅ | ✅ | ✅ |
| Custom Themes | ✅ | ✅ | ✅ |

## Platform Support Summary

| Platform | Chromium | Firefox | WebKit |
|----------|----------|---------|--------|
| Windows | ✅ | ✅ | ✅ |
| macOS | ✅ | ✅ | ✅ |
| Ubuntu 20.04 | ✅ | ✅ | ✅ |
| Ubuntu 22.04+ | ✅ | ✅ | ⚠️ |
| Arch Linux | ✅ | ✅ | ⚠️ |
| Fedora | ✅ | ✅ | ⚠️ |

## Current Test Results

```
============================================================
TEST SUMMARY
============================================================
CHROMIUM  : ✅ PASSED
FIREFOX   : ✅ PASSED
WEBKIT    : ⚠️  Platform-dependent
============================================================
```

**Recommendation**: Use Chromium (default) or Firefox for development and testing. WebKit is available for Safari-specific testing when running on compatible platforms.
