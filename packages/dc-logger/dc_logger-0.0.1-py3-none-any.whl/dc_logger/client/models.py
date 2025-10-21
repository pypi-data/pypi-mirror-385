import datetime as dt
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
import json

from .enums import LogLevel


@dataclass
class Entity:
    """Entity information for logging"""

    type: str  # dataset, card, user, dataflow, page, etc.
    id: Optional[str] = None
    name: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
    parent: Any = None  # instance of a class

    def get_additional_info(self, info_fn: Callable = None):
        """Populate additional_info when we don't have a full parent object"""
        if info_fn:
            self.additional_info = info_fn(self)
            return self.additional_info

        # Only populate additional_info if we don't have a parent object
        # This avoids duplication - use parent for full objects, additional_info for context
        if self.parent:
            return self.additional_info
            
        additional_info = {}
        if hasattr(self.parent, "description"):
            additional_info["description"] = getattr(self.parent, "description", "")
        if hasattr(self.parent, "owner"):
            additional_info["owner"] = getattr(self.parent, "owner", {})
        if hasattr(self.parent, "display_type"):
            additional_info["display_type"] = getattr(self.parent, "display_type", "")
        if hasattr(self.parent, "data_provider_type"):
            additional_info["data_provider_type"] = getattr(
                self.parent, "data_provider_type", ""
            )

        # Get auth instance info
        if hasattr(self.parent, "auth") and self.parent.auth:
            additional_info["domo_instance"] = getattr(
                self.parent.auth, "domo_instance", None
            )

        self.additional_info = additional_info
        return self.additional_info

    def to_dict(self) -> Dict[str, Any]:
        """Convert Entity to dictionary for JSON serialization"""
        parent_dict = None
        if self.parent:
            parent_dict = self._serialize_parent(self.parent)
        
        result = {
            "type": self.type,
            "id": self.id,
            "name": self.name,
        }
        
        # Include parent if we have a full object, otherwise include additional_info for context
        if parent_dict:
            result["parent"] = parent_dict
        elif self.additional_info:
            result["additional_info"] = self.additional_info
            
        return result

    def _serialize_parent(self, parent) -> Dict[str, Any]:
        """Safely serialize parent object to dictionary"""
        if parent is None:
            return None
        
        # If parent has a to_dict method, use it
        if hasattr(parent, 'to_dict') and callable(getattr(parent, 'to_dict')):
            try:
                parent_dict = parent.to_dict()
                # Add metadata about the parent object
                parent_dict['_metadata'] = {
                    "class_name": type(parent).__name__,
                    "module": getattr(type(parent), '__module__', 'unknown')
                }
                return parent_dict
            except Exception as e:
                # If to_dict fails, fall back to manual extraction
                pass
        
        # Extract key attributes from parent object
        parent_info = {
            "_metadata": {
                "class_name": type(parent).__name__,
                "module": getattr(type(parent), '__module__', 'unknown')
            }
        }
        
        # Common attributes to extract from Domo entities
        common_attrs = [
            'id', 'name', 'display_name', 'description', 'owner', 
            'display_type', 'data_provider_type', 'row_count', 'column_count',
            'created_dt', 'last_updated_dt', 'last_touched_dt',
            'stream_id', 'cloud_id', 'formula', 'status'
        ]
        
        for attr in common_attrs:
            if hasattr(parent, attr):
                value = getattr(parent, attr, None)
                if value is not None:
                    # Handle datetime objects
                    if hasattr(value, 'isoformat'):
                        parent_info[attr] = value.isoformat()
                    # Handle simple types
                    elif isinstance(value, (str, int, float, bool)):
                        parent_info[attr] = value
                    # Handle dictionaries
                    elif isinstance(value, dict):
                        parent_info[attr] = value
                    # Handle lists (but limit size)
                    elif isinstance(value, list) and len(value) < 10:
                        parent_info[attr] = value
                    # Convert complex objects to string representation (truncated)
                    else:
                        str_value = str(value)
                        if len(str_value) > 200:
                            parent_info[attr] = str_value[:200] + "... (truncated)"
                        else:
                            parent_info[attr] = str_value
        
        # Extract auth information if available
        if hasattr(parent, 'auth') and parent.auth:
            auth_info = {}
            if hasattr(parent.auth, 'domo_instance'):
                auth_info['domo_instance'] = parent.auth.domo_instance
            if hasattr(parent.auth, 'user_id'):
                auth_info['user_id'] = parent.auth.user_id
            if auth_info:
                parent_info['auth'] = auth_info
        
        # If we didn't extract much useful info, include a summary
        if len(parent_info) <= 1:  # Only metadata
            parent_info['summary'] = str(parent)[:500] + ("..." if len(str(parent)) > 500 else "")
        
        # Special handling for common Domo classes that might not have to_dict
        if hasattr(parent, '__class__'):
            class_name = type(parent).__name__
            if 'DomoDataset' in class_name:
                # Extract specific DomoDataset attributes
                dataset_attrs = [
                    'id', 'name', 'description', 'owner', 'display_type', 'data_provider_type',
                    'row_count', 'column_count', 'stream_id', 'cloud_id', 'created_dt', 
                    'last_updated_dt', 'last_touched_dt'
                ]
                for attr in dataset_attrs:
                    if hasattr(parent, attr) and attr not in parent_info:
                        value = getattr(parent, attr, None)
                        if value is not None:
                            if hasattr(value, 'isoformat'):
                                parent_info[attr] = value.isoformat()
                            elif isinstance(value, (str, int, float, bool, dict)):
                                parent_info[attr] = value
                            else:
                                str_value = str(value)
                                if len(str_value) > 200:
                                    parent_info[attr] = str_value[:200] + "... (truncated)"
                                else:
                                    parent_info[attr] = str_value
        
        return parent_info

    @classmethod
    def from_domo_entity(cls, domo_entity, info_fn: Callable = None) -> "Entity":
        """Create Entity from a DomoEntity object"""

        if not domo_entity:
            return None

        # Extract entity type from class name (e.g., DomoDataset -> dataset)
        entity_type = cls._extract_entity_type(type(domo_entity).__name__)

        entity = cls(
            type=entity_type,
            parent=domo_entity,
            id=getattr(domo_entity, "id", None),
            name=getattr(domo_entity, "name", None),
        )
        entity.get_additional_info(info_fn=info_fn)

        return entity

    @staticmethod
    def _extract_entity_type(class_name: str) -> str:
        """Extract entity type from DomoEntity class name"""
        # Remove 'Domo' prefix and convert to lowercase
        if class_name.startswith("Domo"):
            return class_name[4:].lower()
        return class_name.lower()


@dataclass
class HTTPDetails:
    """HTTP request/response details"""

    method: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    response_size: Optional[int] = None
    request_body: Optional[Any] = None
    response_body: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert HTTPDetails to dictionary for JSON serialization"""
        return {
            "method": self.method,
            "url": self.url,
            "status_code": self.status_code,
            "headers": self.headers,
            "params": self.params,
            "response_size": self.response_size,
            "request_body": self.request_body,
            "response_body": self.response_body
        }


@dataclass
class Correlation:
    """Correlation information for distributed tracing"""

    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Correlation to dictionary for JSON serialization"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id
        }


@dataclass
class MultiTenant:
    """Multi-tenant information"""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert MultiTenant to dictionary for JSON serialization"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "organization_id": self.organization_id
        }


@dataclass
class LogEntry:
    """Enhanced log entry with structured JSON format"""

    # Core log fields
    timestamp: str
    level: LogLevel
    logger: str
    message: str

    # Business context
    user: Optional[str] = None
    action: Optional[str] = None
    entity: Optional[Entity] = None
    status: str = "info"
    duration_ms: Optional[int] = None

    # Distributed tracing
    correlation: Optional[Correlation] = None

    # Multi-tenant context
    multi_tenant: Optional[MultiTenant] = None

    # HTTP details (for API calls)
    http_details: Optional[HTTPDetails] = None

    # Flexible metadata
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            # Core log fields
            "timestamp": self.timestamp,
            "level": self.level.value,
            "logger": self.logger,
            "message": self.message,
            # Business context
            "user": self.user
            or (
                self.multi_tenant.user_id
                if self.multi_tenant and self.multi_tenant.user_id
                else None
            ),
            "action": self.action,
            "status": self.status,
            "duration_ms": self.duration_ms,
            # Entity (serialize if present)
            "entity": self.entity.to_dict() if self.entity else None,
            # Correlation (serialize if present)
            "correlation": self.correlation.__dict__ if self.correlation else None,
            # Multi-tenant (serialize if present)
            "multi_tenant": self.multi_tenant.__dict__ if self.multi_tenant else None,
            # HTTP details (serialize if present and has data)
            "http_details": self._serialize_http_details(),
            # Flexible metadata
            "extra": self.extra,
        }

        # Remove None values for cleaner output
        return {k: v for k, v in result.items() if v is not None}

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def create(cls, level: LogLevel, message: str, logger: str, **kwargs) -> "LogEntry":
        """Factory method to create a LogEntry with current timestamp"""
        timestamp = dt.datetime.utcnow().isoformat() + "Z"

        # Extract known fields
        user = kwargs.get("user")
        action = kwargs.get("action")
        status = kwargs.get("status", "info")
        duration_ms = kwargs.get("duration_ms")
        extra = kwargs.get("extra", {})

        # Handle entity - could be dict, Entity object, or DomoEntity object
        entity = kwargs.get("entity")
        if isinstance(entity, dict) and entity:
            entity_obj = Entity(**entity)
        elif isinstance(entity, Entity):
            entity_obj = entity
        elif entity and hasattr(entity, "id"):  # DomoEntity object
            entity_obj = Entity.from_domo_entity(entity)
        else:
            entity_obj = None

        # Handle correlation - could be dict, Correlation object, or individual fields
        correlation_obj = None
        correlation = kwargs.get("correlation")
        if isinstance(correlation, dict) and correlation:
            correlation_obj = Correlation(**correlation)
        elif isinstance(correlation, Correlation):
            correlation_obj = correlation
        elif any(k in kwargs for k in ["trace_id", "span_id", "parent_span_id"]):
            # Create correlation from individual fields
            correlation_obj = Correlation(
                trace_id=kwargs.get("trace_id"),
                span_id=kwargs.get("span_id"),
                parent_span_id=kwargs.get("parent_span_id"),
            )

        # Handle multi-tenant - could be dict, MultiTenant object, or individual fields
        multi_tenant_obj = None
        multi_tenant = kwargs.get("multi_tenant")
        if isinstance(multi_tenant, dict) and multi_tenant:
            multi_tenant_obj = MultiTenant(**multi_tenant)
        elif isinstance(multi_tenant, MultiTenant):
            multi_tenant_obj = multi_tenant
        elif any(
            k in kwargs
            for k in ["user_id", "session_id", "tenant_id", "organization_id"]
        ):
            # Create multi-tenant from individual fields
            multi_tenant_obj = MultiTenant(
                user_id=kwargs.get("user_id") or kwargs.get("user"),
                session_id=kwargs.get("session_id"),
                tenant_id=kwargs.get("tenant_id"),
                organization_id=kwargs.get("organization_id"),
            )

        # Handle HTTP details - could be dict, HTTPDetails object, or individual fields
        http_details_obj = None
        http_details = kwargs.get("http_details")
        if isinstance(http_details, dict) and http_details:
            http_details_obj = HTTPDetails(**http_details)
        elif isinstance(http_details, HTTPDetails):
            http_details_obj = http_details
        elif any(
            k in kwargs
            for k in ["method", "url", "status_code", "headers", "response_size"]
        ):
            # Create HTTP details from individual fields
            http_details_obj = HTTPDetails(
                method=kwargs.get("method"),
                url=kwargs.get("url"),
                status_code=kwargs.get("status_code"),
                headers=kwargs.get("headers"),
                response_size=kwargs.get("response_size"),
                request_body=kwargs.get("request_body"),
                response_body=kwargs.get("response_body"),
            )

        # If user is not set but multi_tenant has user_id, use that
        if not user and multi_tenant_obj and multi_tenant_obj.user_id:
            user = multi_tenant_obj.user_id

        return cls(
            timestamp=timestamp,
            level=level,
            logger=logger,
            message=message,
            user=user,
            action=action,
            entity=entity_obj,
            status=status,
            duration_ms=duration_ms,
            correlation=correlation_obj,
            multi_tenant=multi_tenant_obj,
            http_details=http_details_obj,
            extra=extra,
        )

    def _serialize_http_details(self) -> Optional[Dict[str, Any]]:
        """Serialize HTTP details for logging, filtering sensitive data"""
        if not self.http_details:
            return None

        http_details_dict = {}

        if self.http_details.method:
            http_details_dict["method"] = self.http_details.method

        if self.http_details.url:
            http_details_dict["url"] = self.http_details.url

        if self.http_details.headers:
            # Only include important headers, not sensitive ones
            safe_headers = {}
            for k, v in self.http_details.headers.items():
                if k.lower() not in [
                    "authorization",
                    "cookie",
                    "x-domo-authentication",
                ]:
                    safe_headers[k] = v
            if safe_headers:
                http_details_dict["headers"] = safe_headers

        if self.http_details.params:
            http_details_dict["params"] = self.http_details.params

        if self.http_details.request_body:
            # Truncate large request bodies
            if (
                isinstance(self.http_details.request_body, str)
                and len(self.http_details.request_body) > 500
            ):
                http_details_dict["request_body"] = (
                    self.http_details.request_body[:500] + "..."
                )
            else:
                http_details_dict["request_body"] = self.http_details.request_body

        if self.http_details.response_body:
            # Truncate large response bodies
            if (
                isinstance(self.http_details.response_body, str)
                and len(self.http_details.response_body) > 500
            ):
                http_details_dict["response_body"] = (
                    self.http_details.response_body[:500] + "..."
                )
            else:
                http_details_dict["response_body"] = self.http_details.response_body

        return http_details_dict if http_details_dict else None
