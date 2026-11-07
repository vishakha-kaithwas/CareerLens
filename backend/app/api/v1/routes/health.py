import time
from typing import Dict
from fastapi import APIRouter, status
from app.core.config import settings
from app.schemas.common import APIResponse

router = APIRouter(tags=["Health"])

START_TIME = time.time()


@router.get(
    "/health",
    response_model=APIResponse[Dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns application health status, version, and running environment.",
)
async def health_check():
    uptime_seconds = int(time.time() - START_TIME)
    return APIResponse(
        success=True,
        message="Service is healthy and operational.",
        data={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "status": "healthy",
            "uptime_seconds": str(uptime_seconds),
        },
    )
