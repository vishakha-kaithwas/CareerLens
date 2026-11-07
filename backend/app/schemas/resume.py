from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PageTextContent(BaseModel):
    """Text and metrics for an individual page."""
    page_number: int = Field(..., description="1-indexed page number")
    text: str = Field(..., description="Extracted plain text for the page")
    character_count: int = Field(..., description="Number of characters in the page text")
    word_count: int = Field(..., description="Number of words in the page text")


class PDFMetadata(BaseModel):
    """Metadata extracted from the PDF document structure."""
    title: Optional[str] = Field(None, description="Document title metadata")
    author: Optional[str] = Field(None, description="Document author metadata")
    creator: Optional[str] = Field(None, description="Application or software that created the PDF")
    producer: Optional[str] = Field(None, description="Producer software metadata")
    creation_date: Optional[str] = Field(None, description="Creation timestamp if available")
    modification_date: Optional[str] = Field(None, description="Modification timestamp if available")
    is_encrypted: bool = Field(False, description="Whether the PDF was encrypted")


class ExtractedResumeData(BaseModel):
    """Complete in-memory extraction payload for a processed resume."""
    filename: str = Field(..., description="Original filename of the uploaded PDF")
    total_pages: int = Field(..., description="Total number of pages parsed")
    total_characters: int = Field(..., description="Total characters extracted across all pages")
    total_words: int = Field(..., description="Total words extracted across all pages")
    is_scanned: bool = Field(False, description="Flag indicating if the document appears to be scanned or image-only")
    metadata: PDFMetadata = Field(..., description="PDF structural metadata")
    pages: List[PageTextContent] = Field(..., description="Extracted content per page")
    full_text: str = Field(..., description="Concatenated clean text from all pages")
