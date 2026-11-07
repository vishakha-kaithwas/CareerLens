"""
Roadmap API Routes.

Provides endpoints to generate personalized, dependency-aware improvement roadmaps
grounded in candidate career gaps.
"""

import logging
from fastapi import APIRouter, status

from app.schemas.common import APIResponse
from app.schemas.roadmap import RoadmapRequest, RoadmapResponse
from app.services.roadmap_generator import RoadmapGeneratorService

logger = logging.getLogger("careerlens.routes.roadmap")

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])
roadmap_generator_service = RoadmapGeneratorService()


@router.post(
    "/generate",
    response_model=APIResponse[RoadmapResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Personalized Improvement Roadmap",
    description=(
        "Analyzes career gaps between candidate resume and job requirements, "
        "identifies unmet prerequisites via skill dependency graphs, and generates "
        "a sequenced, prioritized learning roadmap with specific practical projects."
    ),
)
async def generate_roadmap(payload: RoadmapRequest):
    roadmap_result = roadmap_generator_service.generate_roadmap(
        resume=payload.resume,
        job_description=payload.job_description,
    )

    return APIResponse(
        success=True,
        message="Personalized improvement roadmap generated successfully.",
        data=roadmap_result,
    )
