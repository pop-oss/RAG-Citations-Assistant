"""Document schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentResponse(BaseModel):
    """Document response."""
    id: UUID
    kb_id: UUID
    filename: str
    path: Optional[str] = None
    file_type: Optional[str] = None
    size: Optional[int] = None
    status: DocumentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True
