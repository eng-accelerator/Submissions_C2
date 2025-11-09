"""
Text extraction service for various document formats.

Supports: TXT, PDF
Handles: Encoding detection, text cleaning, size limits
"""

import re
import unicodedata
from pathlib import Path
from typing import BinaryIO, Optional

from loguru import logger


# ============================================================================
# Custom Exceptions
# ============================================================================


class TextExtractionError(Exception):
    """Base exception for text extraction errors."""

    pass


class UnsupportedFileTypeError(TextExtractionError):
    """Raised when file type is not supported."""

    pass


class EmptyDocumentError(TextExtractionError):
    """Raised when document contains no text."""

    pass


class FileTooLargeError(TextExtractionError):
    """Raised when file exceeds size limit."""

    pass


# ============================================================================
# Text Extraction Service
# ============================================================================


class TextExtractionService:
    """
    Service for extracting text from various document formats.

    Supports:
    - Plain text (.txt)
    - PDF documents (.pdf)

    Features:
    - Automatic encoding detection
    - Text cleaning and normalization
    - Size limits
    - Error handling
    """

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {".txt", ".pdf"}

    def __init__(self, max_size_mb: int = 50) -> None:
        """
        Initialize text extraction service.

        Args:
            max_size_mb: Maximum file size in megabytes (default: 50MB)
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        logger.info(f"Initialized TextExtractionService (max_size: {max_size_mb}MB)")

    @property
    def supported_extensions(self) -> set[str]:
        """Get set of supported file extensions."""
        return self.SUPPORTED_EXTENSIONS.copy()

    def extract_from_file(
        self, file_path: Path, normalize_whitespace: bool = True
    ) -> str:
        """
        Extract text from a file.

        Args:
            file_path: Path to the file
            normalize_whitespace: Whether to normalize whitespace

        Returns:
            Extracted text content

        Raises:
            UnsupportedFileTypeError: If file type not supported
            FileTooLargeError: If file exceeds size limit
            EmptyDocumentError: If no text extracted
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_size_bytes:
            raise FileTooLargeError(
                f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds limit "
                f"({self.max_size_bytes / 1024 / 1024:.1f}MB)"
            )

        # Check extension
        extension = file_path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"Unsupported file type: {extension}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        logger.info(f"Extracting text from: {file_path.name}")

        # Extract based on type
        if extension == ".txt":
            text = self._extract_text_file(file_path)
        elif extension == ".pdf":
            text = self._extract_pdf_file(file_path)
        else:
            raise UnsupportedFileTypeError(f"No extractor for {extension}")

        # Clean and validate
        text = self.clean_text(text, normalize_whitespace=normalize_whitespace)

        if not text or not text.strip():
            raise EmptyDocumentError(f"No text content found in {file_path.name}")

        logger.info(f"Extracted {len(text)} characters from {file_path.name}")
        return text

    def extract_from_bytes(
        self,
        file_bytes: BinaryIO,
        filename: str,
        normalize_whitespace: bool = True,
    ) -> str:
        """
        Extract text from bytes stream.

        Args:
            file_bytes: File-like bytes object
            filename: Original filename (for extension detection)
            normalize_whitespace: Whether to normalize whitespace

        Returns:
            Extracted text content
        """
        extension = Path(filename).suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(f"Unsupported file type: {extension}")

        # Check size
        file_bytes.seek(0, 2)  # Seek to end
        size = file_bytes.tell()
        file_bytes.seek(0)  # Reset to beginning

        if size > self.max_size_bytes:
            raise FileTooLargeError(f"File size exceeds {self.max_size_bytes / 1024 / 1024}MB")

        if extension == ".txt":
            text = self._extract_text_bytes(file_bytes)
        elif extension == ".pdf":
            text = self._extract_pdf_bytes(file_bytes)
        else:
            raise UnsupportedFileTypeError(f"No extractor for {extension}")

        text = self.clean_text(text, normalize_whitespace=normalize_whitespace)

        if not text or not text.strip():
            raise EmptyDocumentError(f"No text content found in {filename}")

        return text

    def clean_text(self, text: str, normalize_whitespace: bool = True) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text to clean
            normalize_whitespace: Whether to normalize whitespace

        Returns:
            Cleaned text
        """
        # Remove null bytes and control characters (except newlines/tabs)
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

        # Normalize Unicode (NFD = decomposed form)
        text = unicodedata.normalize("NFKC", text)

        if normalize_whitespace:
            # Replace multiple spaces with single space
            text = re.sub(r" {2,}", " ", text)

            # Replace more than 2 newlines with 2
            text = re.sub(r"\n{3,}", "\n\n", text)

            # Remove trailing whitespace from each line
            text = "\n".join(line.rstrip() for line in text.split("\n"))

        return text.strip()

    # ========================================================================
    # Private extraction methods
    # ========================================================================

    def _extract_text_file(self, file_path: Path) -> str:
        """Extract text from plain text file."""
        # Try UTF-8 first
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback to latin-1 (never fails)
            logger.warning(f"UTF-8 decode failed for {file_path.name}, using latin-1")
            return file_path.read_text(encoding="latin-1")

    def _extract_text_bytes(self, file_bytes: BinaryIO) -> str:
        """Extract text from text bytes."""
        content = file_bytes.read()
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1", errors="ignore")

    def _extract_pdf_file(self, file_path: Path) -> str:
        """
        Extract text from PDF file.

        Uses pypdf as primary extractor.
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF extraction. "
                "Install with: pip install pypdf"
            )

        try:
            reader = PdfReader(str(file_path))
            text_parts = []

            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            if not text_parts:
                # Fallback to pdfminer.six
                logger.warning("pypdf failed, trying pdfminer.six")
                return self._extract_pdf_with_pdfminer(file_path)

            return "\n\n".join(text_parts)

        except Exception as e:
            logger.error(f"PDF extraction failed for {file_path.name}: {e}")
            # Try pdfminer as fallback
            try:
                return self._extract_pdf_with_pdfminer(file_path)
            except Exception as fallback_error:
                raise TextExtractionError(
                    f"Failed to extract PDF: {fallback_error}"
                ) from fallback_error

    def _extract_pdf_bytes(self, file_bytes: BinaryIO) -> str:
        """Extract text from PDF bytes."""
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("pypdf is required for PDF extraction")

        reader = PdfReader(file_bytes)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        if not text_parts:
            raise EmptyDocumentError("No text found in PDF")

        return "\n\n".join(text_parts)

    def _extract_pdf_with_pdfminer(self, file_path: Path) -> str:
        """
        Fallback PDF extraction using pdfminer.six.

        More robust for complex PDFs.
        """
        try:
            from pdfminer.high_level import extract_text
        except ImportError:
            raise ImportError(
                "pdfminer.six is required as PDF fallback. "
                "Install with: pip install pdfminer.six"
            )

        text = extract_text(str(file_path))
        if not text or not text.strip():
            raise EmptyDocumentError(f"No text extracted from {file_path.name}")

        return text

