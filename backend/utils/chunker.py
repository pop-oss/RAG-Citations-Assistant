"""Text chunking utilities for RAG."""
from typing import List, Dict


class TextChunker:
    """Chunk text documents for embedding and retrieval."""
    
    def __init__(
        self, 
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_content(
        self, 
        parsed_content: List[Dict],
        file_type: str
    ) -> List[Dict]:
        """
        Chunk parsed content into smaller pieces for embedding.
        
        Args:
            parsed_content: Output from PDFParser or TextParser
            file_type: 'pdf', 'md', or 'txt'
            
        Returns:
            List of chunk dicts with content and metadata
        """
        chunks = []
        
        for item in parsed_content:
            content = item.get("content", "")
            
            if not content:
                continue
            
            # For short content, keep as is
            if len(content) <= self.chunk_size:
                chunk = {
                    "content": content,
                }
                # Preserve metadata
                if file_type == "pdf":
                    chunk["page_number"] = item.get("page_number")
                else:
                    chunk["line_start"] = item.get("line_start")
                    chunk["line_end"] = item.get("line_end")
                
                chunks.append(chunk)
                continue
            
            # Split longer content into chunks
            text_chunks = self._split_text(content)
            
            for text_chunk in text_chunks:
                chunk = {
                    "content": text_chunk,
                }
                # Preserve metadata (same page/line range for all sub-chunks)
                if file_type == "pdf":
                    chunk["page_number"] = item.get("page_number")
                else:
                    chunk["line_start"] = item.get("line_start")
                    chunk["line_end"] = item.get("line_end")
                
                chunks.append(chunk)
        
        return chunks
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        Tries to split on sentence boundaries when possible.
        """
        chunks = []
        
        # Try to split on paragraphs first
        paragraphs = text.split("\n\n")
        
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) + 2 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Handle long paragraphs
                if len(para) > self.chunk_size:
                    # Split on sentences
                    sentences = self._split_sentences(para)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 > self.chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence
                        else:
                            current_chunk = current_chunk + " " + sentence if current_chunk else sentence
                else:
                    current_chunk = para
            else:
                current_chunk = current_chunk + "\n\n" + para if current_chunk else para
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Apply overlap
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on period, question mark, exclamation
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap to chunks."""
        overlapped = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            curr_chunk = chunks[i]
            
            # Get overlap from end of previous chunk
            overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk
            
            # Prepend overlap to current chunk
            overlapped.append(overlap_text + " " + curr_chunk)
        
        return overlapped
