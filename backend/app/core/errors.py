from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppError(Exception):
    """Base application exception for domain-level errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class FileValidationError(AppError):
    """Raised when an uploaded file violates validation rules (size, type, header)."""
    pass


class PDFExtractionError(AppError):
    """Raised when parsing or reading the PDF fails (corruption, encryption, malformed data)."""
    pass


class ScannedPDFDetectedError(AppError):
    """Raised when a PDF contains insufficient selectable text, indicating scanned/image-only content."""
    pass


class ModelLoadingError(AppError):
    """Raised when the embedding or NLP model fails to load."""
    pass
