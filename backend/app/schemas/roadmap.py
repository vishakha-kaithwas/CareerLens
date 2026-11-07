"""
Pydantic schemas for Milestone 5: Skill Dependency Intelligence & Personalized Improvement Roadmap.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.gap_analysis import GapAnalysisResponse
from app.schemas.job import ParsedJobDescription
from app.schemas.parsed_resume import ParsedResume


class RoadmapPriority(str, Enum):
    """Urgency / priority of a learning recommendation."""
    CRITICAL = "critical"  # Missing mandatory requirement with unmet prerequisites
    HIGH = "high"          # Missing mandatory requirement
    MEDIUM = "medium"      # Partially demonstrated mandatory requirement OR missing preferred requirement
    LOW = "low"            # Partially demonstrated preferred requirement


class RoadmapStep(BaseModel):
    """A concrete, actionable learning milestone in the personalized improvement roadmap."""
    step_number: int = Field(..., description="1-indexed sequence order in the learning trajectory")
    skill_name: str = Field(..., description="Canonical name of the skill to learn or improve")
    category: str = Field(..., description="Technical domain category")
    priority: RoadmapPriority = Field(..., description="Critical, High, Medium, or Low priority")
    is_prerequisite_for: Optional[str] = Field(None, description="The higher-level target job requirement this unlocks")
    why_it_matters: str = Field(..., description="Specific explanation connecting this skill to the target job requirements")
    current_evidence: Optional[str] = Field(None, description="What the candidate's resume currently shows (or 'No evidence')")
    learning_topics: List[str] = Field(default_factory=list, description="Core conceptual topics to master")
    practical_project: str = Field(..., description="Specific portfolio project to implement")
    expected_deliverable: str = Field(..., description="Concrete artifact to produce (code, tests, deployments)")
    estimated_hours: int = Field(..., description="Suggested study & implementation hours")


class RoadmapSummary(BaseModel):
    """Executive metrics for the generated improvement roadmap."""
    total_steps: int = Field(..., description="Total sequential milestones in roadmap")
    critical_steps_count: int = Field(..., description="Number of critical priority gaps")
    high_steps_count: int = Field(..., description="Number of high priority gaps")
    medium_steps_count: int = Field(..., description="Number of medium priority gaps")
    low_steps_count: int = Field(..., description="Number of low priority gaps")
    total_estimated_hours: int = Field(..., description="Total hours across all recommended projects")


class RoadmapRequest(BaseModel):
    """Input payload accepting parsed resume and job description (or existing gap analysis)."""
    resume: ParsedResume = Field(..., description="Parsed resume output from Milestone 2")
    job_description: ParsedJobDescription = Field(..., description="Parsed job description output from Milestone 2")


class RoadmapResponse(BaseModel):
    """Complete personalized improvement roadmap response."""
    summary: RoadmapSummary = Field(..., description="Overview metrics and hour estimates")
    roadmap: List[RoadmapStep] = Field(..., description="Sequenced, dependency-ordered improvement steps")
    gap_summary: str = Field(..., description="Concise assessment of the candidate's qualification gaps")
