# Changelog

All notable changes to MCPlaywright will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.6] - 2025-01-21

### Fixed

- **BREAKING CHANGE**: Removed custom user agent to prevent bot detection and rendering issues
  - Default user agent changed from `MCPlaywright/1.0 (FastMCP)` to Playwright's default (Chrome-like UA)
  - Fixes broken page rendering on websites with bot detection (e-commerce, social media, etc.)
  - Pages now render correctly without requiring DevTools reflow workaround
  - Custom user agents can still be configured via `browser_configure()` when needed

### Added

- User agent configuration support in `browser_configure()` tool
- Comprehensive bot detection documentation (`docs/guides/BOT_DETECTION_FIX.md`)
- Automated test for user agent behavior (`test_bot_detection_fix.py`)
- Visual comparison test for rendering differences (`test_user_agent_rendering.py`)

### Changed

- Browser context now uses Playwright's default user agent instead of custom identification
- User agent is now configurable and optional (None = use Playwright default)

### Documentation

- Added migration guide for projects relying on bot detection behavior
- Added best practices for user agent configuration
- Added examples for mobile device and search engine crawler emulation

## [0.2.5] - 2025-01-20

### Added

- MCP parameter troubleshooting documentation (`docs/TROUBLESHOOTING_MCP_PARAMETERS.md`)
- Diagnostic tools for MCP client parameter validation
- Comprehensive Firefox RDP DevTools support with geckordp integration
- Firefox addon management via Remote Debugging Protocol
- Multi-browser testing validation (Chromium, Firefox, WebKit)
- Browser compatibility documentation (`BROWSER_SUPPORT.md`)

### Changed

- Updated FastMCP dependency to 2.12.5 for improved parameter parsing
- Toned down marketing language in README for professional tone

### Fixed

- Verified MCP tool schemas are correct (parameter errors are client-side issues)
- Firefox RDP connection isolation with temporary profiles
- Firefox security prompt bypass for automated testing

## [0.2.4] - 2025-01-19

### Added

- Critical security and performance improvements
- Context API fixes for tab management
- Validation tests for tab operations

### Changed

- Default to headed mode for better visibility and debugging
- Corrected entry point from app to main in pyproject.toml

## [0.2.3] - 2025-01-18

### Added

- Comprehensive README update with all features and recent improvements
- 40+ tool listings across 10 categories
- Recent improvements section (v0.2.4-v0.2.5)
- Updated revolutionary features from 12 to 17 items

## [0.2.2] - 2025-01-17

### Added

- Version bump with comprehensive server and minimal variant
- Enhanced module architecture

## [0.2.1] - 2025-01-16

### Added

- Initial FastMCP 2.0 implementation
- Core browser automation tools
- Video recording system
- HTTP request monitoring
- Debug toolbar and client identification

---

## Upgrade Guide

### From 0.2.5 to 0.2.6

**Breaking Change**: Default user agent behavior changed.

**Impact**: Pages will now render correctly by default, avoiding bot detection.

**Action Required**:
- **Most projects**: No action needed - pages will render better automatically
- **If you rely on bot detection**: Explicitly set custom user agent:
  ```python
  await browser_configure(user_agent="MCPlaywright/1.0 (FastMCP)")
  ```

**Benefits**:
- ✅ Accurate testing of real user experience
- ✅ Proper page rendering without DevTools workaround
- ✅ Avoid bot detection on e-commerce and social media sites
- ✅ Consistent behavior across page loads

See [`docs/guides/BOT_DETECTION_FIX.md`](docs/guides/BOT_DETECTION_FIX.md) for detailed migration guide.
