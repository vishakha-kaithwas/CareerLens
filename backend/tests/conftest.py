"""
Pytest configuration and test helpers.
Provides fixtures to dynamically generate valid text PDFs, scanned/image-only PDFs,
corrupt PDFs, and encrypted PDFs completely in memory for testing.
"""

import io
import pymupdf as fitz  # PyMuPDF
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    """Async HTTP client bound to the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def make_pdf():
    """Factory fixture to create customized PDF byte streams in memory."""
    def _create(
        text_content: str = "Default Resume Text",
        pages: int = 1,
        title: str = "Sample Resume",
        author: str = "Jane Doe",
    ) -> bytes:
        doc = fitz.open()
        for i in range(pages):
            page = doc.new_page(width=595, height=842)  # A4 size
            # Insert text at top
            page.insert_text(fitz.Point(50, 72), f"Page {i + 1}\n{text_content}")

        doc.set_metadata({
            "title": title,
            "author": author,
            "creator": "CareerLens Test Suite",
        })
        pdf_bytes = doc.write()
        doc.close()
        return pdf_bytes

    return _create


@pytest.fixture
def sample_valid_resume_pdf(make_pdf) -> bytes:
    """Returns a realistic, text-rich multi-page resume PDF."""
    resume_text = """
    John Doe
    Email: john.doe@example.com | Phone: +1-555-0199 | Location: New York, NY
    GitHub: github.com/johndoe | LinkedIn: linkedin.com/in/johndoe

    SUMMARY
    Senior Software Engineer with 5+ years of experience specializing in Python,
    FastAPI, distributed backend systems, and machine learning pipelines.

    EXPERIENCE
    Senior Backend Engineer - TechCorp (2021 - Present)
    - Architected and deployed microservices handling 25,000 requests/sec with FastAPI and Redis.
    - Reduced API p99 latency by 35% through query optimization and database indexing.
    - Built asynchronous worker pipelines using Celery and PostgreSQL.

    Software Engineer - DataFlow Systems (2018 - 2021)
    - Developed REST APIs using Python and Flask for internal analytics dashboards.
    - Implemented automated CI/CD deployment pipelines using Docker and GitHub Actions.

    EDUCATION
    Bachelor of Science in Computer Science
    University of Engineering & Technology (2014 - 2018)

    TECHNICAL SKILLS
    Languages: Python, SQL, TypeScript, Bash
    Frameworks: FastAPI, Flask, PyTorch, Scikit-Learn
    Infrastructure: Docker, Kubernetes, AWS, PostgreSQL, Redis
    """
    return make_pdf(text_content=resume_text, pages=2, title="John Doe Resume")


@pytest.fixture
def sample_scanned_pdf() -> bytes:
    """
    Returns a PDF with pages but NO text (simulating a scanned photo or image PDF).
    """
    doc = fitz.open()
    doc.new_page(width=595, height=842)  # Blank A4 page
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


@pytest.fixture
def sample_corrupt_pdf() -> bytes:
    """Returns invalid PDF bytes with a valid header prefix but corrupt body."""
    return b"%PDF-1.4\n%corrupted_non_readable_gibberish_bytes_xyz\x00\xff"


@pytest.fixture
def sample_empty_pdf() -> bytes:
    """Returns 0 bytes."""
    return b""
