from typing import List
from abc import ABC, abstractmethod

from ..configs.base import LogConfig
from ..client.models import LogEntry


class LogHandler(ABC):
    """Base class for log handlers"""

    def __init__(self, config: LogConfig):
        self.config = config

    @abstractmethod
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write log entries to destination"""
        pass

    @abstractmethod
    async def flush(self) -> bool:
        """Flush any buffered entries"""
        pass

    async def close(self):
        """Clean up resources"""
        pass
