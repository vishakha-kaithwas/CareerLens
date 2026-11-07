from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.job import ParsedJobDescription
from app.schemas.parsed_resume import ParsedResume


class MatchMethod(str, Enum):
    """Strategy used to match a requirement against resume evidence."""
    EXACT = "exact"
    NORMALIZED = "normalized"
    SEMANTIC = "semantic"
    NONE = "none"


class SkillMatchItem(BaseModel):
    """Evidence and metrics for an individual requirement match."""
    job_requirement: str = Field(..., description="The job requirement or skill name")
    is_required: bool = Field(True, description="Whether this is a mandatory requirement vs preferred")
    is_matched: bool = Field(..., description="Whether a valid match was identified above the configured threshold")
    match_method: MatchMethod = Field(MatchMethod.NONE, description="Exact, normalized, semantic, or none")
    similarity_score: float = Field(..., description="Cosine similarity score between 0.0 and 1.0 (1.0 for exact/normalized)")
    matched_resume_skill: Optional[str] = Field(None, description="The resume skill or phrase that satisfied the requirement")
    resume_evidence: Optional[str] = Field(None, description="Original verbatim snippet or bullet point from the resume")
    job_evidence: Optional[str] = Field(None, description="Original verbatim sentence or requirement from the job description")


class SkillMatchingRequest(BaseModel):
    """Input payload accepting structured parsed resume and job description."""
    resume: ParsedResume = Field(..., description="Parsed resume output from Milestone 2")
    job_description: ParsedJobDescription = Field(..., description="Parsed job description output from Milestone 2")


class SkillMatchingResponse(BaseModel):
    """Detailed matching breakdown categorized by required and preferred skills."""
    required_matches: List[SkillMatchItem] = Field(default_factory=list, description="Matches for mandatory job requirements")
    preferred_matches: List[SkillMatchItem] = Field(default_factory=list, description="Matches for preferred/bonus qualifications")
    total_required_count: int = Field(..., description="Total mandatory requirements evaluated")
    total_preferred_count: int = Field(..., description="Total preferred requirements evaluated")
    matched_required_count: int = Field(..., description="Number of mandatory requirements satisfied")
    matched_preferred_count: int = Field(..., description="Number of preferred requirements satisfied")
