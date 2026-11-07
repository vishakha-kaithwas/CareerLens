from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    APP_NAME: str = "CareerLens"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # CORS origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # File Upload Restrictions (Security and Resource Protection)
    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf"]
    ALLOWED_MIME_TYPES: List[str] = ["application/pdf"]

    # Maximum allowed request body size for ASGI middleware.
    # Accounts for multipart headers, boundaries, and form fields overhead (e.g. 256 KB)
    MULTIPART_OVERHEAD_BYTES: int = 256 * 1024  # 256 KB
    
    @property
    def MAX_REQUEST_BODY_SIZE_BYTES(self) -> int:
        return self.MAX_UPLOAD_SIZE_BYTES + self.MULTIPART_OVERHEAD_BYTES

    # Minimum character threshold across entire document to determine if PDF is scanned/image-only
    MIN_TEXT_CHARS_THRESHOLD: int = 50

    # Milestone 3: Semantic Similarity & Embedding Settings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.65

    # Milestone 4: Career Gap Analysis & Coverage Scoring Weights
    SCORE_WEIGHT_MATCHED: float = 1.0
    SCORE_WEIGHT_PARTIAL: float = 0.5
    SCORE_WEIGHT_NOT_DEMONSTRATED: float = 0.0

    OVERALL_REQUIRED_WEIGHT: float = 0.80
    OVERALL_PREFERRED_WEIGHT: float = 0.20


settings = Settings()
