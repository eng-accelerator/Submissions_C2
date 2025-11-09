"""Document loading and text extraction tools."""
from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from typing import Optional
import io
import os
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

from src.tools.pdf_loader import PDFLoader

class FileLoader:
    @staticmethod
    def load_pdf_text(path: str) -> str:
        if path.startswith('http'):
            r = requests.get(path)
            r.raise_for_status()
            data = io.BytesIO(r.content)
        else:
            data = open(path, 'rb')
        if PyPDF2 is None:
            return ''
        reader = PyPDF2.PdfReader(data)
        texts = []
        for p in reader.pages:
            try:
                texts.append(p.extract_text() or '')
            except Exception:
                continue
        return '\n'.join(texts)
    
    @staticmethod
    def load_text(path: str) -> str:
        """Load text content from a file."""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

class HTMLLoader:
    @staticmethod
    def load_text(url: str, max_retries: int = 3) -> str:
        """Load and extract text from HTML content.
        
        Args:
            url: URL to fetch and extract text from
            max_retries: Number of times to retry failed requests
            
        Returns:
            Extracted text content with formatting removed
            
        Raises:
            requests.exceptions.RequestException: If fetching fails after retries
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        last_error = None
        for attempt in range(max_retries):
            try:
                r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                r.raise_for_status()
                
                # Detect and handle common anti-bot measures
                if 'captcha' in r.text.lower() or 'access denied' in r.text.lower():
                    raise requests.exceptions.RequestException("Possible anti-bot protection")
                    
                soup = BeautifulSoup(r.text, 'html.parser')
                
                # Remove non-content elements
                for s in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
                    s.decompose()
                    
                # Extract article content if present
                article = soup.find('article')
                if article:
                    text = article.get_text(separator=' ', strip=True)
                else:
                    # Fall back to main content
                    text = soup.get_text(separator=' ', strip=True)
                    
                # Basic text cleaning
                text = ' '.join(text.split())
                return text
                
            except Exception as e:
                last_error = e
                # Exponential backoff between retries
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                    continue
                    
        raise last_error or requests.exceptions.RequestException("Failed to load URL")

class APILoader:
    """Placeholder for API data loading."""
    @staticmethod
    def load_data(url: str, headers: Optional[dict] = None) -> dict:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
