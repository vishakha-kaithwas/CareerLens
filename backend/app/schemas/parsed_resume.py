from typing import List, Optional
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    """Personal contact information extracted from resume header."""
    name: Optional[str] = Field(None, description="Full name of candidate")
    email: Optional[str] = Field(None, description="Primary email address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    location: Optional[str] = Field(None, description="City, State, or Country")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL or handle")
    github: Optional[str] = Field(None, description="GitHub profile URL or handle")
    portfolio: Optional[str] = Field(None, description="Personal website or portfolio URL")


class EducationEntry(BaseModel):
    """Structured education credential."""
    institution: Optional[str] = Field(None, description="College, University, or Institution")
    degree: Optional[str] = Field(None, description="Degree type (e.g. B.S., M.S., Ph.D.)")
    field_of_study: Optional[str] = Field(None, description="Major, discipline, or field of study")
    dates: Optional[str] = Field(None, description="Timeframe or graduation date")
    raw_text: str = Field(..., description="Original raw snippet for evidence verification")


class ExperienceEntry(BaseModel):
    """Structured employment or internship experience entry."""
    title: Optional[str] = Field(None, description="Job title / role")
    company: Optional[str] = Field(None, description="Organization or employer name")
    dates: Optional[str] = Field(None, description="Employment timeframe")
    responsibilities: List[str] = Field(default_factory=list, description="Bullet points or key tasks")
    raw_text: str = Field(..., description="Original raw snippet for evidence verification")


class ProjectEntry(BaseModel):
    """Structured project entry."""
    title: Optional[str] = Field(None, description="Project title or name")
    description: Optional[str] = Field(None, description="Summary or bullet details of the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies or tools mentioned")
    raw_text: str = Field(..., description="Original raw snippet for evidence verification")


class CertificationEntry(BaseModel):
    """Structured certification or credential entry."""
    name: str = Field(..., description="Certification title")
    issuer: Optional[str] = Field(None, description="Issuing organization or authority")
    raw_text: str = Field(..., description="Original raw snippet for evidence verification")


class ExtracurricularEntry(BaseModel):
    """Structured extracurricular activity, leadership, volunteering, or hackathon entry."""
    title: str = Field(..., description="Activity, club, competition, or leadership title")
    role_or_organization: Optional[str] = Field(None, description="Role, organization, or chapter")
    description: Optional[str] = Field(None, description="Details or achievements")
    raw_text: str = Field(..., description="Original raw snippet for evidence verification")


class ParsedResume(BaseModel):
    """Structured representation of parsed resume sections and entities."""
    contact: ContactInfo = Field(default_factory=ContactInfo, description="Contact details")
    summary: Optional[str] = Field(None, description="Professional summary or objective")
    skills: List[str] = Field(default_factory=list, description="Normalized technical and domain skills")
    experience: List[ExperienceEntry] = Field(default_factory=list, description="Work experience entries")
    education: List[EducationEntry] = Field(default_factory=list, description="Education records")
    projects: List[ProjectEntry] = Field(default_factory=list, description="Projects portfolio entries")
    certifications: List[CertificationEntry] = Field(default_factory=list, description="Certifications and licenses")
    extracurriculars: List[ExtracurricularEntry] = Field(default_factory=list, description="Extracurricular activities, clubs, leadership, hackathons")
    raw_text: str = Field(..., description="Complete original extracted text preserved for verification")
