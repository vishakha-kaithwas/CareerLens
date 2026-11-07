"""
API integration tests for POST /api/v1/resume/improve endpoint.
"""

import pytest
from httpx import AsyncClient
from app.api.v1.routes.improvement import resume_improver_service
from app.schemas.job import ParsedJobDescription
from app.schemas.parsed_resume import (
    ContactInfo,
    ExperienceEntry,
    ParsedResume,
    ProjectEntry,
)
from tests.test_skill_matcher import MockEmbeddingEngine


@pytest.fixture(autouse=True)
def mock_improvement_embeddings(monkeypatch):
    """Overrides the improver's gap analyzer embedding engine with MockEmbeddingEngine."""
    mock_engine = MockEmbeddingEngine()
    monkeypatch.setattr(
        resume_improver_service.gap_analyzer.skill_matcher,
        "embedding_engine",
        mock_engine,
    )


@pytest.fixture
def sample_parsed_resume():
    return ParsedResume(
        contact=ContactInfo(name="Morgan Riley", email="morgan@example.com"),
        summary="Software developer passionate about backend systems.",
        skills=["Python", "FastAPI", "SQL"],
        experience=[
            ExperienceEntry(
                title="Software Engineer",
                company="DataFlow Inc",
                responsibilities=[
                    "Worked on REST APIs using FastAPI and PostgreSQL",
                    "Helped with optimizing database queries",
                ],
                raw_text="Software Engineer at DataFlow Inc\nWorked on REST APIs using FastAPI and PostgreSQL",
            )
        ],
        education=[],
        projects=[
            ProjectEntry(
                title="Cloud Deployer",
                description="Built automated deployment pipelines with Docker and GitHub Actions.",
                technologies=["Docker", "CI/CD"],
                raw_text="Cloud Deployer: Built automated deployment pipelines with Docker.",
            )
        ],
        certifications=[],
        raw_text="Morgan Riley resume text",
    )


@pytest.fixture
def sample_parsed_job():
    return ParsedJobDescription(
        title="Backend Software Engineer",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        preferred_skills=["Kubernetes", "Redis"],
        tools_and_technologies=["FastAPI", "PostgreSQL", "Docker"],
        soft_skills=["Collaboration"],
        experience_requirements=["2+ years backend engineering"],
        education_requirements=["B.S. Computer Science"],
        responsibilities=["Develop robust backend microservices"],
        raw_text="Backend Software Engineer job description text",
    )


@pytest.mark.asyncio
async def test_api_resume_improvement_endpoint(async_client: AsyncClient, sample_parsed_resume, sample_parsed_job):
    """Verifies HTTP 200 response and JSON contract for POST /api/v1/resume/improve."""
    payload = {
        "resume": sample_parsed_resume.model_dump(),
        "job_description": sample_parsed_job.model_dump(),
    }

    response = await async_client.post("/api/v1/resume/improve", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data

    report = data["data"]
    assert "summary" in report
    assert "bullet_improvements" in report
    assert "section_recommendations" in report
    assert "job_relevance" in report
    assert "candidate_questions" in report

    # Verify summary counts
    assert report["summary"]["total_bullet_improvements"] > 0
    assert report["summary"]["high_confidence_improvements"] > 0

    # Verify that bullet improvements contain evidence and reasons
    bullet = report["bullet_improvements"][0]
    assert "original_text" in bullet
    assert "suggested_text" in bullet
    assert "why_useful" in bullet
    assert len(bullet["evidence"]) > 0

    # Verify that candidate questions are populated
    assert len(report["candidate_questions"]) > 0


@pytest.mark.asyncio
async def test_api_resume_improvement_validation_error(async_client: AsyncClient):
    """Verifies HTTP 422 when required schema fields are missing."""
    response = await async_client.post("/api/v1/resume/improve", json={})
    assert response.status_code == 422
