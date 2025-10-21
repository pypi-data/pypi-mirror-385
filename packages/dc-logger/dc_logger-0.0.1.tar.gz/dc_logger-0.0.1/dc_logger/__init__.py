"""
DC Logger - Structured logging system for Domo applications

A comprehensive logging framework with support for:
- Multiple output handlers (console, file, cloud)
- Structured logging with JSON support
- Correlation tracking for distributed tracing
- Cloud integrations (Datadog, AWS CloudWatch, GCP, Azure)
- Async and sync support
- Decorator-based automatic logging
"""

from .logger import DC_Logger, get_logger, set_global_logger
from .client import (
    LogLevel,
    LogEntry,
    Entity,
    HTTPDetails,
    Correlation,
    MultiTenant,
    correlation_manager,
)
from .configs import (
    LogConfig,
    ConsoleLogConfig,
    DatadogLogConfig,
    AWSCloudWatchLogConfig,
    GCPLoggingConfig,
    AzureLogAnalyticsConfig,
    MultiHandler_LogConfig,
    create_console_config,
    create_file_config,
    create_console_file_config,
    create_console_datadog_config,
    create_console_file_datadog_config,
    create_file_datadog_config,
)
from .decorators import log_function_call
from .utils import extract_entity_from_args

__version__ = "1.0.0"

__all__ = [
    # Main logger
    "DC_Logger",
    "get_logger",
    "set_global_logger",
    # Core types
    "LogLevel",
    "LogEntry",
    "Entity",
    "HTTPDetails",
    "Correlation",
    "MultiTenant",
    "correlation_manager",
    # Configurations
    "LogConfig",
    "ConsoleLogConfig",
    "DatadogLogConfig",
    "AWSCloudWatchLogConfig",
    "GCPLoggingConfig",
    "AzureLogAnalyticsConfig",
    "MultiHandler_LogConfig",
    # Factory functions
    "create_console_config",
    "create_file_config",
    "create_console_file_config",
    "create_console_datadog_config",
    "create_console_file_datadog_config",
    "create_file_datadog_config",
    # Decorators and utilities
    "log_function_call",
    "extract_entity_from_args",
]
