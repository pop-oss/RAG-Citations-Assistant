"""Error response schema."""
from pydantic import BaseModel, Field
from typing import Optional, Any


class ErrorResponse(BaseModel):
    """Unified error response format matching frontend ApiError type."""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Any] = Field(None, description="Additional error details")
