"""
MCPlaywright Comprehensive Server

Full-featured FastMCP server with all implemented tools exposed.
Combines module-based tools (BrowserCore, Navigation, etc.) with
standalone function-based tools (tabs, video, dialogs, etc.).
"""

from fastmcp import FastMCP
from typing import Dict, Any
import logging

# Import core modules
from .modules.browser import BrowserCore
from .modules.navigation import BrowserNavigation
from .modules.interaction import BrowserInteraction
from .modules.screenshots import BrowserScreenshots
from .modules.client_id import ClientIdentification

# Import standalone tool functions
from .tools.tabs import (
    browser_new_tab, browser_close_tab, browser_switch_tab, browser_list_tabs,
    NewTabParams, CloseTabParams, SwitchTabParams, TabListParams
)
from .tools.video import (
    browser_start_recording, browser_stop_recording,
    StartRecordingParams, StopRecordingParams
)
from .tools.dialogs import (
    browser_file_upload, browser_handle_dialog,
    browser_dismiss_file_chooser, browser_dismiss_all_file_choosers,
    FileUploadParams, HandleDialogParams, DismissFileChooserParams
)
from .tools.evaluation import (
    browser_evaluate, browser_press_key, browser_type_text,
    EvaluateParams
)
from .tools.wait import (
    browser_wait_for_text, browser_wait_for_text_gone,
    browser_wait_for_element, browser_wait_for_load_state,
    browser_wait_for_time, browser_wait_for_request,
    WaitForTextParams, WaitForTextGoneParams, WaitForElementParams,
    WaitForLoadStateParams, WaitForTimeParams, WaitForRequestParams
)
from .tools.requests import (
    browser_start_request_monitoring, browser_get_requests,
    browser_export_requests, browser_clear_requests,
    browser_request_monitoring_status,
    StartMonitoringParams, GetRequestsParams, ExportRequestsParams,
    ClearRequestsParams, MonitoringStatusParams
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPlaywrightComprehensive(
    BrowserCore,
    BrowserNavigation,
    BrowserInteraction,
    BrowserScreenshots,
    ClientIdentification
):
    """
    Comprehensive MCPlaywright server with full feature parity.

    Includes ALL implemented functionality:
    - Core browser management and lifecycle
    - Navigation and page control
    - Element interactions (click, type, etc.)
    - Screenshots and visual capture
    - Debug toolbar and client identification
    - Tab management
    - Video recording
    - File uploads and dialog handling
    - JavaScript evaluation
    - Advanced wait strategies
    """

    def __init__(self):
        """Initialize all modules."""
        super().__init__()
        logger.info("MCPlaywright comprehensive server initialized")


# Create FastMCP app and server instance
app = FastMCP("MCPlaywright Comprehensive")
server = MCPlaywrightComprehensive()

# Register all module-based tools
server.register_all(app)

# Register standalone tool functions with FastMCP decorators

# === Tab Management Tools ===

@app.tool()
async def browser_tab_new(params: NewTabParams) -> Dict[str, Any]:
    """
    Open a new browser tab and optionally navigate to URL.

    Creates a new page in the current browser context and switches to it.
    Supports optional navigation to a specific URL after creation.
    """
    return await browser_new_tab(params)


@app.tool()
async def browser_tab_close(params: CloseTabParams) -> Dict[str, Any]:
    """
    Close a browser tab by index.

    Closes the specified tab or current tab if no index provided.
    Automatically switches to another tab if the current tab is closed.
    """
    return await browser_close_tab(params)


@app.tool()
async def browser_tab_select(params: SwitchTabParams) -> Dict[str, Any]:
    """
    Switch to a different browser tab by index.

    Changes the active tab to the specified index and updates the current page.
    """
    return await browser_switch_tab(params)


@app.tool()
async def browser_tab_list(params: TabListParams) -> Dict[str, Any]:
    """
    List all open browser tabs with detailed information.

    Returns comprehensive information about all tabs in the current session.
    """
    return await browser_list_tabs(params)


# === Video Recording Tools ===

@app.tool()
async def browser_start_video_recording(params: StartRecordingParams) -> Dict[str, Any]:
    """
    Start video recording browser session with intelligent viewport matching.

    Features:
    - Automatic viewport matching to eliminate gray borders
    - Multiple recording modes (smart, continuous, action-only, segment)
    - Session-based artifact storage

    Smart mode automatically pauses during waits and resumes during actions.
    """
    return await browser_start_recording(params)


@app.tool()
async def browser_stop_video_recording(params: StopRecordingParams) -> Dict[str, Any]:
    """
    Stop video recording and save video files.

    Finalizes all recordings and returns paths to saved video files.
    """
    return await browser_stop_recording(params)


# === File Upload and Dialog Tools ===

@app.tool()
async def browser_upload_file(params: FileUploadParams) -> Dict[str, Any]:
    """
    Upload files to a file input element.

    Handles single or multiple file uploads with validation and progress tracking.
    """
    return await browser_file_upload(params)


@app.tool()
async def browser_dialog_handle(params: HandleDialogParams) -> Dict[str, Any]:
    """
    Handle browser dialogs (alert, confirm, prompt).

    Provides comprehensive dialog handling including text input for prompts.
    """
    return await browser_handle_dialog(params)


@app.tool()
async def browser_file_chooser_dismiss(params: DismissFileChooserParams) -> Dict[str, Any]:
    """
    Dismiss file chooser dialogs without uploading files.

    Handles dismissal of stuck file chooser dialogs gracefully.
    """
    return await browser_dismiss_file_chooser(params)


# === JavaScript Evaluation Tools ===

@app.tool()
async def browser_js_evaluate(params: EvaluateParams) -> Dict[str, Any]:
    """
    Evaluate JavaScript expression on page or element.

    Executes JavaScript code in browser context with return value serialization.
    """
    return await browser_evaluate(params)


@app.tool()
async def browser_keyboard_press(params: dict) -> Dict[str, Any]:
    """
    Press a key on the keyboard.

    Supports special keys, modifiers, and character input.
    """
    return await browser_press_key(params)


@app.tool()
async def browser_keyboard_type(params: dict) -> Dict[str, Any]:
    """
    Type text into the currently focused element.

    Character-by-character typing with configurable delays.
    """
    return await browser_type_text(params)


# === Wait Tools ===

@app.tool()
async def browser_wait_text(params: WaitForTextParams) -> Dict[str, Any]:
    """
    Wait for text to appear on the page.

    Smart video recording integration - automatically pauses in smart mode.
    """
    return await browser_wait_for_text(params)


@app.tool()
async def browser_wait_text_gone(params: WaitForTextGoneParams) -> Dict[str, Any]:
    """
    Wait for text to disappear from the page.

    Smart video recording integration for clean demo videos.
    """
    return await browser_wait_for_text_gone(params)


@app.tool()
async def browser_wait_element(params: WaitForElementParams) -> Dict[str, Any]:
    """
    Wait for an element to reach a specific state.

    Supports visible, hidden, attached, and detached states.
    """
    return await browser_wait_for_element(params)


@app.tool()
async def browser_wait_load(params: WaitForLoadStateParams) -> Dict[str, Any]:
    """
    Wait for the page to reach a specific load state.

    Supports load, domcontentloaded, and networkidle states.
    """
    return await browser_wait_for_load_state(params)


@app.tool()
async def browser_wait_timeout(params: WaitForTimeParams) -> Dict[str, Any]:
    """
    Wait for a specific amount of time.

    Smart video recording integration - pauses recording in smart mode.
    """
    return await browser_wait_for_time(params)


@app.tool()
async def browser_wait_network(params: WaitForRequestParams) -> Dict[str, Any]:
    """
    Wait for a network request matching the URL pattern.

    Useful for waiting for API calls or resource loading.
    """
    return await browser_wait_for_request(params)


# === HTTP Request Monitoring Tools ===

@app.tool()
async def browser_monitoring_start(params: StartMonitoringParams) -> Dict[str, Any]:
    """
    Start comprehensive HTTP request/response monitoring.

    Enables deep HTTP traffic analysis with detailed timing, headers, and bodies.
    Perfect for API reverse engineering, security testing, and performance analysis.
    """
    return await browser_start_request_monitoring(params)


@app.tool()
async def browser_monitoring_get(params: GetRequestsParams) -> Dict[str, Any]:
    """
    Retrieve and analyze captured HTTP requests.

    Supports advanced filtering by type, domain, method, and status code.
    Provides summary, detailed, or statistics-only views.
    """
    return await browser_get_requests(params)


@app.tool()
async def browser_monitoring_export(params: ExportRequestsParams) -> Dict[str, Any]:
    """
    Export captured requests to various formats.

    - json: Full data with comprehensive details
    - har: HTTP Archive format (Chrome DevTools, Insomnia, Postman)
    - summary: Human-readable markdown report
    """
    return await browser_export_requests(params)


@app.tool()
async def browser_monitoring_clear(params: ClearRequestsParams) -> Dict[str, Any]:
    """
    Clear all captured request data from memory.

    Useful for freeing memory or starting fresh analysis.
    """
    return await browser_clear_requests(params)


@app.tool()
async def browser_monitoring_status(params: MonitoringStatusParams) -> Dict[str, Any]:
    """
    Check request monitoring status and configuration.

    Shows whether monitoring is active, current settings, and statistics.
    """
    return await browser_request_monitoring_status(params)


logger.info("🚀 MCPlaywright comprehensive server ready with complete feature set!")
logger.info("📊 Tool categories:")
logger.info("   • Core browser management (navigate, click, type, screenshot)")
logger.info("   • Console messages (browser_console_messages, browser_clear_console)")
logger.info("   • Tab management (new, close, select, list)")
logger.info("   • Video recording (start, stop, modes)")
logger.info("   • File uploads & dialogs (upload, handle, dismiss)")
logger.info("   • JavaScript evaluation (evaluate, press_key, type)")
logger.info("   • Wait strategies (text, element, load, timeout, network)")
logger.info("   • HTTP request monitoring (start, get, export, clear, status)")
logger.info("   • Debug toolbar & client identification")


def main():
    """Run the comprehensive MCPlaywright server via stdio."""
    app.run()


if __name__ == "__main__":
    main()
