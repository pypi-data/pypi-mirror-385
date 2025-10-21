"""Configuration module - Logger configurations for various platforms"""

from .base import LogConfig
from .console import ConsoleLogConfig
from .cloud import (
    LogCloudConfig,
    DatadogLogConfig,
    AWSCloudWatchLogConfig,
    GCPLoggingConfig,
    AzureLogAnalyticsConfig
)
from .multi_handler import MultiHandler_LogConfig, HandlerConfig
from .factory import (
    create_console_config,
    create_file_config,
    create_console_file_config,
    create_console_datadog_config,
    create_console_file_datadog_config,
    create_file_datadog_config
)

__all__ = [
    # Base config
    'LogConfig',
    'ConsoleLogConfig',
    
    # Cloud configs
    'LogCloudConfig',
    'DatadogLogConfig',
    'AWSCloudWatchLogConfig',
    'GCPLoggingConfig',
    'AzureLogAnalyticsConfig',
    
    # Multi-handler config
    'MultiHandler_LogConfig',
    'HandlerConfig',
    
    # Factory functions
    'create_console_config',
    'create_file_config',
    'create_console_file_config',
    'create_console_datadog_config',
    'create_console_file_datadog_config',
    'create_file_datadog_config',
]