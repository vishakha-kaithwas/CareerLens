"""
API integration tests for POST /api/v1/resumes/extract.

Verifies:
1. Successful resume upload and structured text response.
2. File extension validation (.txt rejected).
3. Non-PDF magic byte validation (renamed text file rejected).
4. Empty file handling (0 bytes).
5. Scanned/image-only PDF detection (returns 422 with clear guidance).
6. File size validation (oversized file rejected before buffering entire file).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_extract_valid_pdf(async_client: AsyncClient, sample_valid_resume_pdf):
    files = {"file": ("my_resume.pdf", sample_valid_resume_pdf, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["filename"] == "my_resume.pdf"
    assert data["total_pages"] == 2
    assert "John Doe" in data["full_text"]
    assert "FastAPI" in data["full_text"]
    assert len(data["pages"]) == 2
    assert data["is_scanned"] is False
    assert data["metadata"]["title"] == "John Doe Resume"


@pytest.mark.asyncio
async def test_api_rejects_invalid_extension(async_client: AsyncClient):
    files = {"file": ("resume.txt", b"plain text resume", "text/plain")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert "extension" in payload["message"].lower()


@pytest.mark.asyncio
async def test_api_rejects_fake_pdf_magic_bytes(async_client: AsyncClient):
    # Extension is .pdf, but payload is not a PDF
    fake_content = b"This is a fake PDF without proper magic bytes."
    files = {"file": ("resume.pdf", fake_content, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert "header" in payload["message"].lower() or "magic" in payload["message"].lower()


@pytest.mark.asyncio
async def test_api_rejects_empty_file(async_client: AsyncClient, sample_empty_pdf):
    files = {"file": ("empty.pdf", sample_empty_pdf, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert "empty" in payload["message"].lower()


@pytest.mark.asyncio
async def test_api_detects_scanned_pdf(async_client: AsyncClient, sample_scanned_pdf):
    files = {"file": ("scanned_resume.pdf", sample_scanned_pdf, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    # Scanned PDF returns 422 with a helpful message
    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert "scanned document" in payload["message"].lower() or "image-based" in payload["message"].lower()
    assert payload["errors"]["type"] == "scanned_or_image_pdf"
    assert "suggestion" in payload["errors"]
    assert "possible_reasons" in payload["errors"]


@pytest.mark.asyncio
async def test_api_upload_just_below_limit(async_client: AsyncClient, make_pdf):
    """Verifies that an upload just below the 5 MB limit is accepted and processed."""
    target_size = (5 * 1024 * 1024) - (128 * 1024)
    # Ensure text is well above 50 chars so scanned-check passes
    rich_text = "John Doe Software Engineer with skills in Python, FastAPI, and Docker. " * 3
    base_pdf = make_pdf(text_content=rich_text, pages=1)
    # Add comment padding to reach target_size
    padding_needed = target_size - len(base_pdf)
    pdf_bytes = base_pdf + b"%" + b"A" * (padding_needed - 1)
    assert len(pdf_bytes) == target_size

    files = {"file": ("below_limit.pdf", pdf_bytes, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["filename"] == "below_limit.pdf"


@pytest.mark.asyncio
async def test_api_upload_exactly_at_limit(async_client: AsyncClient, make_pdf):
    """Verifies that an upload exactly at 5 MB (5,242,880 bytes) is accepted."""
    exact_size = 5 * 1024 * 1024
    rich_text = "John Doe Software Engineer with skills in Python, FastAPI, and Docker. " * 3
    base_pdf = make_pdf(text_content=rich_text, pages=1)
    padding_needed = exact_size - len(base_pdf)
    pdf_bytes = base_pdf + b"%" + b"A" * (padding_needed - 1)
    assert len(pdf_bytes) == exact_size

    files = {"file": ("exact_limit.pdf", pdf_bytes, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["filename"] == "exact_limit.pdf"


@pytest.mark.asyncio
async def test_api_upload_above_file_limit_rejected_by_endpoint(async_client: AsyncClient, make_pdf):
    """
    Verifies that a file exceeding 5 MB (e.g. 5 MB + 10 KB) but within the multipart
    overhead threshold is caught and rejected by the endpoint-level streaming validator.
    """
    file_size = (5 * 1024 * 1024) + 10240  # 5 MB + 10 KB
    base_pdf = make_pdf(text_content="Oversized File", pages=1)
    padding = b"\n%" + b"X" * (file_size - len(base_pdf))
    pdf_bytes = base_pdf + padding

    files = {"file": ("slightly_oversized.pdf", pdf_bytes, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert "exceeds the maximum allowed size" in payload["message"].lower()


@pytest.mark.asyncio
async def test_api_upload_significantly_above_limit_rejected_by_asgi_middleware(async_client: AsyncClient):
    """
    Verifies that an oversized request (e.g. 7 MB payload) is intercepted and rejected
    by RequestSizeLimitMiddleware with HTTP 413 BEFORE multipart parsing or disk spooling.
    """
    # 7 MB payload
    oversized_body = b"X" * (7 * 1024 * 1024)
    headers = {
        "content-type": "multipart/form-data; boundary=boundary123",
        "content-length": str(len(oversized_body)),
    }
    response = await async_client.post(
        "/api/v1/resumes/extract",
        content=oversized_body,
        headers=headers,
    )

    assert response.status_code == 413
    payload = response.json()
    assert payload["success"] is False
    assert "request payload exceeds the maximum allowed request size" in payload["message"].lower()
    assert payload["errors"]["type"] == "request_payload_too_large"
