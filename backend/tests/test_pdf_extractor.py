"""
Unit tests for the independent PDFExtractorService.
Tests valid extraction, metadata, empty files, non-PDF files,
corrupt PDFs, and scanned/image-only PDF detection.
"""

import pytest
from app.core.errors import (
    FileValidationError,
    PDFExtractionError,
    ScannedPDFDetectedError,
)
from app.services.pdf_extractor import PDFExtractorService


def test_extractor_valid_pdf(sample_valid_resume_pdf):
    service = PDFExtractorService(min_text_chars_threshold=50)
    result = service.extract_from_bytes(sample_valid_resume_pdf, filename="resume.pdf")

    assert result.filename == "resume.pdf"
    assert result.total_pages == 2
    assert result.total_characters > 100
    assert result.total_words > 20
    assert result.is_scanned is False
    assert "John Doe" in result.full_text
    assert "FastAPI" in result.full_text
    assert len(result.pages) == 2
    assert result.pages[0].page_number == 1
    assert result.metadata.title == "John Doe Resume"


def test_extractor_empty_bytes():
    service = PDFExtractorService()
    with pytest.raises(FileValidationError) as exc_info:
        service.extract_from_bytes(b"", filename="empty.pdf")
    assert "empty" in exc_info.value.message.lower()


def test_extractor_non_pdf_magic_bytes():
    service = PDFExtractorService()
    non_pdf = b"Hello, this is just a plain text file pretending to be a pdf."
    with pytest.raises(FileValidationError) as exc_info:
        service.extract_from_bytes(non_pdf, filename="fake.pdf")
    assert "header" in exc_info.value.message.lower() or "magic" in exc_info.value.message.lower()


def test_extractor_corrupt_pdf(sample_corrupt_pdf):
    service = PDFExtractorService()
    with pytest.raises(PDFExtractionError) as exc_info:
        service.extract_from_bytes(sample_corrupt_pdf, filename="corrupt.pdf")
    assert "corrupted" in exc_info.value.message.lower()


def test_extractor_scanned_pdf_detected(sample_scanned_pdf):
    """Verifies that an image-only / textless PDF triggers ScannedPDFDetectedError."""
    service = PDFExtractorService(min_text_chars_threshold=50)
    with pytest.raises(ScannedPDFDetectedError) as exc_info:
        service.extract_from_bytes(sample_scanned_pdf, filename="scanned.pdf", raise_on_scanned=True)

    assert "scanned document" in exc_info.value.message.lower() or "image-based" in exc_info.value.message.lower()
    assert exc_info.value.details["characters_extracted"] < 50


def test_extractor_scanned_pdf_flag_when_not_raised(sample_scanned_pdf):
    """When raise_on_scanned=False, should return data with is_scanned=True."""
    service = PDFExtractorService(min_text_chars_threshold=50)
    result = service.extract_from_bytes(sample_scanned_pdf, filename="scanned.pdf", raise_on_scanned=False)
    assert result.is_scanned is True
    assert result.total_characters == 0
