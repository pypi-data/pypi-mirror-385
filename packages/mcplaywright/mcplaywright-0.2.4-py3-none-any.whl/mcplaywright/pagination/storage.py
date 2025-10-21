"""
Pluggable Storage Backends for Cursor Persistence

Provides multiple storage options for cursor data with automatic cleanup
of abandoned cursors and efficient memory management.
"""

import json
import time
import aiosqlite
import tempfile
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from .models import CursorState

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for cursor storage backends"""
    
    @abstractmethod
    async def store_cursor(self, cursor_id: str, cursor_state: CursorState) -> bool:
        """Store cursor state"""
        pass
    
    @abstractmethod
    async def retrieve_cursor(self, cursor_id: str) -> Optional[CursorState]:
        """Retrieve cursor state"""
        pass
    
    @abstractmethod
    async def delete_cursor(self, cursor_id: str) -> bool:
        """Delete cursor state"""
        pass
    
    @abstractmethod
    async def cleanup_expired(self, older_than: datetime) -> int:
        """Remove expired cursors, return count removed"""
        pass
    
    @abstractmethod
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage backend statistics"""
        pass
    
    @abstractmethod
    async def close(self):
        """Close storage backend and cleanup resources"""
        pass


class InMemoryStorage(StorageBackend):
    """In-memory storage backend (current implementation)"""

    def __init__(self):
        self._cursors: Dict[str, CursorState] = {}
        self._lock = asyncio.Lock()
    
    async def store_cursor(self, cursor_id: str, cursor_state: CursorState) -> bool:
        """Store cursor in memory"""
        try:
            async with self._lock:
                self._cursors[cursor_id] = cursor_state
            return True
        except Exception as e:
            logger.error(f"Failed to store cursor {cursor_id}: {e}")
            return False

    async def retrieve_cursor(self, cursor_id: str) -> Optional[CursorState]:
        """Retrieve cursor from memory"""
        async with self._lock:
            return self._cursors.get(cursor_id)

    async def delete_cursor(self, cursor_id: str) -> bool:
        """Delete cursor from memory"""
        try:
            async with self._lock:
                if cursor_id in self._cursors:
                    del self._cursors[cursor_id]
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete cursor {cursor_id}: {e}")
            return False

    async def cleanup_expired(self, older_than: datetime) -> int:
        """Remove expired cursors from memory"""
        removed_count = 0

        async with self._lock:
            expired_ids = [
                cursor_id for cursor_id, cursor_state in self._cursors.items()
                if cursor_state.expires_at < older_than
            ]

            for cursor_id in expired_ids:
                del self._cursors[cursor_id]
                removed_count += 1

        return removed_count

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get memory storage statistics"""
        async with self._lock:
            cursor_count = len(self._cursors)

            # Estimate memory usage
            import sys
            total_size = sum(sys.getsizeof(cursor) for cursor in self._cursors.values())

            return {
                "backend_type": "in_memory",
                "cursor_count": cursor_count,
                "estimated_memory_bytes": total_size,
                "estimated_memory_mb": total_size / (1024 * 1024)
            }

    async def close(self):
        """Close in-memory storage"""
        async with self._lock:
            self._cursors.clear()


class SQLiteStorage(StorageBackend):
    """Async SQLite-based cursor storage with automatic cleanup"""

    def __init__(self, db_path: Optional[str] = None, cleanup_interval_minutes: int = 30):
        self.db_path = db_path or str(Path(tempfile.gettempdir()) / "mcplaywright_cursors.db")
        self.cleanup_interval_minutes = cleanup_interval_minutes
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
        
    async def _ensure_connection(self):
        """Ensure async database connection is established"""
        if self._connection is None:
            async with self._lock:
                if self._connection is None:
                    self._connection = await aiosqlite.connect(
                        self.db_path,
                        timeout=30.0
                    )

                    # Enable WAL mode for better concurrent access
                    await self._connection.execute("PRAGMA journal_mode=WAL")
                    await self._connection.execute("PRAGMA synchronous=NORMAL")

                    # Create cursors table
                    await self._connection.execute("""
                        CREATE TABLE IF NOT EXISTS cursors (
                            cursor_id TEXT PRIMARY KEY,
                            session_id TEXT NOT NULL,
                            tool_name TEXT NOT NULL,
                            cursor_data TEXT NOT NULL,
                            created_at REAL NOT NULL,
                            expires_at REAL NOT NULL,
                            last_accessed REAL NOT NULL,
                            data_size_bytes INTEGER NOT NULL
                        )
                    """)

                    # Create indexes separately
                    await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON cursors(session_id)")
                    await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cursors(expires_at)")
                    await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON cursors(last_accessed)")

                    await self._connection.commit()
    
    def _serialize_cursor(self, cursor_state: CursorState) -> str:
        """Serialize cursor state to JSON"""
        cursor_dict = {
            "id": cursor_state.id,
            "session_id": cursor_state.session_id,
            "tool_name": cursor_state.tool_name,
            "query_state": cursor_state.query_state,
            "position": cursor_state.position,
            "created_at": cursor_state.created_at.timestamp(),
            "last_accessed": cursor_state.last_accessed.timestamp(),
            "expires_at": cursor_state.expires_at.timestamp(),
            "direction": cursor_state.direction,
            "chunk_size_history": cursor_state.chunk_size_history,
            "performance_metrics": cursor_state.performance_metrics,
            "cached_positions": cursor_state.cached_positions,
            "result_count": cursor_state.result_count,
            "metadata": cursor_state.metadata
        }
        return json.dumps(cursor_dict, default=str)
    
    def _deserialize_cursor(self, cursor_data: str) -> CursorState:
        """Deserialize cursor state from JSON"""
        cursor_dict = json.loads(cursor_data)
        
        cursor_state = CursorState(
            id=cursor_dict["id"],
            session_id=cursor_dict["session_id"],
            tool_name=cursor_dict["tool_name"],
            query_state=cursor_dict["query_state"],
            position=cursor_dict["position"],
            created_at=datetime.fromtimestamp(cursor_dict["created_at"]),
            last_accessed=datetime.fromtimestamp(cursor_dict["last_accessed"]),
            expires_at=datetime.fromtimestamp(cursor_dict["expires_at"]),
            direction=cursor_dict.get("direction", "forward"),
            chunk_size_history=cursor_dict.get("chunk_size_history", []),
            performance_metrics=cursor_dict.get("performance_metrics", {}),
            cached_positions=cursor_dict.get("cached_positions", {}),
            result_count=cursor_dict.get("result_count", 0),
            metadata=cursor_dict.get("metadata", {})
        )
        
        return cursor_state
    
    async def store_cursor(self, cursor_id: str, cursor_state: CursorState) -> bool:
        """Store cursor in async SQLite"""
        try:
            await self._ensure_connection()

            cursor_data = self._serialize_cursor(cursor_state)
            data_size = len(cursor_data.encode('utf-8'))

            async with self._lock:
                await self._connection.execute("""
                    INSERT OR REPLACE INTO cursors
                    (cursor_id, session_id, tool_name, cursor_data, created_at,
                     expires_at, last_accessed, data_size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cursor_id,
                    cursor_state.session_id,
                    cursor_state.tool_name,
                    cursor_data,
                    cursor_state.created_at.timestamp(),
                    cursor_state.expires_at.timestamp(),
                    cursor_state.last_accessed.timestamp(),
                    data_size
                ))

                await self._connection.commit()

            return True

        except Exception as e:
            logger.error(f"Failed to store cursor {cursor_id} in aiosqlite: {e}")
            return False
    
    async def retrieve_cursor(self, cursor_id: str) -> Optional[CursorState]:
        """Retrieve cursor from async SQLite"""
        try:
            await self._ensure_connection()

            async with self._lock:
                async with self._connection.execute(
                    "SELECT cursor_data FROM cursors WHERE cursor_id = ?",
                    (cursor_id,)
                ) as cursor:
                    row = await cursor.fetchone()

                if row:
                    cursor_state = self._deserialize_cursor(row[0])

                    # Update last accessed time
                    now = datetime.now()
                    cursor_state.last_accessed = now

                    await self._connection.execute(
                        "UPDATE cursors SET last_accessed = ? WHERE cursor_id = ?",
                        (now.timestamp(), cursor_id)
                    )
                    await self._connection.commit()

                    return cursor_state

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve cursor {cursor_id} from aiosqlite: {e}")
            return None

    async def delete_cursor(self, cursor_id: str) -> bool:
        """Delete cursor from async SQLite"""
        try:
            await self._ensure_connection()

            async with self._lock:
                cursor = await self._connection.execute(
                    "DELETE FROM cursors WHERE cursor_id = ?",
                    (cursor_id,)
                )
                await self._connection.commit()

                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Failed to delete cursor {cursor_id} from aiosqlite: {e}")
            return False

    async def cleanup_expired(self, older_than: datetime) -> int:
        """Remove expired cursors from async SQLite"""
        try:
            await self._ensure_connection()

            async with self._lock:
                cursor = await self._connection.execute(
                    "DELETE FROM cursors WHERE expires_at < ?",
                    (older_than.timestamp(),)
                )
                await self._connection.commit()

                return cursor.rowcount

        except Exception as e:
            logger.error(f"Failed to cleanup expired cursors from aiosqlite: {e}")
            return 0

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get async SQLite storage statistics"""
        try:
            await self._ensure_connection()

            async with self._lock:
                # Get cursor count and total data size
                async with self._connection.execute("""
                    SELECT
                        COUNT(*) as cursor_count,
                        SUM(data_size_bytes) as total_data_bytes,
                        AVG(data_size_bytes) as avg_cursor_size,
                        MIN(created_at) as oldest_cursor,
                        MAX(last_accessed) as most_recent_access
                    FROM cursors
                """) as cursor:
                    stats = await cursor.fetchone()

                # Get database file size
                db_path = Path(self.db_path)
                file_size_bytes = db_path.stat().st_size if db_path.exists() else 0

                return {
                    "backend_type": "aiosqlite",
                    "db_path": self.db_path,
                    "cursor_count": stats[0] or 0,
                    "total_data_bytes": stats[1] or 0,
                    "total_data_mb": (stats[1] or 0) / (1024 * 1024),
                    "avg_cursor_size_bytes": stats[2] or 0,
                    "avg_cursor_size_kb": (stats[2] or 0) / 1024,
                    "db_file_size_bytes": file_size_bytes,
                    "db_file_size_mb": file_size_bytes / (1024 * 1024),
                    "oldest_cursor": datetime.fromtimestamp(stats[3]) if stats[3] else None,
                    "most_recent_access": datetime.fromtimestamp(stats[4]) if stats[4] else None
                }

        except Exception as e:
            logger.error(f"Failed to get aiosqlite storage stats: {e}")
            return {"backend_type": "aiosqlite", "error": str(e)}

    async def close(self):
        """Close async SQLite connection"""
        async with self._lock:
            if self._connection:
                await self._connection.close()
                self._connection = None




def create_storage_backend(backend_type: str, **kwargs) -> StorageBackend:
    """Factory function to create storage backends"""

    if backend_type == "memory":
        return InMemoryStorage()
    elif backend_type == "sqlite":
        return SQLiteStorage(**kwargs)
    else:
        raise ValueError(f"Unknown storage backend: {backend_type}. Available: memory, sqlite")