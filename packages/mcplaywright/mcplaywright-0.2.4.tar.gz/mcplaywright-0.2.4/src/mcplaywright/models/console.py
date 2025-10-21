"""
Console Message Models

Structured console message capture with source tracking and timestamps.
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


ConsoleMessageType = Literal["log", "info", "warning", "error", "debug", "dir", "dirxml",
                             "table", "trace", "clear", "startGroup", "startGroupCollapsed",
                             "endGroup", "assert", "profile", "profileEnd", "count", "timeEnd"]


class ConsoleMessageLocation(BaseModel):
    """Location information for console message source."""
    url: str = Field(description="Source file URL")
    line_number: int = Field(description="Line number in source file")
    column_number: int = Field(default=0, description="Column number in source file")


class ConsoleMessage(BaseModel):
    """
    Structured console message with type, text, location, and timestamp.

    Captures all information from browser console including source location
    for easy debugging and filtering.
    """
    type: ConsoleMessageType = Field(description="Message type (log, error, warning, etc.)")
    text: str = Field(description="Message text content")
    location: ConsoleMessageLocation = Field(description="Source location of the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="When message was captured")
    args_count: int = Field(default=0, description="Number of arguments in console call")

    def __str__(self) -> str:
        """Format message for display with type, text, and location."""
        type_str = self.type.upper()
        location_str = f"{self.location.url}:{self.location.line_number}"
        time_str = self.timestamp.strftime("%H:%M:%S.%f")[:-3]  # milliseconds
        return f"[{time_str}] [{type_str}] {self.text} @ {location_str}"

    def matches_type(self, filter_type: str) -> bool:
        """Check if message matches type filter."""
        if filter_type == "all":
            return True
        if filter_type == "log":
            # 'log' filter includes 'log' and 'info'
            return self.type in ("log", "info")
        return self.type == filter_type

    def matches_search(self, search_term: str) -> bool:
        """Check if message contains search term (case-insensitive)."""
        if not search_term:
            return True
        search_lower = search_term.lower()
        return (
            search_lower in self.text.lower() or
            search_lower in self.location.url.lower() or
            search_lower in self.type.lower()
        )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "error",
                "text": "Uncaught TypeError: Cannot read property 'foo' of undefined",
                "location": {
                    "url": "https://example.com/app.js",
                    "line_number": 42,
                    "column_number": 15
                },
                "timestamp": "2024-01-15T10:30:45.123Z",
                "args_count": 1
            }
        }
