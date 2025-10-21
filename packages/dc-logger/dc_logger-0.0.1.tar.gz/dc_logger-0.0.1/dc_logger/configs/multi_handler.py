from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .base import LogConfig
from .console import ConsoleLogConfig
from .cloud import DatadogLogConfig
from ..client.enums import LogLevel


@dataclass
class HandlerConfig:
    type: str
    config: LogConfig
    platform_config: Optional[Dict[str, Any]] = None

    @classmethod
    def from_config(cls, config: LogConfig):
        hc = cls(
            type=config.output_mode,
            config=config,
        )

        if hasattr(config, 'to_platform_config') and callable(getattr(config, 'to_platform_config')):
            hc.platform_config = config.to_platform_config()

        return hc

@dataclass
class MultiHandler_LogConfig(LogConfig):
    """Configuration that supports multiple handlers simultaneously"""

    handlers: List[HandlerConfig] = field(default_factory=list)
    output_mode: str = "multi"

    def get_cloud_config(self) -> Dict[str, Any]:
        """Return empty config since this handles multiple providers"""
        return {"cloud_provider": "multi"}

    def validate_config(self) -> bool:
        """Validate all handler configurations"""
        for handler in self.handlers:
            if not handler.config.validate_config():
                return False
        return True

    def get_handler_configs(self) -> List[Dict[str, Any]]:
        """Return all handler configurations"""
        return [
            {
                "type": handler.type,
                "config": handler.config,
                "cloud_config": (
                    handler.config.to_platform_config()
                    if handler.type == "cloud"
                    else None
                ),
            }
            for handler in self.handlers
        ]

    @classmethod
    def create(
        cls,
        handlers: List[Dict[str, Any]],
        level: LogLevel = LogLevel.INFO,
        batch_size: int = 100,
        flush_interval: int = 30,
        **kwargs
    ) -> "MultiHandlerLogConfig":
        """Create a multi-handler configuration with custom handlers"""
        handler_configs = [
            HandlerConfig(type=h["type"], config=h["config"]) for h in handlers
        ]
        return cls(
            handlers=handler_configs,
            level=level,
            batch_size=batch_size,
            flush_interval=flush_interval,
            **kwargs
        )
