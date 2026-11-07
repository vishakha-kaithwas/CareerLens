"""
API routes for Milestone 6: Evidence-Based Resume Improvement.
"""

import logging
from fastapi import APIRouter, Depends, status

from app.schemas.common import APIResponse
from app.schemas.improvement import ResumeImprovementRequest, ResumeImprovementResponse
from app.services.resume_improver import ResumeImprovementService

logger = logging.getLogger("careerlens.routes.improvement")

router = APIRouter(prefix="/resume", tags=["Resume Improvement"])


resume_improver_service = ResumeImprovementService()


def get_resume_improver_service() -> ResumeImprovementService:
    """Dependency provider for ResumeImprovementService."""
    return resume_improver_service


@router.post(
    "/improve",
    response_model=APIResponse[ResumeImprovementResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate evidence-based resume improvements without fabrication",
    description=(
        "Analyzes parsed resume content against target job requirements, suggesting truthful bullet point "
        "refinements, section recommendations, and asking clarification questions rather than inventing metrics."
    ),
)
async def improve_resume(
    payload: ResumeImprovementRequest,
    service: ResumeImprovementService = Depends(get_resume_improver_service),
) -> APIResponse[ResumeImprovementResponse]:
    """
    Evaluates resume content, extracts weak verbs and vague phrasing, connects bullets to target job requirements,
    and returns evidence-backed improvements.
    """
    logger.info(
        "Received resume improvement request for candidate: %s vs job: %s",
        payload.resume.contact.name or "Anonymous",
        payload.job_description.title or "Target Job",
    )

    improvement_report = service.generate_improvements(
        resume=payload.resume,
        job_description=payload.job_description,
        gap_analysis=payload.gap_analysis,
    )

    return APIResponse(
        success=True,
        message="Evidence-based resume improvement suggestions generated successfully.",
        data=improvement_report,
    )
