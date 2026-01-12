"""Chat and Citation schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class Citation(BaseModel):
    """Citation for RAG answer tracing."""
    doc_id: UUID = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    chunk_id: UUID = Field(..., description="Chunk ID")
    text: str = Field(..., description="Chunk text content")
    score: Optional[float] = Field(None, description="Similarity score")
    page_number: Optional[int] = Field(None, description="Page number (PDF)")
    line_range: Optional[str] = Field(None, description="Line range (MD/TXT)")
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Chat request."""
    message: str = Field(..., min_length=1, description="User message")
    chat_provider: Optional[str] = Field(
        None, 
        description="LLM provider: deepseek, qwen, zhipu"
    )
    conversation_id: Optional[UUID] = Field(
        None, 
        description="Existing conversation ID to continue"
    )


class MessageResponse(BaseModel):
    """Message response."""
    id: UUID
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    created_at: str
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response."""
    id: UUID
    kb_id: UUID
    title: str
    created_at: str
    messages: Optional[List[MessageResponse]] = None
    
    class Config:
        from_attributes = True
