"""Documents router."""
import os
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db, async_session_maker
from models.kb import KnowledgeBase
from models.document import Document, DocumentStatus
from models.user import User
from schemas.document import DocumentResponse
from services.auth_service import get_current_user
from services.document_service import DocumentService

router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def process_document_background(document_id: UUID):
    """Background task to process a document."""
    async with async_session_maker() as db:
        service = DocumentService(db)
        try:
            await service.process_document(document_id)
        except Exception as e:
            print(f"Error processing document {document_id}: {e}")


@router.get("/{kb_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    kb_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all documents in a knowledge base.
    """
    # Verify KB ownership
    kb_result = await db.execute(
        select(KnowledgeBase)
        .where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.owner_id == current_user.id
        )
    )
    if not kb_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "KB_NOT_FOUND", "message": "Knowledge base not found"}
        )
    
    # Get documents
    result = await db.execute(
        select(Document)
        .where(Document.kb_id == kb_id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/{kb_id}/documents", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    kb_id: UUID,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload documents to a knowledge base.
    
    Accepts multiple files: PDF, Markdown (.md), or Text (.txt).
    Documents will be processed asynchronously.
    """
    # Verify KB ownership
    kb_result = await db.execute(
        select(KnowledgeBase)
        .where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.owner_id == current_user.id
        )
    )
    if not kb_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "KB_NOT_FOUND", "message": "Knowledge base not found"}
        )
    
    # Create upload directory for this KB
    kb_upload_dir = os.path.join(settings.upload_dir, str(kb_id))
    os.makedirs(kb_upload_dir, exist_ok=True)
    
    uploaded_documents = []
    
    for file in files:
        # Validate file extension
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_FILE_TYPE",
                    "message": f"File type {ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
                }
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "FILE_TOO_LARGE",
                    "message": f"File {file.filename} exceeds maximum size of 10MB",
                }
            )
        
        # Generate unique filename and save
        import uuid
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(kb_upload_dir, unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create document record
        document = Document(
            kb_id=kb_id,
            filename=file.filename,
            path=file_path,
            file_type=ext[1:],  # Remove the dot
            size=file_size,
            status=DocumentStatus.PROCESSING,
        )
        db.add(document)
        await db.flush()
        await db.refresh(document)
        
        uploaded_documents.append(document)
        
        # Schedule background processing
        background_tasks.add_task(process_document_background, document.id)
    
    await db.commit()
    
    return uploaded_documents
