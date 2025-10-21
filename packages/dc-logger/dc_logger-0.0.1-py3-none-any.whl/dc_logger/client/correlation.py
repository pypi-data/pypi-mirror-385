import uuid
from typing import Optional, Dict, Any
from contextvars import ContextVar

from .models import Correlation


class CorrelationManager:
    """Manages correlation IDs and context propagation"""

    def __init__(self):
        self.trace_id_var: ContextVar[Optional[str]] = ContextVar(
            "trace_id", default=None
        )
        self.request_id_var: ContextVar[Optional[str]] = ContextVar(
            "request_id", default=None
        )
        self.session_id_var: ContextVar[Optional[str]] = ContextVar(
            "session_id", default=None
        )
        self.span_id_var: ContextVar[Optional[str]] = ContextVar(
            "span_id", default=None
        )
        self.correlation_var: ContextVar[Optional[Correlation]] = ContextVar(
            "correlation", default=None
        )
        # Track last span_id per trace_id for proper parent span relationships
        self._trace_span_history: Dict[str, str] = {}

    def generate_trace_id(self) -> str:
        """Generate a new trace ID"""
        return str(uuid.uuid4())

    def generate_request_id(self) -> str:
        """Generate a new request ID"""
        return uuid.uuid4().hex[:12]

    def generate_span_id(self) -> str:
        """Generate a new span ID"""
        return uuid.uuid4().hex[:16]

    def generate_session_id(self, auth=None) -> str:
        """Generate a new session ID based on auth or create random"""
        if auth:
            # Use auth instance and user info for session ID
            user_id = (
                getattr(auth, "user_id", None)
                or getattr(auth, "user_name", None)
                or getattr(auth, "username", None)
            )
            domo_instance = getattr(auth, "domo_instance", None)

            if domo_instance and user_id:
                return f"{domo_instance}_{user_id}"
            elif domo_instance:
                return f"{domo_instance}_anonymous"
            elif user_id:
                return f"unknown_{user_id}"
            else:
                return f"auth_{id(auth)}"
        else:
            return uuid.uuid4().hex[:12]

    def start_request(
        self,
        parent_trace_id: Optional[str] = None,
        auth=None,
        is_pagination_request: bool = False,
    ) -> str:
        """Start a new request context"""
        # Use existing trace_id if available, otherwise generate new one
        # Only generate new trace_id if we don't have one in context AND no parent provided
        current_trace_id = self.trace_id_var.get()
        trace_id = parent_trace_id or current_trace_id or self.generate_trace_id()

        request_id = self.generate_request_id()

        # Generate session_id from auth if available, otherwise use existing or generate random
        if auth and (hasattr(auth, "user_id") or hasattr(auth, "domo_instance")):
            session_id = self.generate_session_id(auth)
        else:
            session_id = self.session_id_var.get() or self.generate_session_id(auth)
        span_id = self.generate_span_id()

        # Handle parent span for pagination vs regular requests
        if is_pagination_request:
            # For pagination requests, use the original parent span for this trace
            # This ensures all pagination requests have the same parent
            parent_span_id = self._trace_span_history.get(f"{trace_id}_original_parent")
            if not parent_span_id:
                # If no original parent stored, this is the first pagination request
                # Store current span as original parent for future pagination requests
                parent_span_id = self._trace_span_history.get(trace_id)
                self._trace_span_history[f"{trace_id}_original_parent"] = (
                    parent_span_id or None
                )
        else:
            # For regular requests, use normal span chaining
            parent_span_id = self._trace_span_history.get(trace_id)
            # Store this as the original parent for future pagination requests
            self._trace_span_history[f"{trace_id}_original_parent"] = parent_span_id

        # Update the span history with the current span_id for this trace
        self._trace_span_history[trace_id] = span_id

        # Set context variables
        self.trace_id_var.set(trace_id)
        self.request_id_var.set(request_id)
        self.session_id_var.set(session_id)
        self.span_id_var.set(span_id)

        # Create correlation object
        correlation = Correlation(
            trace_id=trace_id, span_id=span_id, parent_span_id=parent_span_id
        )
        self.correlation_var.set(correlation)

        return request_id

    def get_current_context(self) -> Dict[str, Any]:
        """Get current correlation context"""
        correlation = self.correlation_var.get()
        return {
            "trace_id": self.trace_id_var.get(),
            "request_id": self.request_id_var.get(),
            "session_id": self.session_id_var.get(),
            "span_id": self.span_id_var.get(),
            "correlation": correlation.__dict__ if correlation else None,
        }

    def set_context_value(self, key: str, value: Any):
        """Set a value in the correlation context"""
        correlation = self.correlation_var.get()
        if correlation:
            correlation_dict = correlation.__dict__.copy()
            correlation_dict[key] = value
            self.correlation_var.set(Correlation(**correlation_dict))


# Global correlation manager instance
correlation_manager = CorrelationManager()
