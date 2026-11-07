"""
Pydantic schemas for Milestone 4: Career Gap Analysis & Explainable Coverage Scoring.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.job import ParsedJobDescription
from app.schemas.matching import MatchMethod
from app.schemas.parsed_resume import ParsedResume


class RequirementClassification(str, Enum):
    """Classification indicating the depth and validity of candidate evidence."""
    MATCHED = "matched"
    PARTIALLY_DEMONSTRATED = "partially_demonstrated"
    NOT_DEMONSTRATED = "not_demonstrated"


class RequirementType(str, Enum):
    """Distinction between mandatory and bonus job qualifications."""
    REQUIRED = "required"
    PREFERRED = "preferred"


class GapAnalysisItem(BaseModel):
    """Detailed evaluation and explanation for an individual job requirement."""
    requirement: str = Field(..., description="The evaluated job requirement or skill name")
    requirement_type: RequirementType = Field(..., description="Required vs. preferred")
    classification: RequirementClassification = Field(..., description="Matched, partially demonstrated, or not demonstrated")
    match_method: MatchMethod = Field(..., description="Exact, normalized, semantic, or none")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    resume_evidence: Optional[str] = Field(None, description="Verbatim resume evidence supporting this requirement")
    job_evidence: Optional[str] = Field(None, description="Verbatim statement from the job description")
    explanation: str = Field(..., description="Transparent rationale for why this classification was assigned")
    suggested_improvement: Optional[str] = Field(None, description="Actionable direction to demonstrate or verify this skill")


class CoverageBreakdown(BaseModel):
    """Transparent scoring calculation for a requirement category."""
    total_count: int = Field(..., description="Total number of requirements evaluated")
    matched_count: int = Field(..., description="Number of requirements classified as matched (weight 1.0)")
    partial_count: int = Field(..., description="Number of requirements classified as partially demonstrated (weight 0.5)")
    not_demonstrated_count: int = Field(..., description="Number of requirements not demonstrated (weight 0.0)")
    coverage_score: Optional[float] = Field(None, description="Calculated percentage (0.0 to 100.0) or null if no requirements exist")
    calculation_explanation: str = Field(..., description="Human-readable formula and breakdown of the score calculation")


class OverallCoverage(BaseModel):
    """Overall job requirement coverage combining required and preferred scores."""
    overall_score: Optional[float] = Field(None, description="Weighted requirement coverage percentage (0.0 to 100.0) or null if no requirements exist")
    required_weight_percent: float = Field(..., description="Weight assigned to required criteria (e.g. 80.0)")
    preferred_weight_percent: float = Field(..., description="Weight assigned to preferred criteria (e.g. 20.0)")
    explanation: str = Field(..., description="Detailed explanation of the weighted score calculation")
    disclaimer: str = Field(
        default="This score measures observable requirement coverage based strictly on provided text evidence. It is NOT a hiring probability, ATS ranking score, or prediction of candidate success.",
        description="Non-misleading disclosure regarding the metric's purpose",
    )


class GapAnalysisRequest(BaseModel):
    """Input payload accepting parsed resume and job description."""
    resume: ParsedResume = Field(..., description="Structured parsed resume from Milestone 2")
    job_description: ParsedJobDescription = Field(..., description="Structured parsed job description from Milestone 2")


class GapAnalysisResponse(BaseModel):
    """Complete explainable gap analysis report."""
    results: List[GapAnalysisItem] = Field(..., description="Item-by-item breakdown of all requirements")
    matched_requirements: List[GapAnalysisItem] = Field(default_factory=list, description="Requirements with direct, verified evidence")
    partially_demonstrated_requirements: List[GapAnalysisItem] = Field(default_factory=list, description="Requirements with related but incomplete or unverified evidence")
    not_demonstrated_requirements: List[GapAnalysisItem] = Field(default_factory=list, description="Requirements with no identifiable resume evidence")
    required_coverage: CoverageBreakdown = Field(..., description="Coverage metrics for mandatory skills")
    preferred_coverage: CoverageBreakdown = Field(..., description="Coverage metrics for preferred skills")
    overall_coverage: OverallCoverage = Field(..., description="Overall weighted requirement coverage analysis")
