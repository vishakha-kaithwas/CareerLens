from typing import List, Optional
from pydantic import BaseModel, Field


class JobDescriptionInput(BaseModel):
    """Input payload for pasting a raw job description."""
    text: str = Field(..., min_length=20, description="Raw job description text")


class ParsedJobDescription(BaseModel):
    """Structured representation of parsed job description."""
    title: Optional[str] = Field(None, description="Inferred or extracted job title")
    required_skills: List[str] = Field(default_factory=list, description="Must-have or required technical and domain skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have or preferred skills")
    tools_and_technologies: List[str] = Field(default_factory=list, description="Frameworks, libraries, and tools mentioned")
    soft_skills: List[str] = Field(default_factory=list, description="Interpersonal and professional soft skills")
    experience_requirements: List[str] = Field(default_factory=list, description="Years of experience and seniority criteria")
    education_requirements: List[str] = Field(default_factory=list, description="Degrees and educational qualifications required")
    responsibilities: List[str] = Field(default_factory=list, description="Key duties and day-to-day responsibilities")
    raw_text: str = Field(..., description="Original raw job description text preserved for verification")
