"""Knowledge Base router."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.kb import KnowledgeBase
from models.user import User
from schemas.kb import KBCreate, KBResponse
from services.auth_service import get_current_user

router = APIRouter()


@router.get("", response_model=List[KBResponse])
async def list_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all knowledge bases owned by the current user.
    """
    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.owner_id == current_user.id)
        .order_by(KnowledgeBase.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=KBResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    request: KBCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new knowledge base.
    
    - **name**: Knowledge base name
    - **description**: Optional description
    """
    kb = KnowledgeBase(
        name=request.name,
        description=request.description,
        owner_id=current_user.id,
    )
    db.add(kb)
    await db.flush()
    await db.refresh(kb)
    
    return kb


@router.get("/{kb_id}", response_model=KBResponse)
async def get_knowledge_base(
    kb_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific knowledge base by ID.
    """
    result = await db.execute(
        select(KnowledgeBase)
        .where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.owner_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "KB_NOT_FOUND",
                "message": "Knowledge base not found",
            }
        )
    
    return kb


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a knowledge base and all its documents.
    """
    # Check ownership
    result = await db.execute(
        select(KnowledgeBase)
        .where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.owner_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "KB_NOT_FOUND",
                "message": "Knowledge base not found",
            }
        )
    
    # Delete (cascade will handle documents, chunks, conversations)
    await db.delete(kb)
    await db.commit()
    
    return None
