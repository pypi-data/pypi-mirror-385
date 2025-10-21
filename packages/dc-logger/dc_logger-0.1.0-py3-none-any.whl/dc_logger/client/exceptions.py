# Logging-specific exceptions
class LoggingError(Exception):
    """Base exception for logging errors"""

    pass


class LogHandlerError(LoggingError):
    """Exception for log handler errors"""

    pass


class LogConfigError(LoggingError):
    """Exception for log configuration errors"""

    pass


class LogWriteError(LoggingError):
    """Exception for log write errors"""

    pass


class LogFlushError(LoggingError):
    """Exception for log flush errors"""

    pass
