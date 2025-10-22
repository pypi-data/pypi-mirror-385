# Bot Detection Fix - User Agent Configuration

## Issue Summary

**Symptom**: Websites rendered incorrectly or with broken layouts when accessed through MCPlaywright, but worked correctly when DevTools was opened.

**Root Cause**: MCPlaywright v0.2.5 and earlier used a custom user agent string (`MCPlaywright/1.0 (FastMCP)`) that triggered bot detection mechanisms on many websites, causing them to serve simplified/broken layouts designed for crawlers.

**Fix Version**: v0.2.6+

## Technical Details

### What Was Happening

1. **Custom User Agent**: Earlier versions set a custom user agent identifying itself as MCPlaywright:
   ```python
   # Old behavior (v0.2.5 and earlier)
   user_agent="MCPlaywright/1.0 (FastMCP)"
   ```

2. **Bot Detection**: Websites use user agent strings to detect automation tools and web scrapers
3. **Different Content**: Many sites serve simplified HTML/CSS to detected bots to:
   - Reduce bandwidth costs
   - Prevent scraping
   - Deter automated access
4. **Layout Breaks**: The simplified content often lacks proper styling and structure

### Why DevTools Fixed It

When you opened DevTools (F12), the browser forced a **layout reflow** (recalculation of page layout). This:
- Re-evaluated CSS media queries
- Triggered lazy-loaded stylesheets
- Forced JavaScript to re-execute layout code
- Temporarily "fixed" the broken layout

However, this didn't solve the underlying issue - the site was still serving bot-optimized content.

## The Fix

### Default Behavior (v0.2.6+)

MCPlaywright now uses Playwright's default user agent, which mimics a real Chrome browser:

```python
# New behavior (v0.2.6+)
# No custom user_agent specified - uses Playwright default
self._context = await self._browser.new_context(
    viewport=self._viewport
    # user_agent NOT specified - uses standard Chrome UA
)
```

**Default User Agent Example**:
```
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
```

### Benefits

✅ **Avoids bot detection** - Sites treat MCPlaywright like a real browser
✅ **Proper page rendering** - Full CSS and JavaScript delivered
✅ **Consistent behavior** - Same content as manual browsing
✅ **Better testing accuracy** - Tests reflect real user experience

### Custom User Agent (Optional)

If you need a custom user agent for specific testing scenarios, you can still configure it:

```python
# Configure custom user agent
await browser_configure(user_agent="MyTestBot/1.0")

# Reset to default (Chrome-like)
await browser_configure(user_agent="")  # Empty string = use default
```

## Impact on Existing Projects

### Breaking Change

**Yes** - This is a behavior change that may affect existing automation:

- **Before**: Sites detected MCPlaywright as a bot
- **After**: Sites treat MCPlaywright as a real browser

### Migration Guide

Most projects will **benefit** from this change without any modifications. However, if your automation specifically relies on bot detection behavior:

1. **Option 1**: Update your tests to work with full page rendering
2. **Option 2**: Explicitly set custom user agent via `browser_configure()`

```python
# If you specifically need bot detection behavior
await browser_configure(user_agent="MCPlaywright/1.0 (FastMCP)")
```

## Affected Websites

Websites commonly using bot detection:

- E-commerce sites (anti-scraping protection)
- Social media platforms (anti-automation)
- Price comparison sites (prevent competitor scraping)
- Real estate listings (data protection)
- Job boards (content protection)
- News sites (paywall enforcement)

## Testing

### Verify the Fix

Run the test suite to verify proper user agent handling:

```bash
uv run python test_bot_detection_fix.py
```

**Expected Output**:
```
✅ PASS: Using standard Chrome-like user agent
   This should avoid bot detection issues.
```

### Visual Testing

To visually compare rendering:

1. **Before Fix** (force old behavior):
   ```python
   await browser_configure(user_agent="MCPlaywright/1.0 (FastMCP)")
   await page.goto("https://example-site.com")
   # May show broken layout
   ```

2. **After Fix** (default behavior):
   ```python
   # No configuration needed
   await page.goto("https://example-site.com")
   # Should render correctly
   ```

## Related Issues

- **Issue #1**: UPC LLC product page rendering broken ✅ **FIXED**
- **Issue #2**: Images not loading on e-commerce sites ✅ **FIXED**
- **Issue #3**: CSS not applying correctly ✅ **FIXED**

## Best Practices

### For General Automation

**Use default user agent** (no configuration needed):
```python
# Just navigate - default UA will work
await page.goto("https://example.com")
```

### For Bot Testing

**Explicitly set custom user agent** to test bot detection:
```python
await browser_configure(user_agent="Googlebot/2.1")
# Test how your site handles search engine crawlers
```

### For Specific Browser Emulation

**Match target browser exactly**:
```python
# Emulate mobile Chrome
await browser_configure(
    user_agent="Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36"
)
```

## Configuration Reference

### browser_configure Parameters

```python
await browser_configure(
    browser_type: Optional[str] = None,      # "chromium", "firefox", "webkit"
    headless: Optional[bool] = None,         # True/False
    viewport: Optional[Dict[str, int]] = None,  # {"width": 1920, "height": 1080}
    user_agent: Optional[str] = None         # Custom UA string (None = default)
)
```

### User Agent Examples

**Default (Recommended)**:
```python
user_agent=None  # Playwright's default Chrome UA
```

**Mobile Device**:
```python
user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
```

**Search Engine Crawler**:
```python
user_agent="Googlebot/2.1 (+http://www.google.com/bot.html)"
```

**Custom Bot** (triggers detection):
```python
user_agent="MyBot/1.0 (Custom Automation)"
```

## Summary

The bot detection fix ensures MCPlaywright behaves like a real browser by default, providing accurate testing and avoiding content discrimination. Custom user agents remain available for specific testing scenarios.

**Key Takeaway**: No action needed for most projects - pages will now render correctly automatically.
