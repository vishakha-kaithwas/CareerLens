from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Standardized top-level API response envelope."""
    success: bool = Field(..., description="Whether the request succeeded")
    message: str = Field(..., description="Human-readable status or summary message")
    data: Optional[DataT] = Field(None, description="Payload data returned by the endpoint")
    errors: Optional[Any] = Field(None, description="Detailed error information if failed")
