"""RAG service for retrieval and answer generation."""
from typing import List, Optional, AsyncGenerator, Tuple
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.document import Document, Chunk
from models.kb import KnowledgeBase
from schemas.chat import Citation
from providers.factory import get_embedding_provider, get_chat_provider


class RAGService:
    """Service for RAG operations: retrieval and generation."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.top_k = 5  # Number of chunks to retrieve
    
    async def retrieve_relevant_chunks(
        self, 
        kb_id: UUID, 
        query: str,
        top_k: int = 5
    ) -> List[Tuple[Chunk, Document, float]]:
        """
        Retrieve most relevant chunks for a query using vector similarity.
        Returns list of (chunk, document, score) tuples.
        """
        # Get query embedding
        embedding_provider = get_embedding_provider()
        query_embeddings = await embedding_provider.embed([query])
        query_embedding = query_embeddings[0]
        
        # Vector similarity search using pgvector
        # Use cosine distance: 1 - cosine_similarity
        embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"
        
        sql = text("""
            SELECT 
                c.id as chunk_id,
                c.doc_id,
                c.content,
                c.page_number,
                c.line_start,
                c.line_end,
                c.chunk_index,
                d.filename,
                1 - (c.embedding <=> :embedding::vector) as score
            FROM chunks c
            JOIN documents d ON c.doc_id = d.id
            WHERE d.kb_id = :kb_id 
              AND d.status = 'ready'
              AND c.embedding IS NOT NULL
            ORDER BY c.embedding <=> :embedding::vector
            LIMIT :limit
        """)
        
        result = await self.db.execute(
            sql,
            {
                "kb_id": str(kb_id),
                "embedding": embedding_str,
                "limit": top_k
            }
        )
        
        rows = result.fetchall()
        chunks_with_scores = []
        
        for row in rows:
            chunk = Chunk(
                id=row.chunk_id,
                doc_id=row.doc_id,
                content=row.content,
                page_number=row.page_number,
                line_start=row.line_start,
                line_end=row.line_end,
                chunk_index=row.chunk_index,
            )
            # Create a minimal document for citation
            doc = Document(
                id=row.doc_id,
                filename=row.filename,
            )
            chunks_with_scores.append((chunk, doc, row.score))
        
        return chunks_with_scores
    
    def build_context(self, chunks_with_scores: List[Tuple[Chunk, Document, float]]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        for i, (chunk, doc, score) in enumerate(chunks_with_scores):
            source_info = f"[{doc.filename}]"
            if chunk.page_number:
                source_info += f" (Page {chunk.page_number})"
            elif chunk.line_start:
                source_info += f" (Lines {chunk.line_start}-{chunk.line_end})"
            
            context_parts.append(f"Source {i+1} {source_info}:\n{chunk.content}")
        
        return "\n\n".join(context_parts)
    
    def create_citations(
        self, 
        chunks_with_scores: List[Tuple[Chunk, Document, float]]
    ) -> List[Citation]:
        """Create citation objects from retrieved chunks."""
        citations = []
        for chunk, doc, score in chunks_with_scores:
            line_range = None
            if chunk.line_start is not None and chunk.line_end is not None:
                line_range = f"{chunk.line_start}-{chunk.line_end}"
            
            citation = Citation(
                doc_id=doc.id,
                filename=doc.filename,
                chunk_id=chunk.id,
                text=chunk.content[:500],  # Truncate for display
                score=round(score, 4) if score else None,
                page_number=chunk.page_number,
                line_range=line_range,
            )
            citations.append(citation)
        
        return citations
    
    async def generate_answer_stream(
        self,
        query: str,
        context: str,
        chat_provider: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate answer using LLM with retrieved context.
        Yields tokens as they are generated.
        """
        # Build prompt
        system_prompt = """You are a helpful assistant that answers questions based on the provided context.
Always cite your sources by referencing the source numbers provided.
If the context doesn't contain enough information to answer the question, say so.
Be concise and accurate in your responses."""
        
        user_prompt = f"""Context:
{context}

Question: {query}

Please answer the question based on the context above. Cite your sources using [Source N] format."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # Get chat provider and stream response
        provider = get_chat_provider(chat_provider)
        
        async for token in provider.stream_chat(messages):
            yield token
