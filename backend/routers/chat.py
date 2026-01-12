"""Chat router with SSE streaming."""
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.kb import KnowledgeBase
from models.user import User
from schemas.chat import ChatRequest
from services.auth_service import get_current_user
from services.rag_service import RAGService

router = APIRouter()


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as SSE event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@router.post("/{kb_id}/chat/stream")
async def chat_stream(
    kb_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream chat response with SSE.
    
    SSE Events:
    - **token**: `{"token": "xxx"}` - Individual token from LLM
    - **citations**: `{"citations": [...]}` - Retrieved source citations
    - **done**: `{}` - Stream completed
    - **error**: `{"message": "xxx", "code": "xxx"}` - Error occurred
    """
    # Verify KB ownership
    kb_result = await db.execute(
        select(KnowledgeBase)
        .where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.owner_id == current_user.id
        )
    )
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "KB_NOT_FOUND", "message": "Knowledge base not found"}
        )
    
    async def generate_response():
        """Generate SSE stream."""
        try:
            rag_service = RAGService(db)
            
            # Retrieve relevant chunks
            chunks_with_scores = await rag_service.retrieve_relevant_chunks(
                kb_id=kb_id,
                query=request.message,
                top_k=5
            )
            
            if not chunks_with_scores:
                # No relevant content found
                yield format_sse_event("token", {"token": "I couldn't find any relevant information in the knowledge base to answer your question."})
                yield format_sse_event("citations", {"citations": []})
                yield format_sse_event("done", {})
                return
            
            # Build context and citations
            context = rag_service.build_context(chunks_with_scores)
            citations = rag_service.create_citations(chunks_with_scores)
            
            # Send citations early so frontend can display them
            citations_data = [c.model_dump(mode="json") for c in citations]
            yield format_sse_event("citations", {"citations": citations_data})
            
            # Stream LLM response
            async for token in rag_service.generate_answer_stream(
                query=request.message,
                context=context,
                chat_provider=request.chat_provider,
            ):
                yield format_sse_event("token", {"token": token})
            
            # Done
            yield format_sse_event("done", {})
            
        except Exception as e:
            # Send error event
            yield format_sse_event("error", {
                "message": str(e),
                "code": "GENERATION_ERROR"
            })
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
