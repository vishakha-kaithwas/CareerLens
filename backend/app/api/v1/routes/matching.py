"""
Matching API routes.

Provides endpoints for intelligent skill matching between parsed resumes
and job descriptions.
"""

import logging
from fastapi import APIRouter, status
from app.schemas.common import APIResponse
from app.schemas.matching import SkillMatchingRequest, SkillMatchingResponse
from app.services.skill_matcher import SkillMatcherService

logger = logging.getLogger("careerlens.routes.matching")

router = APIRouter(prefix="/matching", tags=["Matching"])
skill_matcher_service = SkillMatcherService()


@router.post(
    "/skills",
    response_model=APIResponse[SkillMatchingResponse],
    status_code=status.HTTP_200_OK,
    summary="Match Resume Skills against Job Requirements",
    description=(
        "Compares parsed resume information against job description requirements. "
        "Applies exact matching, taxonomy-based normalized matching, and dense semantic matching. "
        "Returns similarity scores and supporting resume/job evidence for explainability."
    ),
)
async def match_skills(payload: SkillMatchingRequest):
    matching_result = skill_matcher_service.match_skills(
        resume=payload.resume,
        job_description=payload.job_description,
    )

    return APIResponse(
        success=True,
        message="Skill matching completed successfully.",
        data=matching_result,
    )
