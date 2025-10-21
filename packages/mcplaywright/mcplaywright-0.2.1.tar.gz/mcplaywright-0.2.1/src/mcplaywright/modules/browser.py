"""
Browser Management Mixin for MCPlaywright

Provides core browser lifecycle management capabilities.
"""

from typing import Dict, Any, Optional, List
from fastmcp.contrib.mcp_mixin import MCPMixin, mcp_tool
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, ConsoleMessage as PlaywrightConsoleMessage
import logging

from ..models.console import ConsoleMessage, ConsoleMessageLocation

logger = logging.getLogger(__name__)


class BrowserCore(MCPMixin):
    """
    Mixin for browser management operations.
    
    Handles browser lifecycle, context creation, and page management.
    """
    
    def __init__(self):
        super().__init__()
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._current_page: Optional[Page] = None
        self._pages: List[Page] = []
        self._browser_type = "chromium"
        self._headless = True
        self._viewport = {"width": 1280, "height": 720}
        # Persistent console message storage
        self._console_messages: List[ConsoleMessage] = []
        
    async def ensure_browser_context(self) -> BrowserContext:
        """Ensure browser context is initialized."""
        if not self._context:
            await self._create_browser_context()
        return self._context
    
    async def _create_browser_context(self):
        """Create a new browser context with current configuration."""
        if not self._playwright:
            self._playwright = await async_playwright().start()
        
        # Close existing browser if any
        if self._browser:
            await self._browser.close()
        
        # Launch browser based on type
        browser_launcher = getattr(self._playwright, self._browser_type)
        self._browser = await browser_launcher.launch(
            headless=self._headless,
            args=["--no-sandbox", "--disable-setuid-sandbox"] if self._headless else []
        )
        
        # Create context with viewport
        self._context = await self._browser.new_context(
            viewport=self._viewport,
            user_agent="MCPlaywright/1.0 (FastMCP)"
        )
        
        # Create initial page
        self._current_page = await self._context.new_page()
        self._pages = [self._current_page]

        # Set up persistent console message listener
        self._setup_console_listener(self._current_page)

        logger.info(f"Browser context created: {self._browser_type}, headless={self._headless}")
    
    async def get_current_page(self) -> Page:
        """Get the current active page."""
        if not self._current_page:
            await self.ensure_browser_context()
        return self._current_page

    def _setup_console_listener(self, page: Page):
        """Set up persistent console message listener for a page."""
        def handle_console(msg: PlaywrightConsoleMessage):
            """Handle console message and store it."""
            try:
                # Convert Playwright console message to our structured model
                console_msg = ConsoleMessage(
                    type=msg.type,
                    text=msg.text,
                    location=ConsoleMessageLocation(
                        url=msg.location.get("url", ""),
                        line_number=msg.location.get("lineNumber", 0),
                        column_number=msg.location.get("columnNumber", 0)
                    ),
                    args_count=len(msg.args)
                )
                self._console_messages.append(console_msg)
                logger.debug(f"Console message captured: [{console_msg.type}] {console_msg.text[:50]}...")
            except Exception as e:
                logger.error(f"Error capturing console message: {e}")

        # Attach console listener to page
        page.on("console", handle_console)
        logger.debug(f"Console listener attached to page")

    def clear_console_messages(self):
        """Clear all stored console messages."""
        count = len(self._console_messages)
        self._console_messages.clear()
        logger.info(f"Cleared {count} console messages")
        return count

    @mcp_tool(
        name="browser_close",
        description="Close the browser and clean up resources"
    )
    async def close_browser(self) -> Dict[str, Any]:
        """Close browser and cleanup resources."""
        try:
            if self._context:
                await self._context.close()
                self._context = None
            
            if self._browser:
                await self._browser.close()
                self._browser = None
            
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            
            self._current_page = None
            self._pages = []
            
            return {
                "status": "success",
                "message": "Browser closed successfully"
            }
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @mcp_tool(
        name="browser_configure",
        description="Configure browser settings (headless mode, viewport, browser type)"
    )
    async def configure_browser(
        self,
        browser_type: Optional[str] = None,
        headless: Optional[bool] = None,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Configure browser settings and restart with new configuration."""
        try:
            # Update configuration
            if browser_type and browser_type in ["chromium", "firefox", "webkit"]:
                self._browser_type = browser_type
            
            if headless is not None:
                self._headless = headless
            
            if viewport:
                self._viewport = viewport
            
            # Restart browser with new configuration
            await self.close_browser()
            await self.ensure_browser_context()
            
            return {
                "status": "success",
                "configuration": {
                    "browser_type": self._browser_type,
                    "headless": self._headless,
                    "viewport": self._viewport
                }
            }
        except Exception as e:
            logger.error(f"Error configuring browser: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @mcp_tool(
        name="browser_snapshot",
        description="Get a complete accessibility snapshot of the current page",
        annotations={"readOnlyHint": True}
    )
    async def get_page_snapshot(self) -> Dict[str, Any]:
        """Get accessibility snapshot of current page."""
        try:
            page = await self.get_current_page()
            
            # Get page info
            url = page.url
            title = await page.title()
            
            # Get accessibility tree
            accessibility_tree = await page.accessibility.snapshot()
            
            return {
                "status": "success",
                "url": url,
                "title": title,
                "snapshot": accessibility_tree
            }
        except Exception as e:
            logger.error(f"Error getting page snapshot: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @mcp_tool(
        name="browser_console_messages",
        description="Get console messages with filtering support. Filters: type (log/error/warning/info), search text, limit",
        annotations={"readOnlyHint": True}
    )
    async def get_console_messages(
        self,
        type_filter: str = "all",
        search: str = "",
        limit: int = 100,
        clear_after: bool = False
    ) -> Dict[str, Any]:
        """
        Get console messages from persistent storage with filtering.

        Args:
            type_filter: Filter by message type (all, log, error, warning, info, debug)
            search: Search term to filter messages (case-insensitive)
            limit: Maximum number of messages to return
            clear_after: Clear console messages after retrieving them

        Returns:
            Dict with status, messages list, and count
        """
        try:
            # Ensure browser is initialized
            await self.get_current_page()

            # Apply filters
            filtered_messages = [
                msg for msg in self._console_messages
                if msg.matches_type(type_filter) and msg.matches_search(search)
            ]

            # Limit results
            limited_messages = filtered_messages[-limit:] if limit > 0 else filtered_messages

            # Format messages for output
            formatted_messages = [
                {
                    "type": msg.type,
                    "text": msg.text,
                    "location": {
                        "url": msg.location.url,
                        "line": msg.location.line_number,
                        "column": msg.location.column_number
                    },
                    "timestamp": msg.timestamp.isoformat(),
                    "formatted": str(msg)
                }
                for msg in limited_messages
            ]

            # Optionally clear messages after retrieval
            if clear_after:
                self.clear_console_messages()

            return {
                "status": "success",
                "messages": formatted_messages,
                "count": len(formatted_messages),
                "total_captured": len(self._console_messages),
                "filtered_count": len(filtered_messages),
                "filters_applied": {
                    "type": type_filter,
                    "search": search if search else None,
                    "limit": limit
                },
                "cleared": clear_after
            }
        except Exception as e:
            logger.error(f"Error getting console messages: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    @mcp_tool(
        name="browser_clear_console",
        description="Clear all stored console messages"
    )
    async def clear_console(self) -> Dict[str, Any]:
        """Clear all console messages from storage."""
        try:
            count = self.clear_console_messages()
            return {
                "status": "success",
                "message": f"Cleared {count} console messages",
                "cleared_count": count
            }
        except Exception as e:
            logger.error(f"Error clearing console: {e}")
            return {
                "status": "error",
                "message": str(e)
            }