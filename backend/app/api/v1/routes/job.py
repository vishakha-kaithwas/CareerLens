"""
Job Description Processing Router.

Accepts raw pasted job descriptions and extracts structured requirements:
- Inferred Job Title
- Required Skills
- Preferred Skills
- Tools & Technologies
- Soft Skills
- Experience Criteria
- Education Criteria
- Key Responsibilities
"""

import logging
from fastapi import APIRouter, status
from app.schemas.common import APIResponse
from app.schemas.job import JobDescriptionInput, ParsedJobDescription
from app.services.job_parser import JobDescriptionParserService

logger = logging.getLogger("careerlens.routes.job")

router = APIRouter(prefix="/jobs", tags=["Jobs"])
job_parser_service = JobDescriptionParserService()


@router.post(
    "/parse",
    response_model=APIResponse[ParsedJobDescription],
    status_code=status.HTTP_200_OK,
    summary="Parse Job Description",
    description=(
        "Accepts pasted job description text and extracts structured requirements: "
        "required vs. preferred skills, experience, education, tools, and responsibilities. "
        "Preserves raw text for transparent verification."
    ),
)
async def parse_job_description(payload: JobDescriptionInput):
    parsed_job = job_parser_service.parse(payload.text)

    return APIResponse(
        success=True,
        message="Job description parsed successfully.",
        data=parsed_job,
    )
