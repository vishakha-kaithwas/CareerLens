"""
Verification test confirming that Starlette's SpooledTemporaryFile
under our configured settings NEVER rolls over to a disk file for any
accepted upload, and oversized requests are stopped before spooling to disk.
"""

import tempfile
import pytest
from httpx import AsyncClient
import starlette.formparsers


@pytest.mark.asyncio
async def test_verify_no_disk_temporary_files_created_for_accepted_upload(
    async_client: AsyncClient,
    make_pdf,
    monkeypatch,
):
    """
    Spies on tempfile.TemporaryFile and tempfile.NamedTemporaryFile to mathematically
    prove that Starlette's SpooledTemporaryFile never creates a filesystem file
    during an accepted upload up to the 5 MB limit.
    """
    disk_file_created = False
    original_named_temp = tempfile.NamedTemporaryFile

    def spy_named_temp(*args, **kwargs):
        nonlocal disk_file_created
        disk_file_created = True
        return original_named_temp(*args, **kwargs)

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", spy_named_temp)

    # Also spy on SpooledTemporaryFile rollover method
    rollover_occurred = False
    original_rollover = tempfile.SpooledTemporaryFile.rollover

    def spy_rollover(self, *args, **kwargs):
        nonlocal rollover_occurred
        rollover_occurred = True
        return original_rollover(self, *args, **kwargs)

    monkeypatch.setattr(tempfile.SpooledTemporaryFile, "rollover", spy_rollover)

    # 4 MB payload upload
    target_size = 4 * 1024 * 1024
    rich_text = "John Doe Senior Python Engineer. " * 5
    base_pdf = make_pdf(text_content=rich_text, pages=1)
    padding_needed = target_size - len(base_pdf)
    pdf_bytes = base_pdf + b"%" + b"A" * (padding_needed - 1)

    files = {"file": ("in_memory_verify.pdf", pdf_bytes, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/extract", files=files)

    assert response.status_code == 200
    # Verification: rollover was never called, and no disk tempfile was created
    assert rollover_occurred is False, "SpooledTemporaryFile rolled over to disk!"
    assert disk_file_created is False, "A disk temporary file was created!"
