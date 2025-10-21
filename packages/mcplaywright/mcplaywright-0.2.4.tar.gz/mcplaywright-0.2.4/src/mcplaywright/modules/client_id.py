"""
Provides a Django-style debug toolbar for identifying which MCP client is controlling
the browser. This solves the problem of running multiple MCP clients in parallel.
"""

from typing import Dict, Any, Optional, List
from fastmcp.contrib.mcp_mixin import MCPMixin, mcp_tool
import json
import base64
import logging
import re
import html
from datetime import datetime

logger = logging.getLogger(__name__)

# Security: Maximum code length to prevent DoS
MAX_CODE_LENGTH = 50000  # 50KB
MAX_NAME_LENGTH = 100

# Security: Dangerous JavaScript patterns to detect
DANGEROUS_JS_PATTERNS = [
    r'\beval\s*\(',
    r'\bFunction\s*\(',
    r'__proto__',
    r'constructor\[',
    r'\.constructor\(',
    r'<script',
    r'javascript:',
    r'data:text/html',
    r'vbscript:',
    r'file://',
    r'\.innerHTML\s*=',
    r'\.outerHTML\s*=',
    r'document\.write\(',
    r'document\.writeln\(',
]

# Security: Compile patterns for performance
DANGEROUS_JS_REGEX = re.compile('|'.join(DANGEROUS_JS_PATTERNS), re.IGNORECASE)


class ClientIdentification(MCPMixin):
    """
    Provides a visual toolbar to identify which MCP client is controlling the browser,
    along with custom code injection capabilities for enhanced debugging.
    """
    
    def __init__(self):
        super().__init__()
        self.injections: Dict[str, Dict[str, Any]] = {}
        self.toolbar_enabled = False
        self.toolbar_config = {
            "position": "bottom-right",
            "theme": "dark",
            "opacity": 0.9,
            "minimized": False,
            "showDetails": True,
            "projectName": "MCPlaywright"
        }
        # Do not auto-inject anything unless explicitly requested
        self.auto_inject = False
        
    def _generate_debug_toolbar_html(self) -> str:
        """Generate the HTML for the debug toolbar with proper escaping."""
        config = self.toolbar_config

        # Generate unique session ID
        session_id = f"mcp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # HTML-escape user-supplied values to prevent XSS
        safe_session_id = html.escape(session_id, quote=True)
        safe_project_name = html.escape(config['projectName'], quote=True)

        # JavaScript-escape for console logs
        js_session_id = self._escape_js_string(session_id)
        js_project_name = self._escape_js_string(config['projectName'])

        toolbar_html = f"""
        <!-- MCP Client Debug Toolbar -->
        <div id="mcp-debug-toolbar" data-session="{safe_session_id}" style="
            position: fixed;
            {config['position'].split('-')[0]}: 20px;
            {config['position'].split('-')[1]}: 20px;
            background: {'#1a1a1a' if config['theme'] == 'dark' else '#ffffff'};
            color: {'#ffffff' if config['theme'] == 'dark' else '#000000'};
            border: 2px solid {'#4CAF50' if config['theme'] == 'dark' else '#2196F3'};
            border-radius: 8px;
            padding: 10px 15px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            z-index: 999999;
            opacity: {config['opacity']};
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            min-width: 200px;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <span style="
                        display: inline-block;
                        width: 10px;
                        height: 10px;
                        background: #4CAF50;
                        border-radius: 50%;
                        margin-right: 8px;
                        animation: mcp-pulse 2s infinite;
                    "></span>
                    <strong>{safe_project_name}</strong>
                </div>
                <button onclick="window.toggleMCPToolbar()" style="
                    background: none;
                    border: none;
                    color: inherit;
                    cursor: pointer;
                    font-size: 16px;
                    padding: 0;
                    margin-left: 10px;
                ">{'▼' if not config['minimized'] else '▲'}</button>
            </div>

            <div id="mcp-toolbar-details" style="{'display: none;' if config['minimized'] else 'display: block;'} margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2);">
                <div style="margin: 5px 0;">
                    <span style="opacity: 0.7;">Session:</span> {safe_session_id}
                </div>
                <div style="margin: 5px 0;">
                    <span style="opacity: 0.7;">Client:</span> Python MCPlaywright
                </div>
                <div style="margin: 5px 0;">
                    <span style="opacity: 0.7;">Time:</span> <span id="mcp-time">{datetime.now().strftime('%H:%M:%S')}</span>
                </div>
                <div style="margin: 5px 0;">
                    <span style="opacity: 0.7;">Injections:</span> <span id="mcp-injection-count">{len(self.injections)}</span>
                </div>
            </div>
        </div>

        <style id="mcp-toolbar-styles">
            @keyframes mcp-pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}

            #mcp-debug-toolbar:hover {{
                opacity: 1 !important;
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            }}
        </style>

        <script id="mcp-toolbar-script">
            // Store interval ID for cleanup
            if (window.mcpToolbarInterval) {{
                clearInterval(window.mcpToolbarInterval);
            }}

            window.toggleMCPToolbar = function() {{
                const details = document.getElementById('mcp-toolbar-details');
                const toolbar = document.getElementById('mcp-debug-toolbar');
                if (details && details.style.display === 'none') {{
                    details.style.display = 'block';
                    if (toolbar) toolbar.style.minWidth = '250px';
                }} else if (details) {{
                    details.style.display = 'none';
                    if (toolbar) toolbar.style.minWidth = '200px';
                }}
            }};

            // Update time every second - store interval ID for cleanup
            window.mcpToolbarInterval = setInterval(() => {{
                const timeEl = document.getElementById('mcp-time');
                if (timeEl) {{
                    timeEl.textContent = new Date().toLocaleTimeString();
                }} else {{
                    // Toolbar removed, cleanup interval
                    clearInterval(window.mcpToolbarInterval);
                    delete window.mcpToolbarInterval;
                }}
            }}, 1000);

            // Log toolbar activation
            console.log('%c🎭 MCP Client Debug Toolbar Active', 'color: #4CAF50; font-size: 14px; font-weight: bold;');
            console.log('Session: {js_session_id}');
            console.log('Client: {js_project_name}');
        </script>
        """

        return toolbar_html
    
    def _escape_js_string(self, value: str) -> str:
        """Escape string for use in JavaScript context."""
        # Escape backslashes first, then single quotes
        return value.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')

    def _wrap_for_llm_safety(self, html: str) -> str:
        """Wrap HTML in comments to prevent LLM interpretation."""
        return f"<!-- MCP_INJECTION_START -->\n{html}\n<!-- MCP_INJECTION_END -->"

    def _validate_injection_code(self, name: str, code: str, code_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate code injection for security issues.

        Returns:
            (is_valid, error_message) tuple
        """
        # Validate name
        if not name or len(name) > MAX_NAME_LENGTH:
            return False, f"Name must be 1-{MAX_NAME_LENGTH} characters"

        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False, "Name must contain only alphanumeric characters, hyphens, and underscores"

        # Validate code length
        if not code or len(code) > MAX_CODE_LENGTH:
            return False, f"Code must be 1-{MAX_CODE_LENGTH} characters ({MAX_CODE_LENGTH/1024:.0f}KB max)"

        # Validate JavaScript for dangerous patterns
        if code_type == "javascript":
            match = DANGEROUS_JS_REGEX.search(code)
            if match:
                return False, f"Code contains potentially dangerous pattern: {match.group()}"

        # Validate CSS for dangerous patterns
        elif code_type == "css":
            # Check for JavaScript in CSS (expression(), url(javascript:), etc.)
            dangerous_css_patterns = [
                r'expression\s*\(',
                r'javascript:',
                r'vbscript:',
                r'data:text/html',
                r'@import\s+["\']javascript:',
            ]
            for pattern in dangerous_css_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    return False, f"CSS contains potentially dangerous pattern: {pattern}"

        return True, None
    
    @mcp_tool(
        name="browser_enable_debug_toolbar",
        description="Enable the debug toolbar to identify which MCP client is controlling the browser"
    )
    async def enable_debug_toolbar(
        self,
        position: str = "bottom-right",
        theme: str = "dark",
        opacity: float = 0.9,
        minimized: bool = False,
        show_details: bool = True,
        project_name: str = "MCPlaywright"
    ) -> Dict[str, Any]:
        """Enable the MCP client debug toolbar."""
        try:
            # Update toolbar configuration
            self.toolbar_config.update({
                "position": position,
                "theme": theme,
                "opacity": opacity,
                "minimized": minimized,
                "showDetails": show_details,
                "projectName": project_name
            })
            
            # Generate toolbar HTML
            toolbar_html = self._generate_debug_toolbar_html()
            
            # Inject into current page
            page = await self.get_current_page()
            
            # Inject toolbar HTML
            await page.evaluate(f"""
                (() => {{
                    // Remove existing toolbar if present
                    const existing = document.getElementById('mcp-debug-toolbar');
                    if (existing) {{
                        existing.remove();
                    }}
                    
                    // Create container and inject HTML
                    const container = document.createElement('div');
                    container.innerHTML = `{toolbar_html}`;
                    document.body.appendChild(container.firstElementChild);
                    
                    return true;
                }})();
            """)
            
            self.toolbar_enabled = True
            # Enable auto-injection only when toolbar is explicitly enabled
            self.auto_inject = True

            # Store in injections
            self.injections["debug_toolbar"] = {
                "type": "toolbar",
                "name": "Debug Toolbar",
                "config": self.toolbar_config,
                "auto_inject": True,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Debug toolbar enabled: {project_name}")

            return {
                "status": "success",
                "message": "Debug toolbar enabled",
                "config": self.toolbar_config,
                "session": f"mcp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
        except Exception as e:
            logger.error(f"Error enabling debug toolbar: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @mcp_tool(
        name="browser_inject_custom_code",
        description="Inject custom JavaScript or CSS code into all pages in the current session"
    )
    async def inject_custom_code(
        self,
        name: str,
        code: str,
        type: str = "javascript",
        auto_inject: bool = True,
        persistent: bool = False
    ) -> Dict[str, Any]:
        """Inject custom JavaScript or CSS code with security validation."""
        try:
            # Validate type parameter first
            if type not in ["javascript", "css"]:
                return {
                    "status": "error",
                    "message": f"Invalid type: {type}. Must be 'javascript' or 'css'"
                }

            # Security validation
            is_valid, error_message = self._validate_injection_code(name, code, type)
            if not is_valid:
                logger.warning(f"Code injection rejected: {error_message}")
                return {
                    "status": "error",
                    "message": f"Security validation failed: {error_message}",
                    "validation_error": True
                }

            page = await self.get_current_page()

            if type == "javascript":
                # Wrap JavaScript in IIFE for safety
                wrapped_code = f"""
                    (function() {{
                        try {{
                            {code}
                            console.log('MCP Injection "{name}" executed successfully');
                        }} catch (e) {{
                            console.error('MCP Injection "{name}" error:', e);
                        }}
                    }})();
                """
                await page.evaluate(wrapped_code)
                
            elif type == "css":
                # Inject CSS via style tag
                wrapped_code = f"""
                    (() => {{
                        const style = document.createElement('style');
                        style.setAttribute('data-mcp-injection', '{name}');
                        style.textContent = `{code}`;
                        document.head.appendChild(style);
                        return true;
                    }})();
                """
                await page.evaluate(wrapped_code)

            # Store injection for persistence
            self.injections[name] = {
                "name": name,
                "type": type,
                "code": code,
                "auto_inject": auto_inject,
                "persistent": persistent,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Custom {type} injection '{name}' applied")
            
            return {
                "status": "success",
                "message": f"Custom {type} injected successfully",
                "name": name,
                "auto_inject": auto_inject,
                "injection_count": len(self.injections)
            }
            
        except Exception as e:
            logger.error(f"Error injecting custom code: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @mcp_tool(
        name="browser_list_injections",
        description="List all active code injections for the current session",
        annotations={"readOnlyHint": True}
    )
    async def list_injections(self) -> Dict[str, Any]:
        """List all active code injections."""
        try:
            injection_list = []
            
            for key, injection in self.injections.items():
                injection_list.append({
                    "key": key,
                    "name": injection.get("name"),
                    "type": injection.get("type"),
                    "auto_inject": injection.get("auto_inject", False),
                    "persistent": injection.get("persistent", False),
                    "timestamp": injection.get("timestamp")
                })
            
            return {
                "status": "success",
                "toolbar_enabled": self.toolbar_enabled,
                "injection_count": len(injection_list),
                "injections": injection_list
            }
            
        except Exception as e:
            logger.error(f"Error listing injections: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @mcp_tool(
        name="browser_disable_debug_toolbar",
        description="Disable the debug toolbar for the current session"
    )
    async def disable_debug_toolbar(self) -> Dict[str, Any]:
        """Disable the debug toolbar."""
        try:
            page = await self.get_current_page()

            # Remove toolbar and all associated elements from page
            removed = await page.evaluate("""
                (() => {
                    let removedItems = [];

                    // Clear the interval timer
                    if (window.mcpToolbarInterval) {
                        clearInterval(window.mcpToolbarInterval);
                        delete window.mcpToolbarInterval;
                        removedItems.push('interval');
                    }

                    // Remove toolbar div
                    const toolbar = document.getElementById('mcp-debug-toolbar');
                    if (toolbar) {
                        toolbar.remove();
                        removedItems.push('toolbar');
                    }

                    // Remove styles
                    const styles = document.getElementById('mcp-toolbar-styles');
                    if (styles) {
                        styles.remove();
                        removedItems.push('styles');
                    }

                    // Remove script
                    const script = document.getElementById('mcp-toolbar-script');
                    if (script) {
                        script.remove();
                        removedItems.push('script');
                    }

                    // Clean up global function
                    if (window.toggleMCPToolbar) {
                        delete window.toggleMCPToolbar;
                        removedItems.push('toggle-function');
                    }

                    // Log cleanup
                    console.log('🎭 MCP Debug Toolbar cleaned up:', removedItems);

                    return {
                        removed: removedItems,
                        success: removedItems.length > 0
                    };
                })();
            """)

            # Remove from injections
            if "debug_toolbar" in self.injections:
                del self.injections["debug_toolbar"]

            self.toolbar_enabled = False
            # Disable auto-injection when toolbar is disabled
            self.auto_inject = False

            logger.info(f"Debug toolbar disabled - cleaned up: {removed.get('removed', [])}")

            return {
                "status": "success",
                "message": "Debug toolbar disabled and cleaned up",
                "cleaned_items": removed.get('removed', [])
            }

        except Exception as e:
            logger.error(f"Error disabling debug toolbar: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @mcp_tool(
        name="browser_clear_injections",
        description="Remove all custom code injections (keeps debug toolbar)"
    )
    async def clear_injections(
        self,
        include_toolbar: bool = False
    ) -> Dict[str, Any]:
        """Clear all code injections."""
        try:
            page = await self.get_current_page()
            
            # Remove all injection elements from page
            await page.evaluate("""
                (() => {
                    // Remove injected styles
                    const styles = document.querySelectorAll('style[data-mcp-injection]');
                    styles.forEach(s => s.remove());
                    
                    // Log cleanup
                    console.log('MCP injections cleared');
                    
                    return styles.length;
                })();
            """)
            
            # Clear injection registry
            cleared_count = 0
            keys_to_remove = []
            
            for key in self.injections.keys():
                if key != "debug_toolbar" or include_toolbar:
                    keys_to_remove.append(key)
                    cleared_count += 1
            
            for key in keys_to_remove:
                del self.injections[key]
            
            if include_toolbar:
                await self.disable_debug_toolbar()
            
            logger.info(f"Cleared {cleared_count} injections")
            
            return {
                "status": "success",
                "message": f"Cleared {cleared_count} injections",
                "remaining": len(self.injections)
            }
            
        except Exception as e:
            logger.error(f"Error clearing injections: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _auto_inject_on_navigation(self, page):
        """Automatically inject persistent code on new pages."""
        if not self.auto_inject:
            return
        
        for injection in self.injections.values():
            if injection.get("auto_inject", False):
                if injection["type"] == "toolbar":
                    # Re-inject toolbar
                    toolbar_html = self._generate_debug_toolbar_html()
                    await page.evaluate(f"""
                        (() => {{
                            const container = document.createElement('div');
                            container.innerHTML = `{toolbar_html}`;
                            document.body.appendChild(container.firstElementChild);
                        }})();
                    """)
                elif injection["type"] == "javascript":
                    await page.evaluate(injection["code"])
                elif injection["type"] == "css":
                    await page.evaluate(f"""
                        (() => {{
                            const style = document.createElement('style');
                            style.setAttribute('data-mcp-injection', '{injection["name"]}');
                            style.textContent = `{injection["code"]}`;
                            document.head.appendChild(style);
                        }})();
                    """)
        
        logger.info(f"Auto-injected {len(self.injections)} items on new page")
