"""Document processing service."""
import os
import asyncio
from typing import List, Tuple, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.document import Document, Chunk, DocumentStatus
from utils.pdf_parser import PDFParser
from utils.text_parser import TextParser
from utils.chunker import TextChunker
from providers.factory import get_embedding_provider


class DocumentService:
    """Service for document processing and chunking."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chunker = TextChunker()
    
    async def process_document(self, document_id: UUID) -> None:
        """
        Process a document: parse, chunk, and generate embeddings.
        This is meant to be called as a background task.
        """
        # Get document
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return
        
        try:
            # Parse document based on type
            if document.file_type == "pdf":
                parsed_content = await self._parse_pdf(document.path)
            else:  # md or txt
                parsed_content = await self._parse_text(document.path)
            
            # Chunk the content
            chunks_data = self.chunker.chunk_content(
                parsed_content,
                document.file_type
            )
            
            # Generate embeddings
            embedding_provider = get_embedding_provider()
            texts = [chunk["content"] for chunk in chunks_data]
            embeddings = await embedding_provider.embed(texts)
            
            # Create chunk records
            for i, (chunk_data, embedding) in enumerate(zip(chunks_data, embeddings)):
                chunk = Chunk(
                    doc_id=document.id,
                    content=chunk_data["content"],
                    embedding=embedding,
                    page_number=chunk_data.get("page_number"),
                    line_start=chunk_data.get("line_start"),
                    line_end=chunk_data.get("line_end"),
                    chunk_index=i,
                )
                self.db.add(chunk)
            
            # Update document status to ready
            await self.db.execute(
                update(Document)
                .where(Document.id == document_id)
                .values(status=DocumentStatus.READY)
            )
            await self.db.commit()
            
        except Exception as e:
            # Update document status to failed
            await self.db.execute(
                update(Document)
                .where(Document.id == document_id)
                .values(
                    status=DocumentStatus.FAILED,
                    error_message=str(e)
                )
            )
            await self.db.commit()
            raise
    
    async def _parse_pdf(self, path: str) -> List[dict]:
        """Parse PDF and return list of {page_number, content}."""
        parser = PDFParser()
        return await asyncio.to_thread(parser.parse, path)
    
    async def _parse_text(self, path: str) -> List[dict]:
        """Parse text file and return list of {line_start, line_end, content}."""
        parser = TextParser()
        return await asyncio.to_thread(parser.parse, path)
    
    async def get_documents_by_kb(self, kb_id: UUID) -> List[Document]:
        """Get all documents for a knowledge base."""
        result = await self.db.execute(
            select(Document)
            .where(Document.kb_id == kb_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())
