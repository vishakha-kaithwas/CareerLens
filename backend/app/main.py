import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.errors import (
    AppError,
    FileValidationError,
    ModelLoadingError,
    PDFExtractionError,
    ScannedPDFDetectedError,
)
from app.core.logging import setup_logging
from app.core.request_size import RequestSizeLimitMiddleware
from app.schemas.common import APIResponse
import starlette.formparsers

# Ensure multipart parser does not spool files under MAX_UPLOAD_SIZE_BYTES to disk
starlette.formparsers.MultiPartParser.spool_max_size = settings.MAX_UPLOAD_SIZE_BYTES
starlette.formparsers.MultiPartParser.max_part_size = settings.MAX_UPLOAD_SIZE_BYTES

logger = setup_logging(debug=settings.APP_DEBUG)


def create_application() -> FastAPI:
    """Application factory for CareerLens."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "CareerLens API: AI-Powered Career Gap Intelligence Platform. "
            "Analyzes qualifications vs. job requirements and provides actionable roadmaps."
        ),
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 1. Enforce strict request size limits at the ASGI boundary
    # This rejects oversized payloads before multipart parsing or temporary disk spooling.
    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_body_size_bytes=settings.MAX_REQUEST_BODY_SIZE_BYTES,
    )

    # 2. Configure CORS
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Centralized Exception Handlers

    @app.exception_handler(FileValidationError)
    async def file_validation_handler(request: Request, exc: FileValidationError):
        logger.warning("File validation error: %s | details: %s", exc.message, exc.details)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponse(
                success=False,
                message=exc.message,
                errors=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(ScannedPDFDetectedError)
    async def scanned_pdf_handler(request: Request, exc: ScannedPDFDetectedError):
        logger.info("Scanned PDF detected: %s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=APIResponse(
                success=False,
                message=exc.message,
                errors={
                    "type": "scanned_or_image_pdf",
                    "suggestion": (
                        "Please upload a standard text-based PDF resume created from Word, Google Docs, "
                        "or LaTeX, rather than a scanned photo or image PDF."
                    ),
                    **exc.details,
                },
            ).model_dump(),
        )

    @app.exception_handler(PDFExtractionError)
    async def pdf_extraction_handler(request: Request, exc: PDFExtractionError):
        logger.error("PDF extraction error: %s | details: %s", exc.message, exc.details)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=APIResponse(
                success=False,
                message=exc.message,
                errors=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(ModelLoadingError)
    async def model_loading_handler(request: Request, exc: ModelLoadingError):
        logger.error("Model loading error: %s | details: %s", exc.message, exc.details)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=APIResponse(
                success=False,
                message=exc.message,
                errors=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=APIResponse(
                success=False,
                message="Request payload validation failed.",
                errors=exc.errors(),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled server exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse(
                success=False,
                message="An unexpected server error occurred. Please try again later.",
                errors={"error": str(exc)} if settings.APP_DEBUG else None,
            ).model_dump(),
        )

    # Register API v1 routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
