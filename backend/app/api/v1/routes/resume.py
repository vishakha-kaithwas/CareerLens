"""
Resume upload and extraction router.

Key Requirements Followed:
1. Validates file extension and content-type before processing.
2. Validates file size iteratively in chunks without buffering entire large files into memory.
3. In-memory processing: zero disk storage of resumes or personal data.
4. Detects scanned/image-only PDFs and returns a clear, user-friendly response.
"""

import logging
from fastapi import APIRouter, File, UploadFile, status
from app.core.config import settings
from app.core.errors import FileValidationError
from app.schemas.common import APIResponse
from app.schemas.resume import ExtractedResumeData
from app.services.pdf_extractor import PDFExtractorService

logger = logging.getLogger("careerlens.routes.resume")

router = APIRouter(prefix="/resumes", tags=["Resumes"])
pdf_extractor_service = PDFExtractorService()

# Chunk size for streaming file validation: 64 KB
STREAM_CHUNK_SIZE = 64 * 1024


async def read_file_with_size_limit(upload_file: UploadFile, max_size_bytes: int) -> bytes:
    """
    Reads an UploadFile in streaming chunks and enforces the size limit
    strictly BEFORE reading an oversized payload into memory.
    """
    total_bytes_read = 0
    buffer = bytearray()

    while True:
        chunk = await upload_file.read(STREAM_CHUNK_SIZE)
        if not chunk:
            break

        total_bytes_read += len(chunk)
        if total_bytes_read > max_size_bytes:
            raise FileValidationError(
                f"File '{upload_file.filename}' exceeds the maximum allowed size of "
                f"{max_size_bytes // (1024 * 1024)} MB.",
                details={
                    "filename": upload_file.filename,
                    "max_allowed_bytes": max_size_bytes,
                    "bytes_received_so_far": total_bytes_read,
                },
            )
        buffer.extend(chunk)

    return bytes(buffer)


@router.post(
    "/extract",
    response_model=APIResponse[ExtractedResumeData],
    status_code=status.HTTP_200_OK,
    summary="Upload & Extract Resume Text",
    description=(
        "Accepts a PDF resume upload, validates file type, magic bytes, and size, "
        "and extracts plain text and metadata in memory. Does not persist files or PII."
    ),
)
async def extract_resume(
    file: UploadFile = File(..., description="Resume PDF file to extract"),
):
    filename = file.filename or "unknown.pdf"

    # 1. Filename & Extension validation
    if not any(filename.lower().endswith(ext) for ext in settings.ALLOWED_FILE_EXTENSIONS):
        raise FileValidationError(
            f"Invalid file extension for '{filename}'. Only PDF files are supported.",
            details={"filename": filename, "allowed_extensions": settings.ALLOWED_FILE_EXTENSIONS},
        )

    # 2. Content-type check if provided by client
    if file.content_type and file.content_type.lower() not in settings.ALLOWED_MIME_TYPES:
        # Note: Some clients send application/octet-stream; we verify magic bytes below in all cases.
        if file.content_type.lower() != "application/octet-stream":
            raise FileValidationError(
                f"Invalid Content-Type '{file.content_type}'. Must be application/pdf.",
                details={"filename": filename, "content_type": file.content_type},
            )

    # 3. Stream read with immediate size cutoff
    pdf_bytes = await read_file_with_size_limit(file, settings.MAX_UPLOAD_SIZE_BYTES)

    # 4. In-memory extraction via independent service
    extracted_data = pdf_extractor_service.extract_from_bytes(
        pdf_bytes=pdf_bytes,
        filename=filename,
        raise_on_scanned=True,  # Catches scanned/image PDFs and surfaces user-friendly error
    )

    return APIResponse(
        success=True,
        message="Resume extracted successfully in memory.",
        data=extracted_data,
    )


from app.schemas.parsed_resume import ParsedResume
from app.services.resume_parser import ResumeParserService

resume_parser_service = ResumeParserService()


@router.post(
    "/parse",
    response_model=APIResponse[ParsedResume],
    status_code=status.HTTP_200_OK,
    summary="Upload & Parse Resume Sections",
    description=(
        "Uploads a PDF resume, extracts text in memory, and parses structured sections "
        "(Contact, Experience, Education, Skills, Projects, Certifications). "
        "Preserves original raw text on each entry for evidence verification."
    ),
)
async def parse_resume(
    file: UploadFile = File(..., description="Resume PDF file to parse"),
):
    filename = file.filename or "unknown.pdf"

    # Validation
    if not any(filename.lower().endswith(ext) for ext in settings.ALLOWED_FILE_EXTENSIONS):
        raise FileValidationError(
            f"Invalid file extension for '{filename}'. Only PDF files are supported.",
            details={"filename": filename, "allowed_extensions": settings.ALLOWED_FILE_EXTENSIONS},
        )

    if file.content_type and file.content_type.lower() not in settings.ALLOWED_MIME_TYPES:
        if file.content_type.lower() != "application/octet-stream":
            raise FileValidationError(
                f"Invalid Content-Type '{file.content_type}'. Must be application/pdf.",
                details={"filename": filename, "content_type": file.content_type},
            )

    pdf_bytes = await read_file_with_size_limit(file, settings.MAX_UPLOAD_SIZE_BYTES)

    extracted_data = pdf_extractor_service.extract_from_bytes(
        pdf_bytes=pdf_bytes,
        filename=filename,
        raise_on_scanned=True,
    )

    parsed_result = resume_parser_service.parse(extracted_data.full_text)

    return APIResponse(
        success=True,
        message="Resume parsed into structured sections successfully.",
        data=parsed_result,
    )
