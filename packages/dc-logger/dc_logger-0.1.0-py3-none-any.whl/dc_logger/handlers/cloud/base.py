from typing import List
from abc import abstractmethod

from ...client.models import LogEntry
from ...client.exceptions import LogWriteError
from ..base import LogHandler


class CloudHandler(LogHandler):
    """Base class for cloud log handlers"""

    def __init__(self, config):
        super().__init__(config)
        self.cloud_config = config.to_platform_config()
        config.validate_config()

    @abstractmethod
    async def _send_to_cloud(self, entries: List[LogEntry]) -> bool:
        """Send entries to cloud provider"""
        pass

    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to cloud provider"""
        try:
            return await self._send_to_cloud(entries)
        except Exception as e:
            raise LogWriteError(f"Error sending logs to cloud provider: {e}")

    async def flush(self) -> bool:
        """Cloud handlers may need batching, implement in subclasses"""
        return True
