# DC Logger Architecture

## Overview

DC Logger is a structured logging system designed for Domo applications with support for multiple output handlers, correlation tracking, and cloud integrations.

## Project Structure

```
dc_logger/
├── client/                      # Core data models and utilities
│   ├── __init__.py             # Module exports
│   ├── correlation.py          # CorrelationManager for distributed tracing
│   ├── enums.py                # LogLevel enum
│   ├── exceptions.py           # Custom exceptions
│   └── models.py               # Data models (LogEntry, Entity, HTTPDetails, etc.)
│
├── configs/                     # Configuration classes
│   ├── __init__.py             # Module exports
│   ├── base.py                 # Base LogConfig abstract class
│   ├── console.py              # ConsoleLogConfig
│   ├── cloud.py                # Cloud provider configs (Datadog, AWS, GCP, Azure)
│   ├── multi_handler.py        # Multi-handler configuration
│   └── factory.py              # Factory functions for common configs
│
├── handlers/                    # Log output handlers
│   ├── __init__.py             # Module exports
│   ├── base.py                 # LogHandler abstract base class
│   ├── console.py              # ConsoleHandler for stdout
│   ├── file.py                 # FileHandler for file output
│   └── cloud/                  # Cloud platform handlers
│       ├── __init__.py         # Module exports
│       ├── base.py             # CloudHandler abstract base
│       ├── datadog.py          # DatadogHandler
│       ├── aws.py              # AWSCloudWatchHandler
│       ├── gcp.py              # GCPLoggingHandler
│       └── azure.py            # AzureLogAnalyticsHandler
│
├── __init__.py                  # Package exports
├── logger.py                    # Main DC_Logger class
├── decorators.py                # @log_function_call decorator
├── utils.py                     # Utility functions
└── readme.md                    # Project documentation
```

## Design Principles

### SOLID Principles

1. **Single Responsibility Principle (SRP)**
   - Each class has one clear purpose
   - `LogEntry` handles log data, `DC_Logger` handles logging operations
   - Handlers are responsible only for their specific output destination

2. **Open/Closed Principle (OCP)**
   - Easily extensible through abstract base classes
   - New handlers can be added without modifying existing code
   - New configurations can be created by extending `LogConfig`

3. **Liskov Substitution Principle (LSP)**
   - All handlers implement the same `LogHandler` interface
   - Configurations are interchangeable through `LogConfig` base class

4. **Interface Segregation Principle (ISP)**
   - Handlers only implement methods they need
   - Cloud handlers extend base handler with cloud-specific methods

5. **Dependency Inversion Principle (DIP)**
   - `DC_Logger` depends on `LogHandler` abstraction, not concrete implementations
   - Configuration classes use abstract base for flexibility

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `DC_Logger`, `ConsoleHandler`)
- **Functions**: `snake_case` (e.g., `get_logger`, `create_console_config`)
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: Prefixed with `_` (e.g., `_setup_handlers`)

## Key Components

### 1. Core Models (`client/`)

#### LogEntry
Structured log entry with all contextual information:
- Timestamp, level, message, logger name
- Business context (user, action, entity, status, duration)
- Distributed tracing (correlation IDs)
- Multi-tenant information
- HTTP details
- Extra metadata

#### Entity
Represents logged entities (datasets, users, cards, etc.):
- Type, ID, name
- Additional metadata
- Factory method to create from Domo entities

#### CorrelationManager
Manages correlation IDs for distributed tracing:
- Trace ID (across multiple services)
- Request ID (per request)
- Session ID (per user session)
- Span ID (per operation)

### 2. Configurations (`configs/`)

#### Base Configuration
`LogConfig` - Abstract base class for all configurations
- Common settings: level, output_mode, format, batch_size, flush_interval
- Abstract methods: `validate_config()`, `to_platform_config()`
- Default implementation of `get_handler_configs()`

#### Console Configuration
`ConsoleLogConfig` - For console output
- Supports JSON and text formats
- Pretty-print option for development

#### Cloud Configurations
- `DatadogLogConfig` - Datadog integration
- `AWSCloudWatchLogConfig` - AWS CloudWatch
- `GCPLoggingConfig` - Google Cloud Logging
- `AzureLogAnalyticsConfig` - Azure Log Analytics

#### Multi-Handler Configuration
`MultiHandler_LogConfig` - Multiple handlers simultaneously
- Supports any combination of handlers
- Unified configuration

#### Factory Functions
Convenience functions for common configurations:
- `create_console_config()` - Simple console logging
- `create_file_config()` - File logging
- `create_console_file_config()` - Console + file
- `create_console_datadog_config()` - Console + Datadog
- `create_console_file_datadog_config()` - Console + file + Datadog
- `create_file_datadog_config()` - File + Datadog

### 3. Handlers (`handlers/`)

#### Base Handler
`LogHandler` - Abstract base for all handlers
- `write(entries)` - Write log entries
- `flush()` - Flush buffered entries
- `close()` - Clean up resources

#### Console Handler
`ConsoleHandler` - Writes to stdout
- Supports JSON and text formats
- Pretty-print for development

#### File Handler
`FileHandler` - Writes to files
- Automatic directory creation
- Append mode
- Error handling for permissions/IO

#### Cloud Handler
`CloudHandler` - Base for cloud handlers
- `_send_to_cloud(entries)` - Abstract method for cloud integration
- Validation and error handling

#### Specific Cloud Handlers
- `DatadogHandler` - Direct HTTP API integration
- `AWSCloudWatchHandler` - AWS integration (TODO)
- `GCPLoggingHandler` - GCP integration (TODO)
- `AzureLogAnalyticsHandler` - Azure integration (TODO)

### 4. Main Logger (`logger.py`)

#### DC_Logger
Main logger class with:
- **Async-first design** with background flush task
- **Buffer management** with configurable batch size
- **Multiple handlers** support
- **Correlation tracking** integration
- **Convenience methods** (debug, info, warning, error, critical)
- **Context management** (start_request, end_request)

#### Global Logger Functions
- `get_logger(app_name)` - Get or create global logger
- `set_global_logger(logger)` - Set global logger instance

### 5. Decorators (`decorators.py`)

#### @log_function_call
Automatic function call logging:
- Captures function parameters (sanitized)
- Measures execution time
- Logs results or errors
- Extracts entity information from arguments
- Handles both async and sync functions
- Pagination request detection

### 6. Utilities (`utils.py`)

#### extract_entity_from_args
Extracts entity information from function arguments:
- Detects Domo entity objects
- Parses entity IDs from parameters
- Extracts entity info from URLs

## Usage Examples

### Basic Console Logging

```python
from dc_logger import get_logger, LogLevel

logger = get_logger("myapp")

await logger.info("Application started")
await logger.error("Something went wrong", extra={"error_code": 500})
```

### Console + File Logging

```python
from dc_logger import DC_Logger, create_console_file_config

config = create_console_file_config(
    file_path="logs/app.log",
    level=LogLevel.INFO,
    pretty_print=True
)
logger = DC_Logger(config, "myapp")

await logger.info("Logging to both console and file")
```

### Datadog Integration

```python
from dc_logger import DC_Logger, create_console_datadog_config

config = create_console_datadog_config(
    datadog_api_key="your-api-key",
    datadog_service="myapp",
    datadog_env="production"
)
logger = DC_Logger(config, "myapp")

await logger.info("Sent to both console and Datadog")
```

### Using the Decorator

```python
from dc_logger import log_function_call, LogLevel

@log_function_call(
    action_name="fetch_data",
    include_params=True,
    log_level=LogLevel.INFO
)
async def fetch_user_data(user_id: str):
    # Your code here
    return data
```

### Structured Logging with Context

```python
from dc_logger import get_logger, Entity, HTTPDetails

logger = get_logger("myapp")

entity = Entity(type="dataset", id="abc123", name="Sales Data")
http_details = HTTPDetails(method="GET", url="/api/data", status_code=200)

await logger.info(
    "Data fetched successfully",
    action="fetch_data",
    entity=entity,
    http_details=http_details,
    duration_ms=250,
    extra={"rows": 1000}
)
```

## Extension Points

### Adding a New Handler

1. Create a new handler class inheriting from `LogHandler` or `CloudHandler`
2. Implement required methods: `write()`, `flush()`, `close()`
3. Add to `handlers/__init__.py` exports
4. Update `DC_Logger._setup_handlers()` to support it

### Adding a New Configuration

1. Create config class inheriting from `LogConfig`
2. Implement `validate_config()` and `to_platform_config()`
3. Add to `configs/__init__.py` exports
4. Create factory function in `configs/factory.py`

### Adding a New Cloud Provider

1. Create handler in `handlers/cloud/`
2. Inherit from `CloudHandler`
3. Implement `_send_to_cloud()`
4. Create corresponding config in `configs/LogConfig_Cloud.py`
5. Update exports and factory functions

## Best Practices

1. **Use factory functions** for common configurations
2. **Use the decorator** for automatic function logging
3. **Always await** async methods (log, flush, close)
4. **Provide context** in log calls (entity, action, etc.)
5. **Use structured logging** with extra fields instead of string concatenation
6. **Set appropriate log levels** based on environment
7. **Close logger** properly on application shutdown
8. **Use correlation IDs** for distributed tracing

## Future Enhancements

- [ ] Complete AWS CloudWatch implementation
- [ ] Complete GCP Logging implementation
- [ ] Complete Azure Log Analytics implementation
- [ ] Add log filtering/sampling
- [ ] Add log rotation for file handler
- [ ] Add metrics and monitoring
- [ ] Add log encryption
- [ ] Add webhook handler
- [ ] Add database handler
- [ ] Performance optimizations
