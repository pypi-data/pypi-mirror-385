"""
HTTP Request/Response Models

Structured models for request monitoring and analysis.
"""

from typing import Dict, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class RequestHeaders(BaseModel):
    """HTTP request headers"""
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")


class ResponseHeaders(BaseModel):
    """HTTP response headers"""
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")


class RequestFailure(BaseModel):
    """Request failure information"""
    error_text: str = Field(description="Error message for failed request")
    timestamp: datetime = Field(default_factory=datetime.now, description="Failure timestamp")


class ResponseInfo(BaseModel):
    """HTTP response information"""
    status: int = Field(description="HTTP status code")
    status_text: str = Field(description="HTTP status text")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    body: Optional[str] = Field(None, description="Response body (if captured)")
    body_size: int = Field(0, description="Response body size in bytes")
    from_cache: bool = Field(False, description="Whether response was served from cache")
    duration: Optional[int] = Field(None, description="Response duration in milliseconds")


class InterceptedRequest(BaseModel):
    """
    Complete captured HTTP request with response and timing information.

    This model captures all information about browser HTTP requests including:
    - Request details (URL, method, headers, body)
    - Response details (status, headers, body, caching)
    - Timing information (duration, timestamps)
    - Failure information (if request failed)
    """
    # Request information
    url: str = Field(description="Request URL")
    method: str = Field(description="HTTP method (GET, POST, etc.)")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    post_data: Optional[str] = Field(None, description="Request body/post data")
    resource_type: str = Field(description="Resource type (document, script, xhr, etc.)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")

    # Response information (populated when response received)
    response: Optional[ResponseInfo] = Field(None, description="Response information")

    # Timing information
    duration: Optional[int] = Field(None, description="Total request duration in milliseconds")

    # Failure information
    failed: bool = Field(False, description="Whether the request failed")
    failure: Optional[RequestFailure] = Field(None, description="Failure details")

    # Metadata
    request_id: str = Field(description="Unique request identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://api.example.com/data",
                "method": "GET",
                "headers": {"user-agent": "Mozilla/5.0"},
                "resource_type": "xhr",
                "timestamp": "2025-10-20T17:51:00.000Z",
                "response": {
                    "status": 200,
                    "status_text": "OK",
                    "headers": {"content-type": "application/json"},
                    "body_size": 1024,
                    "from_cache": False,
                    "duration": 145
                },
                "duration": 145,
                "failed": False,
                "request_id": "req_001"
            }
        }


class RequestStatistics(BaseModel):
    """
    Aggregated statistics for captured requests.

    Provides comprehensive analytics including success/failure rates,
    performance metrics, and categorization by method, status, and domain.
    """
    total_requests: int = Field(0, description="Total number of requests")
    successful_requests: int = Field(0, description="Successful requests (2xx/3xx)")
    failed_requests: int = Field(0, description="Failed requests (network failures)")
    error_responses: int = Field(0, description="Error responses (4xx/5xx)")

    # Performance metrics
    average_response_time: int = Field(0, description="Average response time in ms")
    slow_requests: int = Field(0, description="Requests taking >1s")
    fast_requests: int = Field(0, description="Requests taking <1s")

    # Categorization
    requests_by_method: Dict[str, int] = Field(default_factory=dict, description="Request count by HTTP method")
    requests_by_status: Dict[str, int] = Field(default_factory=dict, description="Request count by status code")
    requests_by_domain: Dict[str, int] = Field(default_factory=dict, description="Request count by domain")

    # Timing
    first_request_time: Optional[datetime] = Field(None, description="Timestamp of first request")
    last_request_time: Optional[datetime] = Field(None, description="Timestamp of last request")

    class Config:
        json_schema_extra = {
            "example": {
                "total_requests": 45,
                "successful_requests": 40,
                "failed_requests": 2,
                "error_responses": 3,
                "average_response_time": 234,
                "slow_requests": 5,
                "fast_requests": 40,
                "requests_by_method": {"GET": 35, "POST": 10},
                "requests_by_status": {"200": 38, "404": 3, "500": 2},
                "requests_by_domain": {"api.example.com": 25, "cdn.example.com": 20}
            }
        }
