import inspect
import time
import asyncio
import json
from typing import Optional
from functools import wraps

from .client.enums import LogLevel
from .client.models import LogEntry, Entity, HTTPDetails, Correlation, MultiTenant
from .utils import (
    extract_entity_from_args,
    _find_calling_context,
    create_dynamic_action_name,
)


def log_function_call(
    action_name: Optional[str] = None,
    include_params: bool = False,
    include_result: bool = False,
    logger=None,
    log_level: LogLevel = LogLevel.INFO,
    suppress_repeated_calls: bool = True,
):
    """
    Decorator to automatically log function calls with comprehensive context.

    Args:
        action_name: Custom action name, defaults to function name
        include_params: Whether to log function parameters (sanitized)
        include_result: Whether to log function result (sanitized)
        logger: Specific logger instance, defaults to global logger
        log_level: Log level for the function call
        suppress_repeated_calls: Whether to suppress logging for repeated calls (like pagination)
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Import here to avoid circular imports
            from .logger import get_logger

            if logger is None:
                log = get_logger()
            else:
                log = logger

            start_time = time.time()
            function_name = func.__qualname__

            # Check for pagination requests (simplified detection)
            pagination_context = None

            if suppress_repeated_calls and function_name in ["get_data", "looper"]:
                # Extract URL from kwargs for pagination detection
                url = kwargs.get("url", "")
                current_context = log.correlation_manager.get_current_context()
                current_trace_id = current_context.get("trace_id")

                # Check if this is a dataset query pagination request
                is_pagination_request = (
                    "/api/query/v1/execute"
                    in url  # Query execute endpoint (most common)
                    or "/data/v1/query" in url  # Dataset query endpoint
                    or ("offset=" in url)  # Any URL with offset pagination
                    or ("skip=" in url)  # Any URL with skip pagination
                )

                if is_pagination_request:
                    # Track pagination requests by trace_id and base URL
                    url_base = url.split("?")[0] if "?" in url else url

                    # Initialize or update pagination tracking
                    if not hasattr(log, "_pagination_requests"):
                        log._pagination_requests = {}

                    pagination_key = f"{current_trace_id}_{url_base}"
                    if pagination_key in log._pagination_requests:
                        # This is a continued pagination request
                        log._pagination_requests[pagination_key]["count"] += 1
                        pagination_context = {
                            "is_pagination": True,
                            "request_count": log._pagination_requests[pagination_key][
                                "count"
                            ],
                            "url_base": url_base,
                        }
                    else:
                        # First request in this pagination sequence
                        log._pagination_requests[pagination_key] = {
                            "count": 1,
                            "start_time": time.time(),
                            "url_base": url_base,
                        }
                        pagination_context = {
                            "is_pagination": False,
                            "request_count": 1,
                            "url_base": url_base,
                        }

            # Get caller context
            caller_frame = inspect.currentframe().f_back
            caller_info = {
                "file": caller_frame.f_code.co_filename,
                "line": caller_frame.f_lineno,
                "function": caller_frame.f_code.co_name,
            }

            # Extract auth and entity info from kwargs
            auth = kwargs.get("auth")
            url = kwargs.get("url", "")
            method = kwargs.get("method", "GET")
            headers = kwargs.get("headers", {})
            body = kwargs.get("body")

            # Extract entity information and calling context
            calling_context = _find_calling_context()
            entity = calling_context.get("entity") or extract_entity_from_args(
                args, kwargs
            )

            # Start request context (inherit trace_id from parent if available)
            request_id = log.start_request(auth=auth)

            # Create HTTP details object with all request information
            params = kwargs.get("params")
            http_details = HTTPDetails(
                method=method,
                url=url,
                headers=headers,
                params=params,
                request_body=body,
            )

            # Get current correlation context
            correlation_context = log.correlation_manager.get_current_context()
            correlation = correlation_context.get("correlation")
            if correlation:
                correlation_obj = Correlation(**correlation)
            else:
                correlation_obj = None

            # Create multi-tenant context - prioritize auth object's context
            multi_tenant = None
            if auth:
                # Extract user information from auth object
                user_id = getattr(auth, "user_id", None)
                user_name = (
                    getattr(auth, "user_name", None)
                    or getattr(auth, "username", None)
                    or getattr(auth, "domo_username", None)
                )

                # Extract tenant/organization information - always use domo_instance if available
                domo_instance = getattr(auth, "domo_instance", None)
                tenant_id = domo_instance
                organization_id = domo_instance

                # Extract session information - prioritize generating from auth
                if user_id and domo_instance:
                    session_id = f"{domo_instance}_{user_id}"
                elif user_name and domo_instance:
                    # Use username/email for session ID if user_id not available
                    session_id = f"{domo_instance}_{user_name}"
                else:
                    session_id = (
                        getattr(auth, "session_id", None)
                        or log.correlation_manager.session_id_var.get()
                    )

                # Always create multi-tenant object if we have auth (at minimum we have domo_instance)
                # Ensure consistent tenant/organization info across all logs
                if hasattr(auth, "domo_instance") or user_id or user_name or session_id:
                    multi_tenant = MultiTenant(
                        user_id=user_id,
                        session_id=session_id,
                        tenant_id=tenant_id,
                        organization_id=organization_id,
                    )
            else:
                # Even without auth, try to get session_id from context
                session_id = log.correlation_manager.session_id_var.get()
                if session_id:
                    multi_tenant = MultiTenant(
                        user_id=None,
                        session_id=session_id,
                        tenant_id=None,
                        organization_id=None,
                    )

            # Prepare function context
            func_context = {
                "action": create_dynamic_action_name(
                    action_name or function_name, calling_context
                ),
                "entity": entity,
                "correlation": correlation_obj,
                "multi_tenant": multi_tenant,
                "http_details": http_details,
            }

            # Add function and caller info to extra for debugging
            extra_func_info = {
                "function": function_name,
                "module": func.__module__,
                "caller": caller_info,
            }

            # Add pagination context if available
            if pagination_context:
                extra_func_info["pagination"] = pagination_context

            # Include sanitized parameters if requested
            if include_params:
                # Sanitize sensitive parameters
                safe_kwargs = {}
                for k, v in kwargs.items():
                    if k in ["password", "token", "auth_token", "access_token"]:
                        safe_kwargs[k] = "***"
                    elif k == "auth":
                        safe_kwargs[k] = str(type(v).__name__)
                    elif isinstance(v, (str, int, float, bool, type(None))):
                        safe_kwargs[k] = v
                    else:
                        safe_kwargs[k] = f"<{type(v).__name__}>"

                func_context["parameters"] = safe_kwargs

            try:
                if not kwargs.get("logger"):
                    kwargs.update({"logger": logger})

                # Call the function
                result = await func(*args, **kwargs)

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Update HTTP details with response information if result is ResponseGetData
                is_http_error = False
                if (
                    hasattr(result, "status")
                    and hasattr(result, "response")
                    and http_details
                ):
                    status_code = getattr(result, "status", None)
                    http_details.status_code = status_code

                    # Check if this is an HTTP error status
                    if status_code and status_code >= 400:
                        is_http_error = True

                    response_data = getattr(result, "response", None)
                    if response_data is not None:
                        if isinstance(response_data, (str, bytes)):
                            http_details.response_size = len(response_data)
                            # Truncate large responses for logging
                            if len(str(response_data)) > 500:
                                http_details.response_body = (
                                    str(response_data)[:500] + "..."
                                )
                            else:
                                http_details.response_body = str(response_data)
                        elif hasattr(response_data, "__len__"):
                            try:
                                response_length = len(response_data)
                                http_details.response_size = response_length
                                if response_length > 100:
                                    http_details.response_body = f"<{type(response_data).__name__} with {response_length} items>"
                                else:
                                    http_details.response_body = (
                                        f"<{type(response_data).__name__}>"
                                    )
                            except:
                                http_details.response_body = (
                                    f"<{type(response_data).__name__}>"
                                )
                        else:
                            http_details.response_body = (
                                f"<{type(response_data).__name__}>"
                            )

                # Prepare result context - check for HTTP errors
                result_context = {
                    "duration_ms": duration_ms,
                    "status": "error" if is_http_error else "success",
                }

                if include_result and result is not None:
                    if hasattr(result, "__len__") and len(result) > 100:
                        result_context["result"] = (
                            f"<{type(result).__name__} with {len(result)} items>"
                        )
                    elif isinstance(result, (str, int, float, bool, type(None))):
                        result_context["result"] = result
                    else:
                        result_context["result"] = f"<{type(result).__name__}>"

                # Update func_context with potentially updated http_details
                func_context["http_details"] = http_details

                # Log based on whether this is an HTTP error or success
                if is_http_error:
                    await log.error(
                        f"Function {create_dynamic_action_name(action_name or function_name, calling_context)} completed with HTTP error {status_code}",
                        logger=f"domolibrary.{func.__module__}",
                        **func_context,
                        **result_context,
                        extra=extra_func_info,
                    )
                else:
                    await log.info(
                        f"Function {create_dynamic_action_name(action_name or function_name, calling_context)} completed successfully",
                        logger=f"domolibrary.{func.__module__}",
                        **func_context,
                        **result_context,
                        extra=extra_func_info,
                    )

                return result

            except Exception as e:
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # If we have an exception that contains response info (like DomoError), capture it
                if hasattr(e, "status") and http_details:
                    http_details.status_code = getattr(e, "status", None)
                elif hasattr(e, "response") and http_details:
                    response_data = getattr(e, "response", None)
                    if hasattr(response_data, "status_code"):
                        http_details.status_code = response_data.status_code

                # Update func_context with potentially updated http_details
                func_context["http_details"] = http_details

                # Log failed function call
                error_extra = {
                    **extra_func_info,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "async_call": True,
                }
                await log.error(
                    f"Function {create_dynamic_action_name(action_name or function_name, calling_context)} failed: {str(e)}",
                    logger=f"domolibrary.{func.__module__}",
                    **func_context,
                    duration_ms=duration_ms,
                    status="error",
                    extra=error_extra,
                )
                raise
            finally:
                log.end_request()

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Import here to avoid circular imports
            from .logger import get_logger

            if logger is None:
                log = get_logger()
            else:
                log = logger

            start_time = time.time()
            function_name = func.__qualname__

            # Get caller context
            caller_frame = inspect.currentframe().f_back
            caller_info = {
                "file": caller_frame.f_code.co_filename,
                "line": caller_frame.f_lineno,
                "function": caller_frame.f_code.co_name,
            }

            # Extract auth and entity info from kwargs
            auth = kwargs.get("auth")
            url = kwargs.get("url", "")
            method = kwargs.get("method", "GET")
            headers = kwargs.get("headers", {})
            body = kwargs.get("body")

            # Extract entity information and calling context
            calling_context = _find_calling_context()
            entity = calling_context.get("entity") or extract_entity_from_args(
                args, kwargs
            )

            # Start request context (inherit trace_id from parent if available)
            request_id = log.start_request(auth=auth)

            # Create HTTP details object with all request information
            params = kwargs.get("params")
            http_details = HTTPDetails(
                method=method,
                url=url,
                headers=headers,
                params=params,
                request_body=body,
            )

            # Get current correlation context
            correlation_context = log.correlation_manager.get_current_context()
            correlation = correlation_context.get("correlation")
            if correlation:
                correlation_obj = Correlation(**correlation)
            else:
                correlation_obj = None

            # Create multi-tenant context
            multi_tenant = None
            if auth:
                # Extract user information from auth object
                user_id = getattr(auth, "user_id", None)
                user_name = (
                    getattr(auth, "user_name", None)
                    or getattr(auth, "username", None)
                    or getattr(auth, "domo_username", None)
                )

                # Extract tenant/organization information - always use domo_instance if available
                domo_instance = getattr(auth, "domo_instance", None)
                tenant_id = domo_instance
                organization_id = domo_instance

                # Extract session information - prioritize generating from auth
                if user_id and domo_instance:
                    session_id = f"{domo_instance}_{user_id}"
                elif user_name and domo_instance:
                    # Use username/email for session ID if user_id not available
                    session_id = f"{domo_instance}_{user_name}"
                else:
                    session_id = (
                        getattr(auth, "session_id", None)
                        or log.correlation_manager.session_id_var.get()
                    )

                # Always create multi-tenant object if we have auth (at minimum we have domo_instance)
                # Ensure consistent tenant/organization info across all logs
                if hasattr(auth, "domo_instance") or user_id or user_name or session_id:
                    multi_tenant = MultiTenant(
                        user_id=user_id,
                        session_id=session_id,
                        tenant_id=tenant_id,
                        organization_id=organization_id,
                    )
            else:
                # Even without auth, try to get session_id from context
                session_id = log.correlation_manager.session_id_var.get()
                if session_id:
                    multi_tenant = MultiTenant(
                        user_id=None,
                        session_id=session_id,
                        tenant_id=None,
                        organization_id=None,
                    )

            # Prepare function context
            func_context = {
                "action": create_dynamic_action_name(
                    action_name or function_name, calling_context
                ),
                "entity": entity,
                "correlation": correlation_obj,
                "multi_tenant": multi_tenant,
                "http_details": http_details,
            }

            # Add function and caller info to extra for debugging
            extra_func_info = {
                "function": function_name,
                "module": func.__module__,
                "caller": caller_info,
            }

            try:
                # Call the function
                result = func(*args, **kwargs)

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Update HTTP details with response information if result is ResponseGetData
                is_http_error = False
                if (
                    hasattr(result, "status")
                    and hasattr(result, "response")
                    and http_details
                ):
                    status_code = getattr(result, "status", None)
                    http_details.status_code = status_code

                    # Check if this is an HTTP error status
                    if status_code and status_code >= 400:
                        is_http_error = True

                    response_data = getattr(result, "response", None)
                    if response_data is not None:
                        if isinstance(response_data, (str, bytes)):
                            http_details.response_size = len(response_data)
                            # Truncate large responses for logging
                            if len(str(response_data)) > 500:
                                http_details.response_body = (
                                    str(response_data)[:500] + "..."
                                )
                            else:
                                http_details.response_body = str(response_data)
                        elif hasattr(response_data, "__len__"):
                            try:
                                response_length = len(response_data)
                                http_details.response_size = response_length
                                if response_length > 100:
                                    http_details.response_body = f"<{type(response_data).__name__} with {response_length} items>"
                                else:
                                    http_details.response_body = (
                                        f"<{type(response_data).__name__}>"
                                    )
                            except:
                                http_details.response_body = (
                                    f"<{type(response_data).__name__}>"
                                )
                        else:
                            http_details.response_body = (
                                f"<{type(response_data).__name__}>"
                            )

                # Prepare result context - check for HTTP errors
                result_context = {
                    "duration_ms": duration_ms,
                    "status": "error" if is_http_error else "success",
                }

                # Update func_context with potentially updated http_details
                func_context["http_details"] = http_details

                # Log based on whether this is an HTTP error or success
                sync_extra = {**extra_func_info, "async_call": False}

                if is_http_error:
                    entry = LogEntry.create(
                        level=LogLevel.ERROR,
                        message=f"Function {function_name} completed with HTTP error {status_code}",
                        logger=f"domolibrary.{func.__module__}",
                        **func_context,
                        **result_context,
                        extra=sync_extra,
                    )
                else:
                    entry = LogEntry.create(
                        level=LogLevel.INFO,
                        message=f"Function {function_name} completed successfully",
                        logger=f"domolibrary.{func.__module__}",
                        **func_context,
                        **result_context,
                        extra=sync_extra,
                    )

                # Add to buffer and flush synchronously
                log.buffer.append(entry)

                # Always try to print immediately in sync context if no event loop
                try:
                    asyncio.get_running_loop()
                    # Event loop exists, flush will happen on next async call
                    if len(log.buffer) >= log.config.batch_size:
                        pass  # Will be flushed by background task
                except RuntimeError:
                    # No event loop, print directly
                    if log.config.pretty_print:
                        print(json.dumps(entry.to_dict(), indent=2, default=str))
                        print("-" * 80)
                    else:
                        print(entry.to_json())
                    log.buffer.clear()  # Clear buffer after printing

                return result

            except Exception as e:
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # If we have an exception that contains response info (like DomoError), capture it
                if hasattr(e, "status") and http_details:
                    http_details.status_code = getattr(e, "status", None)
                elif hasattr(e, "response") and http_details:
                    response_data = getattr(e, "response", None)
                    if hasattr(response_data, "status_code"):
                        http_details.status_code = response_data.status_code

                # Update func_context with potentially updated http_details
                func_context["http_details"] = http_details

                # Log failed function call
                # For sync functions, we need to create the log entry manually since we can't await
                sync_error_extra = {
                    **extra_func_info,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "async_call": False,
                }
                error_entry = LogEntry.create(
                    level=LogLevel.ERROR,
                    message=f"Function {function_name} failed: {str(e)}",
                    logger=f"domolibrary.{func.__module__}",
                    **func_context,
                    duration_ms=duration_ms,
                    status="error",
                    extra=sync_error_extra,
                )

                # Add to buffer and flush synchronously
                log.buffer.append(error_entry)
                try:
                    asyncio.get_running_loop()
                    # Event loop exists, flush will happen on next async call
                    pass
                except RuntimeError:
                    # No event loop, print directly
                    if log.config.pretty_print:
                        print(json.dumps(error_entry.to_dict(), indent=2, default=str))
                        print("-" * 80)
                    else:
                        print(error_entry.to_json())
                    log.buffer.clear()  # Clear buffer after printing
                raise
            finally:
                log.end_request()

        # Return appropriate wrapper based on whether function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
