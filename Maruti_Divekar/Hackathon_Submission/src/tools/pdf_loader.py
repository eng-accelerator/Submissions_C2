"""PDF document loading and text extraction."""
from typing import Optional
import fitz  # PyMuPDF
import os

class PDFLoader:
    """Loads and extracts text from PDF documents."""
    
    @staticmethod
    def load_text(file_path: str, 
                 start_page: Optional[int] = None,
                 end_page: Optional[int] = None) -> str:
        """Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            start_page: First page to extract (0-based, optional)
            end_page: Last page to extract (optional)
            
        Returns:
            Extracted text content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        try:
            doc = fitz.open(file_path)
            
            # Handle page range
            start = start_page if start_page is not None else 0
            end = end_page if end_page is not None else doc.page_count
            
            # Extract text from pages
            text = []
            for page_num in range(start, end):
                page = doc[page_num]
                text.append(page.get_text())
            
            return "\n\n".join(text)
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        finally:
            if 'doc' in locals():
                doc.close()