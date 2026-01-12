"""Text and Markdown document parser."""
from typing import List, Dict


class TextParser:
    """Parser for text and markdown files, tracks line numbers."""
    
    def __init__(self, lines_per_chunk: int = 50):
        """
        Initialize parser.
        
        Args:
            lines_per_chunk: Number of lines to group together
        """
        self.lines_per_chunk = lines_per_chunk
    
    def parse(self, file_path: str) -> List[Dict]:
        """
        Parse a text/markdown file and extract content with line ranges.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of dicts with 'line_start', 'line_end', and 'content' keys
        """
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
        
        if not lines:
            raise ValueError("File is empty")
        
        # Group lines into chunks
        current_chunk = []
        chunk_start = 1
        
        for line_num, line in enumerate(lines, start=1):
            current_chunk.append(line)
            
            # Create chunk when reaching limit or end of file
            if len(current_chunk) >= self.lines_per_chunk or line_num == len(lines):
                content = "".join(current_chunk).strip()
                
                if content:  # Only add non-empty chunks
                    chunks.append({
                        "line_start": chunk_start,
                        "line_end": line_num,
                        "content": content,
                    })
                
                current_chunk = []
                chunk_start = line_num + 1
        
        if not chunks:
            raise ValueError("File contains no content")
        
        return chunks
