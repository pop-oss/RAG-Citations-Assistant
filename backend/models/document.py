"""Document and Chunk models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import enum

from database import Base
from config import settings


class DocumentStatus(str, enum.Enum):
    """Document processing status."""
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(Base):
    """Document table for uploaded files."""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    path = Column(String(512), nullable=False)  # Local storage path
    file_type = Column(String(10), nullable=False)  # pdf, md, txt
    size = Column(Integer, nullable=True)  # File size in bytes
    status = Column(
        Enum(DocumentStatus),
        default=DocumentStatus.PROCESSING,
        nullable=False
    )
    error_message = Column(Text, nullable=True)  # Error message if failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"


class Chunk(Base):
    """Document chunk with embedding vector."""
    
    __tablename__ = "chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.embedding_dimension), nullable=True)  # pgvector
    
    # Metadata for citation tracing
    page_number = Column(Integer, nullable=True)  # For PDF
    line_start = Column(Integer, nullable=True)   # For MD/TXT
    line_end = Column(Integer, nullable=True)     # For MD/TXT
    chunk_index = Column(Integer, nullable=False, default=0)  # Order within document
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, doc_id={self.doc_id}, index={self.chunk_index})>"
