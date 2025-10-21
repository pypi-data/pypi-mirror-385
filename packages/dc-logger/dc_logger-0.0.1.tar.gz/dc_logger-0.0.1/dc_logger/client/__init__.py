"""Client module - Core data models, exceptions, and utilities"""

from .enums import LogLevel
from .exceptions import (
    LoggingError,
    LogHandlerError,
    LogConfigError,
    LogWriteError,
    LogFlushError
)
from .models import (
    Entity,
    HTTPDetails,
    Correlation,
    MultiTenant,
    LogEntry
)
from .correlation import CorrelationManager, correlation_manager

__all__ = [
    # Enums
    'LogLevel',
    
    # Exceptions
    'LoggingError',
    'LogHandlerError',
    'LogConfigError',
    'LogWriteError',
    'LogFlushError',
    
    # Models
    'Entity',
    'HTTPDetails',
    'Correlation',
    'MultiTenant',
    'LogEntry',
    
    # Correlation
    'CorrelationManager',
    'correlation_manager',
]