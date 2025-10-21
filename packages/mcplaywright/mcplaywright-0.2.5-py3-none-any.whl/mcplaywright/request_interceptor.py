"""
HTTP Request Interceptor

Comprehensive request/response interception and analysis engine.
Captures all browser HTTP traffic with detailed timing, headers, and bodies.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from urllib.parse import urlparse
from playwright.async_api import Page, Route, Request, Response

from .models.request import InterceptedRequest, ResponseInfo, RequestFailure, RequestStatistics

logger = logging.getLogger(__name__)


class RequestInterceptor:
    """
    Comprehensive HTTP request/response interceptor.

    Hooks into Playwright's routing system to capture all browser HTTP traffic.
    Provides filtering, statistics, and export capabilities for analysis.

    Features:
    - URL pattern filtering (string, regex, or custom function)
    - Request/response body capture with size limits
    - Timing and performance metrics
    - HAR file export for Chrome DevTools
    - CSV export for spreadsheet analysis
    - Statistics dashboard with aggregations
    """

    def __init__(
        self,
        page: Page,
        url_filter: Optional[Union[str, Callable]] = None,
        capture_body: bool = True,
        max_body_size: int = 10485760,  # 10MB
        output_path: Optional[str] = None
    ):
        """
        Initialize request interceptor.

        Args:
            page: Playwright page to monitor
            url_filter: URL filter (string contains, regex, or function)
            capture_body: Whether to capture request/response bodies
            max_body_size: Maximum body size to capture in bytes
            output_path: Directory for saved request data
        """
        self.page = page
        self.url_filter = url_filter
        self.capture_body = capture_body
        self.max_body_size = max_body_size
        self.output_path = Path(output_path) if output_path else Path("./requests")

        # Storage for captured requests
        self._requests: List[InterceptedRequest] = []
        self._requests_by_id: Dict[str, InterceptedRequest] = {}

        # Request timing tracking
        self._request_start_times: Dict[str, datetime] = {}

        # Statistics
        self._stats_dirty = True
        self._cached_stats: Optional[RequestStatistics] = None

        # State
        self._attached = False
        self._route_handler = None

        logger.info(f"Request interceptor initialized (capture_body: {capture_body}, max_size: {max_body_size})")

    async def attach(self):
        """Attach interceptor to page to start monitoring requests."""
        if self._attached:
            logger.warning("Request interceptor already attached")
            return

        # Define route handler to intercept all requests
        async def route_handler(route: Route):
            """Handle intercepted route."""
            request = route.request

            # Check if request matches filter
            if not self._matches_filter(request.url):
                # Continue without monitoring
                await route.continue_()
                return

            # Generate unique request ID
            request_id = str(uuid.uuid4())

            # Record request start time
            self._request_start_times[request_id] = datetime.now()

            # Capture request information
            try:
                intercepted_request = InterceptedRequest(
                    url=request.url,
                    method=request.method,
                    headers=request.headers,
                    post_data=request.post_data if self.capture_body else None,
                    resource_type=request.resource_type,
                    timestamp=datetime.now(),
                    request_id=request_id
                )

                # Store request
                self._requests.append(intercepted_request)
                self._requests_by_id[request_id] = intercepted_request
                self._stats_dirty = True

                logger.debug(f"Captured request: {request.method} {request.url}")

            except Exception as e:
                logger.error(f"Error capturing request: {e}")

            # Continue the request
            await route.continue_()

        # Set up response listener to capture response data
        async def response_handler(response: Response):
            """Handle response to update request data."""
            request = response.request

            # Find corresponding intercepted request
            matching_requests = [
                req for req in self._requests
                if req.url == request.url and req.method == request.method and req.response is None
            ]

            if not matching_requests:
                return

            # Use the most recent matching request
            intercepted_request = matching_requests[-1]
            request_id = intercepted_request.request_id

            # Calculate duration
            start_time = self._request_start_times.get(request_id)
            duration = None
            if start_time:
                duration = int((datetime.now() - start_time).total_seconds() * 1000)
                del self._request_start_times[request_id]

            # Capture response information
            try:
                # Get response body if capture enabled
                body = None
                body_size = 0
                if self.capture_body:
                    try:
                        body_bytes = await response.body()
                        body_size = len(body_bytes)
                        if body_size <= self.max_body_size:
                            # Try to decode as text
                            try:
                                body = body_bytes.decode('utf-8')
                            except:
                                body = f"<Binary data: {body_size} bytes>"
                        else:
                            body = f"<Body too large: {body_size} bytes, max: {self.max_body_size}>"
                    except Exception as body_error:
                        logger.debug(f"Could not capture response body: {body_error}")
                        body = "<Body unavailable>"

                # Create response info
                response_info = ResponseInfo(
                    status=response.status,
                    status_text=response.status_text,
                    headers=response.headers,
                    body=body,
                    body_size=body_size,
                    from_cache=response.from_service_worker or False,  # Approximation
                    duration=duration
                )

                # Update intercepted request
                intercepted_request.response = response_info
                intercepted_request.duration = duration
                self._stats_dirty = True

                logger.debug(f"Captured response: {response.status} for {request.url} ({duration}ms)")

            except Exception as e:
                logger.error(f"Error capturing response: {e}")

        # Set up request failure listener
        async def request_failure_handler(request: Request):
            """Handle request failure."""
            matching_requests = [
                req for req in self._requests
                if req.url == request.url and req.method == request.method and not req.failed
            ]

            if not matching_requests:
                return

            # Mark request as failed
            intercepted_request = matching_requests[-1]
            intercepted_request.failed = True
            intercepted_request.failure = RequestFailure(
                error_text=request.failure or "Unknown error",
                timestamp=datetime.now()
            )
            self._stats_dirty = True

            logger.debug(f"Request failed: {request.method} {request.url}")

        # Attach all handlers
        self._route_handler = route_handler
        await self.page.route("**/*", route_handler)
        self.page.on("response", response_handler)
        self.page.on("requestfailed", request_failure_handler)

        self._attached = True
        logger.info(f"Request interceptor attached to page: {self.page.url}")

    async def detach(self):
        """Detach interceptor from page to stop monitoring."""
        if not self._attached:
            return

        # Remove route handler
        if self._route_handler:
            try:
                await self.page.unroute("**/*", self._route_handler)
            except Exception as e:
                logger.debug(f"Error removing route: {e}")

        self._attached = False
        logger.info("Request interceptor detached")

    def _matches_filter(self, url: str) -> bool:
        """Check if URL matches the configured filter."""
        if self.url_filter is None:
            return True

        if isinstance(self.url_filter, str):
            # Simple string contains match
            return self.url_filter in url

        if callable(self.url_filter):
            # Custom function filter
            try:
                return self.url_filter(url)
            except Exception as e:
                logger.error(f"URL filter function error: {e}")
                return True

        return True

    def get_requests(self) -> List[InterceptedRequest]:
        """Get all captured requests."""
        return self._requests.copy()

    def get_failed_requests(self) -> List[InterceptedRequest]:
        """Get all failed requests."""
        return [req for req in self._requests if req.failed]

    def get_slow_requests(self, threshold_ms: int = 1000) -> List[InterceptedRequest]:
        """Get requests slower than threshold."""
        return [
            req for req in self._requests
            if req.duration is not None and req.duration > threshold_ms
        ]

    def clear(self) -> int:
        """Clear all captured requests."""
        count = len(self._requests)
        self._requests.clear()
        self._requests_by_id.clear()
        self._request_start_times.clear()
        self._stats_dirty = True
        logger.info(f"Cleared {count} captured requests")
        return count

    def get_statistics(self) -> RequestStatistics:
        """Generate comprehensive statistics for captured requests."""
        if not self._stats_dirty and self._cached_stats:
            return self._cached_stats

        stats = RequestStatistics()

        if not self._requests:
            return stats

        # Basic counts
        stats.total_requests = len(self._requests)
        stats.failed_requests = sum(1 for req in self._requests if req.failed)

        # Response categorization
        for req in self._requests:
            if req.response:
                status = req.response.status
                if 200 <= status < 400:
                    stats.successful_requests += 1
                elif status >= 400:
                    stats.error_responses += 1

                # Status code distribution
                status_str = str(status)
                stats.requests_by_status[status_str] = stats.requests_by_status.get(status_str, 0) + 1

            # Method distribution
            stats.requests_by_method[req.method] = stats.requests_by_method.get(req.method, 0) + 1

            # Domain distribution
            try:
                domain = urlparse(req.url).netloc
                stats.requests_by_domain[domain] = stats.requests_by_domain.get(domain, 0) + 1
            except:
                pass

        # Performance metrics
        durations = [req.duration for req in self._requests if req.duration is not None]
        if durations:
            stats.average_response_time = int(sum(durations) / len(durations))
            stats.slow_requests = sum(1 for d in durations if d > 1000)
            stats.fast_requests = sum(1 for d in durations if d <= 1000)

        # Timing
        timestamps = [req.timestamp for req in self._requests]
        if timestamps:
            stats.first_request_time = min(timestamps)
            stats.last_request_time = max(timestamps)

        # Cache result
        self._cached_stats = stats
        self._stats_dirty = False

        return stats

    async def export_har(self, filename: Optional[str] = None) -> str:
        """
        Export captured requests to HAR (HTTP Archive) format.

        HAR files can be imported into Chrome DevTools, Insomnia, Postman, etc.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"requests_{timestamp}.har"

        output_path = self.output_path / filename

        # Build HAR structure
        har = {
            "log": {
                "version": "1.2",
                "creator": {
                    "name": "MCPlaywright",
                    "version": "1.0"
                },
                "pages": [],
                "entries": []
            }
        }

        # Convert requests to HAR entries
        for req in self._requests:
            entry = {
                "startedDateTime": req.timestamp.isoformat(),
                "time": req.duration or 0,
                "request": {
                    "method": req.method,
                    "url": req.url,
                    "httpVersion": "HTTP/1.1",
                    "headers": [{"name": k, "value": v} for k, v in req.headers.items()],
                    "queryString": [],
                    "cookies": [],
                    "headersSize": -1,
                    "bodySize": len(req.post_data or "")
                },
                "response": {
                    "status": req.response.status if req.response else 0,
                    "statusText": req.response.status_text if req.response else "",
                    "httpVersion": "HTTP/1.1",
                    "headers": [{"name": k, "value": v} for k, v in (req.response.headers if req.response else {}).items()],
                    "cookies": [],
                    "content": {
                        "size": req.response.body_size if req.response else 0,
                        "mimeType": (req.response.headers.get("content-type", "text/plain") if req.response else "text/plain")
                    },
                    "redirectURL": "",
                    "headersSize": -1,
                    "bodySize": req.response.body_size if req.response else 0
                },
                "cache": {},
                "timings": {
                    "send": 0,
                    "wait": req.duration or 0,
                    "receive": 0
                }
            }

            har["log"]["entries"].append(entry)

        # Save HAR file
        self.output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(har, f, indent=2)

        logger.info(f"Exported {len(self._requests)} requests to HAR: {output_path}")
        return str(output_path)

    async def export_json(self, filename: Optional[str] = None) -> str:
        """Export captured requests to JSON format."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"requests_{timestamp}.json"

        output_path = self.output_path / filename

        # Convert requests to JSON-serializable format
        data = {
            "requests": [req.model_dump(mode='json') for req in self._requests],
            "statistics": self.get_statistics().model_dump(mode='json'),
            "export_timestamp": datetime.now().isoformat()
        }

        # Save JSON file
        self.output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Exported {len(self._requests)} requests to JSON: {output_path}")
        return str(output_path)
