"""
Pydantic schemas for Milestone 6: Evidence-Based Resume Improvement.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.gap_analysis import GapAnalysisResponse
from app.schemas.job import ParsedJobDescription
from app.schemas.matching import SkillMatchingResponse
from app.schemas.parsed_resume import ParsedResume
from app.schemas.roadmap import RoadmapResponse


class SuggestionConfidence(str, Enum):
    """Strength of evidence supporting the improvement."""
    HIGH = "high"        # Fully grounded in candidate's existing experience/projects
    MEDIUM = "medium"    # Grounded in listed skills or conceptual relevance, needing candidate details
    LOW = "low"          # Heuristic suggestion requiring user input


class EvidenceReference(BaseModel):
    """Verbatim or structural evidence supporting a suggestion."""
    source_section: str = Field(..., description="Resume section (e.g., 'experience', 'projects', 'skills')")
    evidence_text: str = Field(..., description="Exact snippet or item from resume that justifies this suggestion")
    related_job_requirement: Optional[str] = Field(None, description="Job requirement that this evidence relates to")


class CandidateQuestion(BaseModel):
    """Specific clarification question asking candidate for truthful details rather than inventing them."""
    context: str = Field(..., description="The bullet point or area needing clarification")
    question: str = Field(..., description="What specific truthful detail the candidate should provide")
    why_needed: str = Field(..., description="Why this detail strengthens the resume honestly without hallucination")


class BulletImprovement(BaseModel):
    """An evidence-based improvement for a specific resume bullet or snippet."""
    id: str = Field(..., description="Unique identifier for this improvement suggestion")
    section_name: str = Field(..., description="Section name (e.g. 'experience', 'projects', 'summary')")
    original_text: str = Field(..., description="Original verbatim text from the resume")
    suggested_text: str = Field(..., description="Suggested improved phrasing grounded in real evidence")
    why_useful: str = Field(..., description="Explanation of why this change improves job relevance and clarity")
    relevant_job_requirement: Optional[str] = Field(None, description="Target job requirement addressed")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Specific resume evidence supporting this change")
    confidence: SuggestionConfidence = Field(..., description="Confidence / evidence strength (high, medium, low)")
    needs_candidate_info: bool = Field(False, description="Whether candidate must supply specific metrics/outcomes")
    candidate_questions: List[CandidateQuestion] = Field(default_factory=list, description="Clarification questions if additional information is needed")


class SectionRecommendation(BaseModel):
    """Section-level evaluation and tactical recommendations."""
    section_name: str = Field(..., description="Name of the section (e.g. 'summary', 'skills', 'experience', 'projects', 'certifications')")
    status: str = Field(..., description="Status summary (e.g. 'strong', 'needs_focus', 'missing', 'unaligned')")
    recommendations: List[str] = Field(default_factory=list, description="Actionable advice for this section")
    skills_to_highlight: List[str] = Field(default_factory=list, description="Candidate skills demonstrated in projects/experience that should be brought forward")
    irrelevant_or_repetitive_notes: List[str] = Field(default_factory=list, description="Observations on repetitive or distracting content")


class JobRelevanceAnalysis(BaseModel):
    """High-level analysis of resume alignment with target job description."""
    top_aligned_strengths: List[str] = Field(default_factory=list, description="Existing candidate strengths directly relevant to the target job")
    buried_skills: List[str] = Field(default_factory=list, description="Demonstrated skills buried in project bullets that deserve explicit section prominence")
    missing_critical_evidence: List[str] = Field(default_factory=list, description="Important job requirements with zero resume evidence")
    honesty_guardrails_applied: List[str] = Field(
        default_factory=lambda: [
            "No metrics, percentages, or numbers were invented.",
            "No skills or technologies were recommended without candidate's confirmed usage.",
            "Academic or personal projects were not converted into professional job titles.",
            "Candidate clarification requested wherever outcomes or scopes are ambiguous."
        ],
        description="Explicit disclosure of anti-hallucination rules applied",
    )


class ImprovementSummary(BaseModel):
    """Executive metrics of the improvement report."""
    total_bullet_improvements: int = Field(..., description="Total bullet improvement suggestions")
    high_confidence_improvements: int = Field(..., description="Improvements fully grounded in existing evidence")
    questions_for_candidate: int = Field(..., description="Total clarification questions requiring candidate input")
    overall_readiness: str = Field(..., description="Assessment of resume alignment for this specific role")


class ResumeImprovementRequest(BaseModel):
    """Input payload accepting parsed resume and job description (with optional M3/M4/M5 artifacts)."""
    resume: ParsedResume = Field(..., description="Structured parsed resume from Milestone 2")
    job_description: ParsedJobDescription = Field(..., description="Structured parsed job description from Milestone 2")
    gap_analysis: Optional[GapAnalysisResponse] = Field(None, description="Optional pre-computed gap analysis from Milestone 4")
    roadmap: Optional[RoadmapResponse] = Field(None, description="Optional pre-computed roadmap from Milestone 5")


class ResumeImprovementResponse(BaseModel):
    """Complete evidence-based resume improvement report."""
    summary: ImprovementSummary = Field(..., description="Executive summary metrics")
    bullet_improvements: List[BulletImprovement] = Field(default_factory=list, description="Itemized bullet-level improvements")
    section_recommendations: List[SectionRecommendation] = Field(default_factory=list, description="Section-by-section strategic guidance")
    job_relevance: JobRelevanceAnalysis = Field(..., description="Job relevance and alignment analysis")
    candidate_questions: List[CandidateQuestion] = Field(default_factory=list, description="Aggregated questions requiring candidate input")
