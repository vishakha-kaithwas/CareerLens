"""
PDF Extractor Service using PyMuPDF (fitz).

This service is completely independent of FastAPI or any web framework.
It accepts raw bytes and filename, validates structure and magic bytes,
and produces structured text, metadata, and scanned/image-only detection.
"""

import logging
from typing import List, Optional
import pymupdf as fitz  # PyMuPDF

from app.core.config import settings
from app.core.errors import (
    FileValidationError,
    PDFExtractionError,
    ScannedPDFDetectedError,
)
from app.schemas.resume import ExtractedResumeData, PageTextContent, PDFMetadata

logger = logging.getLogger("careerlens.pdf_extractor")


class PDFExtractorService:
    """Independent service for parsing and extracting text from PDF documents."""

    def __init__(self, min_text_chars_threshold: Optional[int] = None):
        self.min_chars_threshold = (
            min_text_chars_threshold
            if min_text_chars_threshold is not None
            else settings.MIN_TEXT_CHARS_THRESHOLD
        )

    def validate_pdf_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> None:
        """
        Validates magic bytes and basic integrity before parsing.
        """
        if not pdf_bytes or len(pdf_bytes) == 0:
            raise FileValidationError(
                f"File '{filename}' is empty (0 bytes).",
                details={"filename": filename, "reason": "empty_file"},
            )

        # PDF standard requires files to start with '%PDF-' (allowing up to a few bytes header offset)
        header_sample = pdf_bytes[:1024]
        if b"%PDF-" not in header_sample:
            raise FileValidationError(
                f"File '{filename}' does not have a valid PDF header (%PDF-).",
                details={"filename": filename, "reason": "invalid_magic_bytes"},
            )

    def extract_from_bytes(
        self,
        pdf_bytes: bytes,
        filename: str = "resume.pdf",
        raise_on_scanned: bool = True,
    ) -> ExtractedResumeData:
        """
        Extracts structured text and metadata from PDF bytes completely in memory.
        
        Args:
            pdf_bytes: Raw bytes of the PDF file.
            filename: Original name of the uploaded document.
            raise_on_scanned: If True, raises ScannedPDFDetectedError when text count is below threshold.
                             If False, returns ExtractedResumeData with is_scanned=True.
        """
        self.validate_pdf_bytes(pdf_bytes, filename=filename)

        doc = None
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            logger.error("Failed to open PDF stream for %s: %s", filename, exc)
            raise PDFExtractionError(
                f"File '{filename}' is corrupted or not a readable PDF.",
                details={"filename": filename, "error": str(exc)},
            ) from exc

        try:
            if doc.is_encrypted:
                # Try decrypting with empty password
                try:
                    authenticated = doc.authenticate("")
                except Exception:
                    authenticated = 0

                if not authenticated:
                    raise PDFExtractionError(
                        f"File '{filename}' is password-protected and cannot be read.",
                        details={"filename": filename, "reason": "password_protected"},
                    )

            total_pages = len(doc)
            if total_pages == 0:
                raise PDFExtractionError(
                    f"File '{filename}' has 0 pages.",
                    details={"filename": filename, "reason": "zero_pages"},
                )

            # Metadata extraction
            raw_meta = doc.metadata or {}
            metadata = PDFMetadata(
                title=raw_meta.get("title") or None,
                author=raw_meta.get("author") or None,
                creator=raw_meta.get("creator") or None,
                producer=raw_meta.get("producer") or None,
                creation_date=raw_meta.get("creationDate") or None,
                modification_date=raw_meta.get("modDate") or None,
                is_encrypted=doc.is_encrypted,
            )

            pages_content: List[PageTextContent] = []
            full_text_parts: List[str] = []
            total_characters = 0
            total_words = 0

            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                # "text" layout preserves readable whitespace and line breaks
                page_text = page.get_text("text").strip()
                char_count = len(page_text)
                word_count = len(page_text.split()) if page_text else 0

                total_characters += char_count
                total_words += word_count

                pages_content.append(
                    PageTextContent(
                        page_number=page_idx + 1,
                        text=page_text,
                        character_count=char_count,
                        word_count=word_count,
                    )
                )
                if page_text:
                    full_text_parts.append(page_text)

            full_text = "\n\n".join(full_text_parts)

            # Check for potentially scanned, image-only, or non-extractable text
            # Calculate average characters per page to avoid misclassifying multi-page documents
            avg_chars_per_page = total_characters / total_pages if total_pages > 0 else 0
            is_scanned = total_characters < self.min_chars_threshold

            if is_scanned and raise_on_scanned:
                raise ScannedPDFDetectedError(
                    f"Uploaded PDF '{filename}' contains very little or no extractable text "
                    f"({total_characters} characters found across {total_pages} page(s)). "
                    f"It may be a scanned document, image-based PDF, or use non-standard font encodings. "
                    f"CareerLens requires a text-selectable PDF for accurate analysis.",
                    details={
                        "filename": filename,
                        "total_pages": total_pages,
                        "characters_extracted": total_characters,
                        "threshold": self.min_chars_threshold,
                        "possible_reasons": [
                            "The document is a scanned image or photo of a resume.",
                            "The PDF was exported as flattened curves or vector outlines without underlying text.",
                            "The document is an empty or almost blank template.",
                            "Non-standard custom font encodings prevented selectable text extraction."
                        ],
                    },
                )

            return ExtractedResumeData(
                filename=filename,
                total_pages=total_pages,
                total_characters=total_characters,
                total_words=total_words,
                is_scanned=is_scanned,
                metadata=metadata,
                pages=pages_content,
                full_text=full_text,
            )

        finally:
            if doc is not None:
                doc.close()
