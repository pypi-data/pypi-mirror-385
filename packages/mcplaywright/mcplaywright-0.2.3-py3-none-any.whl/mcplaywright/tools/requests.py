"""
HTTP Request Monitoring Tools for MCPlaywright

Comprehensive request/response interception and analysis tools.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from pydantic import BaseModel, Field

from ..session_manager import get_session_manager
from ..request_interceptor import RequestInterceptor

logger = logging.getLogger(__name__)


class StartMonitoringParams(BaseModel):
    """Parameters for starting request monitoring"""
    session_id: Optional[str] = Field(None, description="Session ID")
    url_filter: Optional[str] = Field(None, description="URL filter (string contains match)")
    capture_body: Optional[bool] = Field(True, description="Capture request/response bodies")
    max_body_size: Optional[int] = Field(10485760, description="Maximum body size in bytes (default: 10MB)")


class GetRequestsParams(BaseModel):
    """Parameters for retrieving captured requests"""
    session_id: Optional[str] = Field(None, description="Session ID")
    filter_type: str = Field("all", description="Filter: 'all', 'failed', 'slow', 'errors', 'success'")
    domain: Optional[str] = Field(None, description="Filter by domain hostname")
    method: Optional[str] = Field(None, description="Filter by HTTP method")
    status: Optional[int] = Field(None, description="Filter by HTTP status code")
    format: str = Field("summary", description="Format: 'summary', 'detailed', 'stats'")
    slow_threshold: int = Field(1000, description="Threshold in ms for slow requests")
    limit: int = Field(50, description="Maximum number of requests to return")


class ExportRequestsParams(BaseModel):
    """Parameters for exporting captured requests"""
    session_id: Optional[str] = Field(None, description="Session ID")
    format: str = Field("json", description="Export format: 'json', 'har', 'summary'")
    filename: Optional[str] = Field(None, description="Custom filename for export")
    filter_type: str = Field("all", description="Filter which requests to export")


class ClearRequestsParams(BaseModel):
    """Parameters for clearing captured requests"""
    session_id: Optional[str] = Field(None, description="Session ID")


class MonitoringStatusParams(BaseModel):
    """Parameters for checking monitoring status"""
    session_id: Optional[str] = Field(None, description="Session ID")


async def browser_start_request_monitoring(params: StartMonitoringParams) -> Dict[str, Any]:
    """
    Start comprehensive HTTP request/response monitoring.

    Enables deep HTTP traffic analysis during browser automation.
    Captures headers, bodies, timing, and failure information for all requests.

    Features:
    - URL filtering (string contains match)
    - Request/response body capture with size limits
    - Automatic timing measurement
    - Failure detection and tracking

    Perfect for:
    - API reverse engineering and analysis
    - Security testing and vulnerability assessment
    - Performance monitoring and optimization
    - Debugging network issues

    Returns:
        Monitoring startup result with configuration details
    """
    try:
        session_manager = get_session_manager()
        context = await session_manager.get_or_create_session(params.session_id)

        # Get current page
        page = await context.get_current_page()

        # Create output directory for this session
        output_path = context.artifacts_dir / "requests"
        output_path.mkdir(parents=True, exist_ok=True)

        # Create request interceptor
        interceptor = RequestInterceptor(
            page=page,
            url_filter=params.url_filter,
            capture_body=params.capture_body or True,
            max_body_size=params.max_body_size or 10485760,
            output_path=str(output_path)
        )

        # Attach interceptor to page
        await interceptor.attach()

        # Store interceptor in context
        context._request_interceptor = interceptor

        logger.info(f"Request monitoring started for session {context.session_id}")

        return {
            "success": True,
            "message": "Request monitoring started successfully",
            "configuration": {
                "url_filter": params.url_filter or "All requests",
                "capture_body": params.capture_body,
                "max_body_size_mb": (params.max_body_size or 10485760) / 1024 / 1024,
                "output_path": str(output_path)
            },
            "session_id": context.session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to start request monitoring: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": params.session_id,
            "timestamp": datetime.now().isoformat()
        }


async def browser_get_requests(params: GetRequestsParams) -> Dict[str, Any]:
    """
    Retrieve and analyze captured HTTP requests.

    Access comprehensive request data including timing, headers, bodies,
    and failure information. Supports advanced filtering and analysis.

    Filtering options:
    - all: All captured requests
    - failed: Network failures only
    - slow: Requests slower than threshold
    - errors: HTTP 4xx/5xx responses
    - success: HTTP 2xx/3xx responses

    Format options:
    - summary: Basic request/response info
    - detailed: Full headers and bodies
    - stats: Statistics dashboard only

    Returns:
        Captured requests with filtering and formatting applied
    """
    try:
        session_manager = get_session_manager()
        context = await session_manager.get_session(params.session_id)

        if not context:
            return {
                "success": False,
                "error": f"Session {params.session_id} not found",
                "session_id": params.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Get request interceptor
        interceptor = getattr(context, '_request_interceptor', None)
        if not interceptor:
            return {
                "success": False,
                "error": "Request monitoring not active. Start monitoring first with browser_start_request_monitoring",
                "session_id": context.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Handle stats-only format
        if params.format == "stats":
            stats = interceptor.get_statistics()
            return {
                "success": True,
                "statistics": stats.model_dump(mode='json'),
                "session_id": context.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Get and filter requests
        requests = interceptor.get_requests()

        # Apply type filter
        if params.filter_type == "failed":
            requests = interceptor.get_failed_requests()
        elif params.filter_type == "slow":
            requests = interceptor.get_slow_requests(params.slow_threshold)
        elif params.filter_type == "errors":
            requests = [r for r in requests if r.response and r.response.status >= 400]
        elif params.filter_type == "success":
            requests = [r for r in requests if r.response and r.response.status < 400]

        # Apply additional filters
        if params.domain:
            requests = [r for r in requests if params.domain in r.url]

        if params.method:
            requests = [r for r in requests if r.method.upper() == params.method.upper()]

        if params.status:
            requests = [r for r in requests if r.response and r.response.status == params.status]

        # Apply limit
        limited_requests = requests[-params.limit:] if params.limit > 0 else requests

        # Format requests based on requested format
        formatted_requests = []
        for req in limited_requests:
            if params.format == "detailed":
                # Full request/response data
                formatted = {
                    "method": req.method,
                    "url": req.url,
                    "status": req.response.status if req.response else None,
                    "duration_ms": req.duration,
                    "timestamp": req.timestamp.isoformat(),
                    "headers": req.headers,
                    "response_headers": req.response.headers if req.response else None,
                    "response_body": req.response.body if req.response else None,
                    "body_size": req.response.body_size if req.response else 0,
                    "from_cache": req.response.from_cache if req.response else False,
                    "failed": req.failed,
                    "failure_reason": req.failure.error_text if req.failure else None
                }
            else:
                # Summary format
                formatted = {
                    "method": req.method,
                    "url": req.url,
                    "status": req.response.status if req.response else "FAILED" if req.failed else "PENDING",
                    "duration_ms": req.duration,
                    "timestamp": req.timestamp.isoformat(),
                    "size_kb": (req.response.body_size / 1024) if req.response else 0,
                    "from_cache": req.response.from_cache if req.response else False
                }

            formatted_requests.append(formatted)

        # Get statistics
        stats = interceptor.get_statistics()

        return {
            "success": True,
            "requests": formatted_requests,
            "count": len(formatted_requests),
            "total_captured": len(interceptor.get_requests()),
            "filtered_count": len(requests),
            "statistics": {
                "total": stats.total_requests,
                "successful": stats.successful_requests,
                "failed": stats.failed_requests,
                "errors": stats.error_responses,
                "avg_response_time_ms": stats.average_response_time
            },
            "filters_applied": {
                "type": params.filter_type,
                "domain": params.domain,
                "method": params.method,
                "status": params.status,
                "limit": params.limit
            },
            "session_id": context.session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get requests: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": params.session_id,
            "timestamp": datetime.now().isoformat()
        }


async def browser_export_requests(params: ExportRequestsParams) -> Dict[str, Any]:
    """
    Export captured requests to various formats.

    Export formats:
    - json: Full data with comprehensive request/response details
    - har: HTTP Archive format (importable to Chrome DevTools, Insomnia, Postman)
    - summary: Human-readable markdown report with statistics

    Perfect for:
    - Sharing analysis results with team members
    - Importing into other analysis tools
    - Creating audit reports
    - Documentation and debugging

    Returns:
        Export result with file path and export details
    """
    try:
        session_manager = get_session_manager()
        context = await session_manager.get_session(params.session_id)

        if not context:
            return {
                "success": False,
                "error": f"Session {params.session_id} not found",
                "session_id": params.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Get request interceptor
        interceptor = getattr(context, '_request_interceptor', None)
        if not interceptor:
            return {
                "success": False,
                "error": "Request monitoring not active",
                "session_id": context.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Check if we have requests to export
        requests = interceptor.get_requests()
        if not requests:
            return {
                "success": False,
                "error": "No requests captured to export",
                "session_id": context.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Export based on format
        export_path = None
        if params.format == "har":
            export_path = await interceptor.export_har(params.filename)
        elif params.format == "json":
            export_path = await interceptor.export_json(params.filename)
        elif params.format == "summary":
            # Create summary report
            stats = interceptor.get_statistics()
            summary_lines = [
                "# HTTP Request Analysis Summary",
                f"Generated: {datetime.now().isoformat()}",
                "",
                "## Overview",
                f"- Total Requests: {stats.total_requests}",
                f"- Successful: {stats.successful_requests}",
                f"- Failed: {stats.failed_requests}",
                f"- Errors: {stats.error_responses}",
                f"- Average Response Time: {stats.average_response_time}ms",
                "",
                "## Request Methods",
                *[f"- {method}: {count}" for method, count in stats.requests_by_method.items()],
                "",
                "## Status Codes",
                *[f"- {status}: {count}" for status, count in stats.requests_by_status.items()],
                "",
                "## Top Domains",
                *[f"- {domain}: {count}" for domain, count in sorted(stats.requests_by_domain.items(), key=lambda x: x[1], reverse=True)[:10]],
                "",
                "## Slow Requests (>1s)",
                *[f"- {req.method} {req.url} ({req.duration}ms)" for req in interceptor.get_slow_requests()[:10]],
                "",
                "## Failed Requests",
                *[f"- {req.method} {req.url} - {req.failure.error_text if req.failure else 'Unknown error'}" for req in interceptor.get_failed_requests()[:10]]
            ]

            filename = params.filename or f"requests_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            export_path = str(Path(interceptor.output_path) / filename)
            with open(export_path, 'w') as f:
                f.write('\n'.join(summary_lines))

        logger.info(f"Exported {len(requests)} requests to {params.format}: {export_path}")

        return {
            "success": True,
            "message": f"Exported {len(requests)} requests successfully",
            "export_path": export_path,
            "format": params.format,
            "request_count": len(requests),
            "session_id": context.session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to export requests: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": params.session_id,
            "timestamp": datetime.now().isoformat()
        }


async def browser_clear_requests(params: ClearRequestsParams) -> Dict[str, Any]:
    """
    Clear all captured request data from memory.

    Useful for:
    - Freeing memory during long sessions
    - Starting fresh analysis after configuration changes
    - Managing storage in memory-constrained environments

    Returns:
        Cleared request count and confirmation
    """
    try:
        session_manager = get_session_manager()
        context = await session_manager.get_session(params.session_id)

        if not context:
            return {
                "success": False,
                "error": f"Session {params.session_id} not found",
                "session_id": params.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Get request interceptor
        interceptor = getattr(context, '_request_interceptor', None)
        if not interceptor:
            return {
                "success": False,
                "error": "Request monitoring not active",
                "session_id": context.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Clear requests
        cleared_count = interceptor.clear()

        logger.info(f"Cleared {cleared_count} requests for session {context.session_id}")

        return {
            "success": True,
            "message": f"Cleared {cleared_count} captured requests",
            "cleared_count": cleared_count,
            "session_id": context.session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to clear requests: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": params.session_id,
            "timestamp": datetime.now().isoformat()
        }


async def browser_request_monitoring_status(params: MonitoringStatusParams) -> Dict[str, Any]:
    """
    Check request monitoring status and configuration.

    Shows:
    - Whether monitoring is active
    - Current configuration settings
    - Capture statistics
    - Output paths and storage details

    Returns:
        Complete monitoring status and configuration
    """
    try:
        session_manager = get_session_manager()
        context = await session_manager.get_session(params.session_id)

        if not context:
            return {
                "success": False,
                "error": f"Session {params.session_id} not found",
                "session_id": params.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Get request interceptor
        interceptor = getattr(context, '_request_interceptor', None)
        if not interceptor:
            return {
                "success": True,
                "monitoring_active": False,
                "message": "Request monitoring is not active. Start with browser_start_request_monitoring",
                "session_id": context.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Get current statistics
        stats = interceptor.get_statistics()

        # Get current page info
        page = await context.get_current_page()

        return {
            "success": True,
            "monitoring_active": True,
            "configuration": {
                "capture_body": interceptor.capture_body,
                "max_body_size_mb": interceptor.max_body_size / 1024 / 1024,
                "url_filter": str(interceptor.url_filter) if interceptor.url_filter else "All requests",
                "output_path": str(interceptor.output_path)
            },
            "current_page": page.url,
            "statistics": {
                "total_captured": stats.total_requests,
                "successful": stats.successful_requests,
                "failed": stats.failed_requests,
                "errors": stats.error_responses,
                "average_response_time_ms": stats.average_response_time,
                "slow_requests": stats.slow_requests
            },
            "session_id": context.session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get monitoring status: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": params.session_id,
            "timestamp": datetime.now().isoformat()
        }
