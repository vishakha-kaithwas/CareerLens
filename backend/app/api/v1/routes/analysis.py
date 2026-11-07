"""
Gap Analysis API Routes.

Provides endpoints to analyze candidate qualification gaps against job requirements
and compute explainable coverage scores.
"""

import logging
from fastapi import APIRouter, status

from app.schemas.common import APIResponse
from app.schemas.gap_analysis import GapAnalysisRequest, GapAnalysisResponse
from app.services.gap_analyzer import GapAnalyzerService

logger = logging.getLogger("careerlens.routes.analysis")

router = APIRouter(prefix="/analysis", tags=["Analysis"])
gap_analyzer_service = GapAnalyzerService()


@router.post(
    "/gaps",
    response_model=APIResponse[GapAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Analyze Career Gaps & Compute Coverage",
    description=(
        "Consumes parsed resume and job description information, executes skill matching, "
        "and classifies each requirement into Matched, Partially Demonstrated, or Not Demonstrated. "
        "Returns transparent coverage scores and actionable explanations grounded in evidence."
    ),
)
async def analyze_gaps(payload: GapAnalysisRequest):
    analysis_result = gap_analyzer_service.analyze_gaps(
        resume=payload.resume,
        job_description=payload.job_description,
    )

    return APIResponse(
        success=True,
        message="Career gap analysis completed successfully.",
        data=analysis_result,
    )
