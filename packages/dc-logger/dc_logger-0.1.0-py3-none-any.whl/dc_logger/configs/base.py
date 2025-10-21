import os
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass
from abc import ABC, abstractmethod

from ..client.enums import LogLevel
from ..client.exceptions import LogConfigError


# Type for valid output modes
OutputMode = Literal["cloud", "console", "file"]


@dataclass
class LogConfig(ABC):
    """Abstract base configuration for logging system"""

    level: LogLevel = LogLevel.INFO
    output_mode: OutputMode = "console"  # cloud, console, or file
    format: str = "json"  # json, text
    destination: Optional[str] = None  # file path, webhook URL, etc.
    batch_size: int = 100
    flush_interval: int = 30  # seconds
    correlation_enabled: bool = True
    include_traceback: bool = True
    max_buffer_size: int = 1000
    pretty_print: bool = False  # Pretty print JSON for development

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the configuration"""
        raise NotImplementedError()

    def get_handler_configs(self) -> List[Dict[str, Any]]:
        """Get handler configurations for this config. Default implementation returns single handler."""
        return [{
            "type": self.output_mode,
            "config": self,
            "cloud_config": self.to_platform_config() if self.output_mode == "cloud" else None
        }]
