"""
Firefox Extension Management Module

Provides tools for installing and managing Firefox addons using the Remote Debugging Protocol.
Unlike Chromium's command-line approach, Firefox requires connecting via RDP to install addons dynamically.

Key differences from Chromium:
- Uses geckordp library for RDP communication
- Launches Firefox with --start-debugger-server flag
- Installs addons via AddonsActor after browser is running
- Supports .xpi (Firefox addon) format
"""

from typing import Dict, Any, Optional, List, Tuple
from fastmcp.contrib.mcp_mixin import MCPMixin, mcp_tool
from pathlib import Path
import logging
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class FirefoxExtensionManagement(MCPMixin):
    """
    Manages Firefox addons using the Remote Debugging Protocol.

    Features:
    - Dynamic addon installation via RDP
    - Support for temporary addons (no signing required)
    - Integration with Mozilla Addons (AMO) catalog
    - Automatic debugger server management
    """

    # Popular Firefox addons from addons.mozilla.org
    POPULAR_ADDONS = {
        "ublock-origin": {
            "name": "uBlock Origin",
            "id": "uBlock0@raymondhill.net",
            "description": "Efficient ad blocker with low memory footprint",
            "type": "privacy",
            "amo_id": "ublock-origin",
            "url": "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi"
        },
        "react-devtools": {
            "name": "React Developer Tools",
            "id": "@react-devtools",
            "description": "Inspect React component hierarchies",
            "type": "developer",
            "amo_id": "react-devtools",
            "url": "https://addons.mozilla.org/firefox/downloads/latest/react-devtools/latest.xpi"
        },
        "vue-devtools": {
            "name": "Vue.js devtools",
            "id": "{5caff8cc-3d2e-4110-a88a-003cc85b3858}",
            "description": "Inspect Vue.js applications",
            "type": "developer",
            "amo_id": "vue-js-devtools"
        },
        "redux-devtools": {
            "name": "Redux DevTools",
            "id": "extension@redux.devtools",
            "description": "Debug Redux state changes",
            "type": "developer",
            "amo_id": "reduxdevtools"
        },
        "axe-devtools": {
            "name": "axe DevTools",
            "id": "@axe-devtools",
            "description": "Accessibility testing and analysis",
            "type": "accessibility",
            "amo_id": "axe-devtools"
        },
        "jsonview": {
            "name": "JSONView",
            "id": "jsonview@brh.numbera.com",
            "description": "Format and view JSON documents",
            "type": "utility",
            "amo_id": "jsonview"
        },
        "web-developer": {
            "name": "Web Developer",
            "id": "{c45c406e-ab73-11d8-be73-000a95be3b12}",
            "description": "Various web developer tools",
            "type": "developer",
            "amo_id": "web-developer"
        },
        "colorzilla": {
            "name": "ColorZilla",
            "id": "{6AC85730-7D0F-4de0-B3FA-21142DD85326}",
            "description": "Advanced color picker and eyedropper",
            "type": "design",
            "amo_id": "colorzilla"
        },
        "whatfont": {
            "name": "WhatFont",
            "id": "whatfont@chengyinliu.com",
            "description": "Identify fonts on web pages",
            "type": "design",
            "amo_id": "whatfont"
        }
    }

    def __init__(self):
        super().__init__()
        self._rdp_client = None
        self._rdp_port = None
        self._installed_addons: Dict[str, Dict[str, Any]] = {}

    async def _ensure_geckordp(self):
        """Ensure geckordp is available"""
        try:
            import geckordp
            return True
        except ImportError:
            logger.error("geckordp library not installed. Install with: pip install geckordp")
            return False

    async def _ensure_rdp_connection(self, port: int = 6000) -> Tuple[bool, Optional[str]]:
        """
        Ensure RDP connection to Firefox debugging server.

        Returns:
            Tuple of (success, error_message)
        """
        if not await self._ensure_geckordp():
            return False, "geckordp library not installed"

        try:
            from geckordp.rdp_client import RDPClient
            from geckordp.actors.root import RootActor

            if self._rdp_client is None:
                self._rdp_client = RDPClient()
                self._rdp_client.connect("localhost", port)
                self._rdp_port = port

                # Initialize root actor
                root = RootActor(self._rdp_client)
                root.get_root()

                logger.info(f"Connected to Firefox RDP server on port {port}")

            return True, None

        except Exception as e:
            logger.error(f"Failed to connect to Firefox RDP: {e}")
            return False, str(e)

    def _validate_firefox_browser(self) -> Tuple[bool, str]:
        """
        Validate that Firefox browser is being used.

        Returns:
            Tuple of (is_valid, warning_message)
        """
        if hasattr(self, '_browser_type') and self._browser_type != 'firefox':
            return False, (
                "Firefox addons are only supported with Firefox browser. "
                "Use browser_configure to switch to firefox."
            )
        return True, ""

    @mcp_tool(
        name="browser_install_firefox_addon",
        description="Install a Firefox addon from local path (.xpi file)"
    )
    async def install_addon(
        self,
        path: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Install a Firefox addon from a local .xpi file.

        Args:
            path: Path to the .xpi addon file
            name: Optional custom name for the addon

        Returns:
            Dict with installation status and addon details
        """
        try:
            # Validate Firefox browser
            is_valid, warning = self._validate_firefox_browser()
            if not is_valid:
                return {
                    "success": False,
                    "error": warning,
                    "timestamp": datetime.now().isoformat()
                }

            addon_path = Path(path)
            if not addon_path.exists():
                return {
                    "success": False,
                    "error": f"Addon file not found: {path}",
                    "timestamp": datetime.now().isoformat()
                }

            if addon_path.suffix != '.xpi':
                return {
                    "success": False,
                    "error": "Firefox addons must be .xpi files",
                    "timestamp": datetime.now().isoformat()
                }

            # Ensure RDP connection
            success, error = await self._ensure_rdp_connection()
            if not success:
                return {
                    "success": False,
                    "error": f"RDP connection failed: {error}",
                    "timestamp": datetime.now().isoformat()
                }

            # Install addon via RDP
            from geckordp.actors.root import RootActor
            from geckordp.actors.addon.addons import AddonsActor

            root = RootActor(self._rdp_client)
            root_ids = root.get_root()

            addons_actor = AddonsActor(self._rdp_client, root_ids["addonsActor"])
            response = addons_actor.install_temporary_addon(str(addon_path))

            addon_id = response.get("id")
            if addon_id:
                addon_name = name or addon_path.stem
                self._installed_addons[addon_id] = {
                    "id": addon_id,
                    "name": addon_name,
                    "path": str(addon_path),
                    "installed_at": datetime.now().isoformat()
                }

                logger.info(f"Installed Firefox addon: {addon_name} ({addon_id})")

                return {
                    "success": True,
                    "addon_id": addon_id,
                    "addon_name": addon_name,
                    "path": str(addon_path),
                    "message": f"Firefox addon '{addon_name}' installed successfully",
                    "installed_addons": len(self._installed_addons),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Addon installation failed - no ID returned",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Failed to install Firefox addon: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    @mcp_tool(
        name="browser_list_firefox_addons",
        description="List all installed Firefox addons"
    )
    async def list_addons(self) -> Dict[str, Any]:
        """List all currently installed Firefox addons"""
        return {
            "success": True,
            "addon_count": len(self._installed_addons),
            "addons": list(self._installed_addons.values()),
            "rdp_connected": self._rdp_client is not None,
            "rdp_port": self._rdp_port,
            "timestamp": datetime.now().isoformat()
        }

    @mcp_tool(
        name="browser_install_popular_firefox_addon",
        description="Install a popular Firefox addon by name (e.g., 'ublock-origin', 'react-devtools')"
    )
    async def install_popular_addon(
        self,
        addon: str
    ) -> Dict[str, Any]:
        """
        Install a popular Firefox addon from the catalog.

        Args:
            addon: Addon identifier (e.g., 'ublock-origin', 'react-devtools')

        Returns:
            Dict with installation status
        """
        addon_lower = addon.lower()
        if addon_lower not in self.POPULAR_ADDONS:
            available = ", ".join(sorted(self.POPULAR_ADDONS.keys()))
            return {
                "success": False,
                "error": f"Addon '{addon}' not found in catalog",
                "available_addons": available,
                "timestamp": datetime.now().isoformat()
            }

        addon_info = self.POPULAR_ADDONS[addon_lower]

        return {
            "success": False,
            "error": "Automatic download from AMO not yet implemented",
            "addon_info": addon_info,
            "message": f"Download {addon_info['name']} from: {addon_info.get('url', 'addons.mozilla.org')}",
            "note": "Use browser_install_firefox_addon() with downloaded .xpi file",
            "timestamp": datetime.now().isoformat()
        }

    async def cleanup_rdp(self):
        """Cleanup RDP connection"""
        if self._rdp_client:
            try:
                self._rdp_client.disconnect()
                logger.info("Disconnected from Firefox RDP server")
            except Exception as e:
                logger.warning(f"Error disconnecting from RDP: {e}")
            finally:
                self._rdp_client = None
                self._rdp_port = None
