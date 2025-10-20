from abc import ABC
from enum import Enum
from typing import Any, List

from pydantic import BaseModel, Field


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    Patch = "PATCH"
    DELETE = "DELETE"


class HeaderConfig(BaseModel):
    """Secure header configuration with environment variables support."""
    name: str
    value: str
    secure: bool = False

    class Config:
        frozen = True


class RequestSchemaConfig(BaseModel):
    """Schema definition for request payload population."""
    field_path: str  # JSON path-like: "data.user.id"
    value: Any
    value_type: str = "static"  # static, env, dynamic
    required: bool = True


class ResponseMappingConfig(BaseModel):
    """Response data extraction mapping."""
    field_path: str  # JSON path-like: "data.results[0].id"
    extract_as: str  # Name to extract as
    default: Any = None


class EndpointConfig(BaseModel):
    """Complete endpoint configuration."""
    name: str
    base_url: str
    path: str
    method: HttpMethod
    headers: List[HeaderConfig] = Field(default_factory=list)
    request_schema: List[RequestSchemaConfig] = Field(default_factory=list)
    response_mapping: List[ResponseMappingConfig] = Field(default_factory=list)
    timeout: int = 30
    retry_count: int = 3
    retry_backoff: float = 1.0

    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v.startswith('/'):
            return f'/{v}'
        return v


class PayloadBuilder(ABC):
    """Abstract base for payload construction strategies."""