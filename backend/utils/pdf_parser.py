"""PDF document parser."""
from typing import List, Dict
from pypdf import PdfReader


class PDFParser:
    """Parser for PDF documents, extracts text by page."""
    
    def parse(self, file_path: str) -> List[Dict]:
        """
        Parse a PDF file and extract text by page.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of dicts with 'page_number' and 'content' keys
        """
        pages = []
        
        try:
            reader = PdfReader(file_path)
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                
                if text and text.strip():
                    pages.append({
                        "page_number": page_num,
                        "content": text.strip(),
                    })
        
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {e}")
        
        if not pages:
            raise ValueError("PDF contains no extractable text")
        
        return pages
