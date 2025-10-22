"""
Firefox DevTools Implementation for MCPlaywright

Provides Firefox Remote Debugging Protocol (RDP) access for advanced debugging,
JavaScript evaluation, breakpoint management, console capture, and DOM inspection.

Parallel to Chromium CDP implementation but uses geckordp for Firefox.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from ..state.devtools_state import get_devtools_state
from ..session_manager import get_session_manager

logger = logging.getLogger(__name__)


# Parameter models for Firefox DevTools tools
class FirefoxDevToolsEnableParams(BaseModel):
    session_id: Optional[str] = Field(
        None,
        description="Session ID (if not provided, uses current session)"
    )
    rdp_port: int = Field(
        6000,
        description="Remote Debugging Protocol port (default: 6000)"
    )


class FirefoxDevToolsDisableParams(BaseModel):
    session_id: Optional[str] = Field(
        None,
        description="Session ID (if not provided, uses current session)"
    )


class FirefoxEvaluateJSParams(BaseModel):
    expression: str = Field(description="JavaScript expression to evaluate")
    session_id: Optional[str] = Field(
        None,
        description="Session ID (if not provided, uses current session)"
    )
    eager: bool = Field(
        False,
        description="Eager evaluation (returns immediately)"
    )


class FirefoxSetBreakpointParams(BaseModel):
    url: str = Field(description="URL of the script to set breakpoint in")
    line_number: int = Field(description="Line number (1-based) to set breakpoint")
    column_number: Optional[int] = Field(None, description="Column number (0-based)")
    condition: Optional[str] = Field(None, description="Conditional breakpoint expression")
    session_id: Optional[str] = Field(
        None,
        description="Session ID (if not provided, uses current session)"
    )


class FirefoxResumeParams(BaseModel):
    action: str = Field(
        description="Resume action: 'none', 'next', 'step', 'finish'"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID (if not provided, uses current session)"
    )


class FirefoxGetConsoleLogsParams(BaseModel):
    session_id: Optional[str] = Field(
        None,
        description="Session ID (if not provided, uses current session)"
    )
    message_types: List[str] = Field(
        default=["PageError", "ConsoleAPI"],
        description="Message types to retrieve"
    )


class FirefoxInspectDOMParams(BaseModel):
    selector: Optional[str] = Field(None, description="CSS selector to inspect specific element")
    session_id: Optional[str] = Field(
        None,
        description="Session ID (if not provided, uses current session)"
    )


# Firefox DevTools tool implementations
async def browser_firefox_dev_tools_enable(params: FirefoxDevToolsEnableParams) -> Dict[str, Any]:
    """
    Enable Firefox DevTools for advanced debugging and inspection via RDP.

    This will make the following tools available:
    • browser_firefox_dev_tools_disable - Return to normal browsing mode
    • browser_firefox_evaluate_js - Execute JavaScript with full runtime access
    • browser_firefox_set_breakpoint - Set JavaScript breakpoints with conditional support
    • browser_firefox_resume_execution - Control execution (next, step, finish)
    • browser_firefox_get_console_logs - Capture console messages and errors
    • browser_firefox_inspect_dom - Examine DOM structure and properties

    Use cases: Debug JavaScript errors, analyze page behavior, inspect page structure,
    monitor console output, advanced Firefox-specific testing automation.

    Note: Requires Firefox launched with --start-debugger-server flag.
    WARNING: DevTools access provides powerful debugging capabilities. Use responsibly.
    """
    try:
        # Check if geckordp is available
        try:
            from geckordp.rdp_client import RDPClient
            from geckordp.actors.root import RootActor
        except ImportError:
            return {
                "status": "error",
                "message": "geckordp library not installed",
                "hint": "Install with: pip install 'mcplaywright[firefox]' or pip install geckordp"
            }

        session_manager = get_session_manager()
        if not session_manager:
            return {
                "status": "error",
                "message": "Session manager not available"
            }

        # Get session ID
        session_id = params.session_id
        if not session_id:
            # Try to get default session
            sessions = await session_manager.list_sessions()
            if sessions:
                session_id = sessions[0]["session_id"]
            else:
                return {
                    "status": "error",
                    "message": "No active session found. Configure browser first.",
                    "hint": "Use 'browser_configure' to create a session"
                }

        # Get session to verify it exists
        session = await session_manager.get_session(session_id)
        if not session:
            return {
                "status": "error",
                "message": f"Session {session_id} not found"
            }

        # Verify browser is Firefox
        if session.config.browser_type.value != "firefox":
            return {
                "status": "error",
                "message": "Firefox DevTools only works with Firefox browser",
                "current_browser": session.config.browser_type.value,
                "hint": "Use 'browser_configure' with browser_type='firefox'"
            }

        # Enable DevTools for this session
        devtools_state = get_devtools_state()
        devtools_state.enable_for_session(session_id)

        # Connect to Firefox RDP
        rdp_client = RDPClient()
        try:
            rdp_client.connect("localhost", params.rdp_port)
        except Exception as e:
            devtools_state.disable_for_session(session_id)
            return {
                "status": "error",
                "message": f"Failed to connect to Firefox RDP server on port {params.rdp_port}",
                "error": str(e),
                "hint": "Firefox must be launched with --start-debugger-server flag"
            }

        # Get root actor
        try:
            root = RootActor(rdp_client)
            root_ids = root.get_root()

            if not root_ids:
                rdp_client.disconnect()
                devtools_state.disable_for_session(session_id)
                return {
                    "status": "error",
                    "message": "Failed to initialize Firefox RDP root actor"
                }

            # Store RDP connection in session context for reuse
            session.context._rdp_client = rdp_client
            session.context._rdp_root_ids = root_ids
            session.context._rdp_port = params.rdp_port

            logger.info(f"Firefox DevTools enabled for session: {session_id} on port {params.rdp_port}")

            return {
                "status": "success",
                "message": "Firefox DevTools enabled successfully",
                "session_id": session_id,
                "rdp_port": params.rdp_port,
                "enabled_tools": [
                    "browser_firefox_dev_tools_disable",
                    "browser_firefox_evaluate_js",
                    "browser_firefox_set_breakpoint",
                    "browser_firefox_resume_execution",
                    "browser_firefox_get_console_logs",
                    "browser_firefox_inspect_dom"
                ],
                "available_actors": list(root_ids.keys())[:10],  # First 10 actors
                "next_steps": [
                    "Use 'browser_firefox_evaluate_js' to execute JavaScript",
                    "Use 'browser_firefox_get_console_logs' to monitor console output",
                    "Use 'browser_firefox_inspect_dom' to examine page structure"
                ]
            }

        except Exception as e:
            rdp_client.disconnect()
            devtools_state.disable_for_session(session_id)
            logger.error(f"Failed to initialize Firefox RDP: {e}")
            return {
                "status": "error",
                "message": f"Failed to initialize Firefox RDP: {str(e)}"
            }

    except Exception as e:
        logger.error(f"Failed to enable Firefox DevTools: {e}")
        return {
            "status": "error",
            "message": f"Failed to enable Firefox DevTools: {str(e)}"
        }


async def browser_firefox_dev_tools_disable(params: FirefoxDevToolsDisableParams) -> Dict[str, Any]:
    """
    Disable Firefox DevTools and return to normal browsing mode.

    This will hide all DevTools capabilities and clean up RDP connections.
    """
    try:
        session_manager = get_session_manager()
        if not session_manager:
            return {
                "status": "error",
                "message": "Session manager not available"
            }

        # Get session ID
        session_id = params.session_id
        if not session_id:
            # Try to get default session
            sessions = await session_manager.list_sessions()
            if sessions:
                session_id = sessions[0]["session_id"]
            else:
                return {
                    "status": "error",
                    "message": "No active session found"
                }

        # Get DevTools usage stats before disabling
        devtools_state = get_devtools_state()
        metadata = devtools_state.get_session_metadata(session_id)
        tools_accessed = metadata.get("tools_accessed", set())

        # Disable DevTools for this session
        devtools_state.disable_for_session(session_id)

        # Cleanup RDP connection if it exists
        session = await session_manager.get_session(session_id)
        if session and hasattr(session.context, '_rdp_client'):
            try:
                rdp_client = session.context._rdp_client
                rdp_client.disconnect()
                delattr(session.context, '_rdp_client')
                delattr(session.context, '_rdp_root_ids')
                delattr(session.context, '_rdp_port')
            except Exception as e:
                logger.warning(f"Error disconnecting RDP client: {e}")

        logger.info(f"Firefox DevTools disabled for session: {session_id}")

        return {
            "status": "success",
            "message": "Firefox DevTools disabled successfully",
            "session_id": session_id,
            "session_stats": {
                "tools_accessed_count": len(tools_accessed),
                "tools_accessed": list(tools_accessed),
                "session_duration": metadata.get("enabled_at", "unknown")
            },
            "note": "RDP connection cleaned up and DevTools tools are now hidden"
        }

    except Exception as e:
        logger.error(f"Failed to disable Firefox DevTools: {e}")
        return {
            "status": "error",
            "message": f"Failed to disable Firefox DevTools: {str(e)}"
        }


async def browser_firefox_evaluate_js(params: FirefoxEvaluateJSParams) -> Dict[str, Any]:
    """
    Execute JavaScript expression in Firefox with full runtime access.

    Provides JavaScript evaluation capabilities with access to the page context,
    variables, functions, and DOM. Uses Firefox WebConsole actor.
    """
    try:
        from geckordp.actors.web_console import WebConsoleActor

        session_manager = get_session_manager()
        session = await _get_firefox_session_with_devtools(session_manager, params.session_id)
        if isinstance(session, dict) and session.get("status") == "error":
            return session

        # Track tool usage
        devtools_state = get_devtools_state()
        devtools_state.track_tool_access(session["session_id"], "browser_firefox_evaluate_js")

        rdp_client = session["context"]._rdp_client
        root_ids = session["context"]._rdp_root_ids

        # Get WebConsole actor
        web_console_actor_id = root_ids.get("consoleActor")
        if not web_console_actor_id:
            return {
                "status": "error",
                "message": "WebConsole actor not available"
            }

        web_console = WebConsoleActor(rdp_client, web_console_actor_id)

        # Evaluate JavaScript expression
        result = web_console.evaluate_js_async(
            text=params.expression,
            eager=params.eager
        )

        return {
            "status": "success",
            "expression": params.expression,
            "result": result,
            "session_id": session["session_id"]
        }

    except Exception as e:
        logger.error(f"Firefox JavaScript evaluation failed: {e}")
        return {
            "status": "error",
            "message": f"Firefox JavaScript evaluation failed: {str(e)}"
        }


async def browser_firefox_get_console_logs(params: FirefoxGetConsoleLogsParams) -> Dict[str, Any]:
    """
    Capture console messages, warnings, and errors from Firefox.

    Provides comprehensive console log access including message types and content.
    """
    try:
        from geckordp.actors.web_console import WebConsoleActor

        session_manager = get_session_manager()
        session = await _get_firefox_session_with_devtools(session_manager, params.session_id)
        if isinstance(session, dict) and session.get("status") == "error":
            return session

        # Track tool usage
        devtools_state = get_devtools_state()
        devtools_state.track_tool_access(session["session_id"], "browser_firefox_get_console_logs")

        rdp_client = session["context"]._rdp_client
        root_ids = session["context"]._rdp_root_ids

        # Get WebConsole actor
        web_console_actor_id = root_ids.get("consoleActor")
        if not web_console_actor_id:
            return {
                "status": "error",
                "message": "WebConsole actor not available"
            }

        web_console = WebConsoleActor(rdp_client, web_console_actor_id)

        # Convert message types to enum
        message_types = []
        for msg_type in params.message_types:
            if msg_type == "PageError":
                message_types.append(WebConsoleActor.MessageTypes.PAGE_ERROR)
            elif msg_type == "ConsoleAPI":
                message_types.append(WebConsoleActor.MessageTypes.CONSOLE_API)

        # Get cached console messages
        messages = web_console.get_cached_messages(message_types)

        return {
            "status": "success",
            "console_messages": messages,
            "message_count": len(messages.get("messages", [])) if isinstance(messages, dict) else 0,
            "session_id": session["session_id"]
        }

    except Exception as e:
        logger.error(f"Getting Firefox console logs failed: {e}")
        return {
            "status": "error",
            "message": f"Getting Firefox console logs failed: {str(e)}"
        }


async def browser_firefox_inspect_dom(params: FirefoxInspectDOMParams) -> Dict[str, Any]:
    """
    Examine DOM structure and properties in Firefox.

    Provides DOM inspection capabilities using Firefox Inspector actor.
    """
    try:
        from geckordp.actors.inspector import InspectorActor
        from geckordp.actors.walker import WalkerActor

        session_manager = get_session_manager()
        session = await _get_firefox_session_with_devtools(session_manager, params.session_id)
        if isinstance(session, dict) and session.get("status") == "error":
            return session

        # Track tool usage
        devtools_state = get_devtools_state()
        devtools_state.track_tool_access(session["session_id"], "browser_firefox_inspect_dom")

        rdp_client = session["context"]._rdp_client
        root_ids = session["context"]._rdp_root_ids

        # Get Inspector actor
        inspector_actor_id = root_ids.get("inspectorActor")
        if not inspector_actor_id:
            return {
                "status": "error",
                "message": "Inspector actor not available"
            }

        inspector = InspectorActor(rdp_client, inspector_actor_id)

        # Get walker for DOM tree traversal
        walker_actor_id = inspector.get_walker()
        walker = WalkerActor(rdp_client, walker_actor_id)

        # Get document root
        document = walker.document()

        return {
            "status": "success",
            "document": document,
            "session_id": session["session_id"],
            "note": "Use WalkerActor for detailed DOM traversal"
        }

    except Exception as e:
        logger.error(f"Firefox DOM inspection failed: {e}")
        return {
            "status": "error",
            "message": f"Firefox DOM inspection failed: {str(e)}"
        }


# Helper function for session and DevTools validation
async def _get_firefox_session_with_devtools(session_manager, session_id: Optional[str]) -> Dict[str, Any]:
    """
    Get Firefox session and validate DevTools is enabled.

    Returns either session info or error response.
    """
    if not session_manager:
        return {
            "status": "error",
            "message": "Session manager not available"
        }

    # Get session ID if not provided
    if not session_id:
        sessions = await session_manager.list_sessions()
        if not sessions:
            return {
                "status": "error",
                "message": "No active session found. Configure browser first."
            }
        session_id = sessions[0]["session_id"]

    # Check if DevTools is enabled for this session
    devtools_state = get_devtools_state()
    if not devtools_state.is_enabled_for_session(session_id):
        return {
            "status": "error",
            "message": "Firefox DevTools not enabled for this session",
            "hint": "Use 'browser_firefox_dev_tools_enable' first"
        }

    # Get the session
    session = await session_manager.get_session(session_id)
    if not session:
        return {
            "status": "error",
            "message": f"Session {session_id} not found"
        }

    # Check if RDP connection exists
    if not hasattr(session.context, '_rdp_client'):
        return {
            "status": "error",
            "message": "RDP connection not initialized",
            "hint": "Re-enable Firefox DevTools to initialize RDP connection"
        }

    return {
        "context": session,
        "session_id": session_id
    }


# Placeholder implementations for remaining tools (to be implemented)
async def browser_firefox_set_breakpoint(params: FirefoxSetBreakpointParams) -> Dict[str, Any]:
    """Set JavaScript breakpoint in Firefox with conditional support."""
    return {
        "status": "not_implemented",
        "message": "Firefox breakpoint support coming soon",
        "note": "Will use ThreadActor and SourceActor for breakpoint management"
    }


async def browser_firefox_resume_execution(params: FirefoxResumeParams) -> Dict[str, Any]:
    """Control Firefox JavaScript execution (next, step, finish)."""
    return {
        "status": "not_implemented",
        "message": "Firefox execution control coming soon",
        "note": "Will use ThreadActor.resume() with different ResumeLimit values"
    }
