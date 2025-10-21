# DC Logger Examples

Complete examples demonstrating all functionality of the dc_logger library.

## 📚 Examples Index

### Core Concepts

1. **[01_basic_logs.ipynb](01_basic_logs.ipynb)** - LogEntry, LogLevel, and Context Objects
   - Creating log entries at different levels
   - Adding context (Entity, HTTPDetails, MultiTenant, Correlation)
   - Serialization (to_dict, to_json)
   - Working with CorrelationManager

2. **[02_extractors.ipynb](02_extractors.ipynb)** - Context Extractors
   - Default extractors (KwargsEntityExtractor, KwargsHTTPDetailsExtractor, etc.)
   - Creating custom extractors
   - ResultProcessor implementations
   - Real-world extractor examples

3. **[03_decorators.ipynb](03_decorators.ipynb)** - Function Decorators
   - Basic `@log_call` usage
   - LogDecoratorConfig options
   - Custom extractors with decorators
   - Error handling
   - Sensitive data sanitization
   - Dependency injection

### Service Handlers & Logging

4. **[04_console_logging.ipynb](04_console_logging.ipynb)** - Console Logging
   - ConsoleHandler setup
   - Console_ServiceConfig
   - JSON vs Text output
   - Pretty printing
   - Using factory functions

5. **[05_file_logging.ipynb](05_file_logging.ipynb)** - File Logging
   - FileHandler setup
   - File_ServiceConfig
   - JSON, Text, and CSV formats
   - Append vs Overwrite modes
   - Directory creation
   - Error handling

6. **[06_cloud_logging.ipynb](06_cloud_logging.ipynb)** - Cloud Logging (Datadog)
   - DatadogHandler setup
   - Datadog_ServiceConfig
   - API key configuration
   - Site selection
   - Log format conversion
   - Testing with mock endpoints

7. **[07_multi_handler.ipynb](07_multi_handler.ipynb)** - Multi-Handler Logging
   - Logging to multiple destinations
   - Console + File
   - Console + Datadog
   - Console + File + Datadog
   - Handler orchestration
   - Factory functions for multi-handler configs

### Complete Workflows

8. **[08_complete_workflow.ipynb](08_complete_workflow.ipynb)** - End-to-End Examples
   - E-commerce platform example
   - API service example
   - Data processing pipeline example
   - Custom extractors + handlers + decorators
   - Real-world patterns

9. **[09_advanced_patterns.ipynb](09_advanced_patterns.ipynb)** - Advanced Patterns
   - Correlation and distributed tracing
   - Multi-tenant scenarios
   - Batching and buffering
   - Performance optimization
   - Testing strategies

## 🚀 Quick Start

### Basic Logging
```python
from dc_logger.client.Log import LogEntry, LogLevel

entry = LogEntry.create(
    level=LogLevel.INFO,
    message="Hello, World!",
    app_name="my_app"
)
print(entry.to_json())
```

### With Decorator
```python
from dc_logger.client.decorators import log_call

@log_call()
async def my_function():
    return "success"
```

### Console Logging
```python
from dc_logger.services.console.base import ConsoleHandler, Console_ServiceConfig
from dc_logger.client.base import Handler_BufferSettings

config = Console_ServiceConfig(output_mode="console")
buffer_settings = Handler_BufferSettings()
handler = ConsoleHandler(
    service_config=config,
    buffer_settings=buffer_settings
)
```

## 📖 Learning Path

**Beginners**: Start with 01 → 02 → 03 → 04  
**Intermediate**: 05 → 06 → 07  
**Advanced**: 08 → 09

## 🔗 Additional Resources

- [Architecture Documentation](../nbs/client/DECORATOR_ARCHITECTURE.md)
- [Test Plan](../TEST_PLAN.md)
- [API Documentation](../nbs/index.md)

## 💡 Tips

- Run notebooks in order for first-time learning
- Each notebook is self-contained and can run independently
- Check the test.ipynb for quick demonstrations
- Modify examples to experiment with features

