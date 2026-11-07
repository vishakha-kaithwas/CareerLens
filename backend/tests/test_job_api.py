"""
API integration tests for:
1. POST /api/v1/resumes/parse (upload PDF and parse structured resume)
2. POST /api/v1/jobs/parse (paste job description text and parse structured requirements)
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_parse_resume_endpoint(async_client: AsyncClient, sample_valid_resume_pdf):
    files = {"file": ("john_doe_resume.pdf", sample_valid_resume_pdf, "application/pdf")}
    response = await async_client.post("/api/v1/resumes/parse", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    # Contact
    assert data["contact"]["name"] == "John Doe"
    assert data["contact"]["email"] == "john.doe@example.com"

    # Skills
    skills = data["skills"]
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills

    # Experience
    assert len(data["experience"]) >= 1

    # Raw text preserved
    assert len(data["raw_text"]) > 100


@pytest.mark.asyncio
async def test_api_parse_job_description_endpoint(async_client: AsyncClient):
    jd_payload = {
        "text": """
        Position: Senior Machine Learning Engineer

        Responsibilities:
        - Develop and deploy predictive ML pipelines in production.
        - Collaborate with backend engineers on RESTful APIs.

        Requirements:
        - 4+ years of hands-on experience in Python and PyTorch.
        - Experience with Docker, SQL, and Git.
        - Master's degree in Data Science, Computer Science or equivalent.

        Bonus Points:
        - Hands-on experience with FastAPI and Redis.
        - Familiarity with Kubernetes and AWS.
        """
    }

    response = await async_client.post("/api/v1/jobs/parse", json=jd_payload)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["title"] == "Senior Machine Learning Engineer"
    assert "Python" in data["required_skills"]
    assert "PyTorch" in data["required_skills"]
    assert "Docker" in data["required_skills"]

    # Bonus points separated into preferred_skills
    assert "FastAPI" in data["preferred_skills"]
    assert "Redis" in data["preferred_skills"]

    # Experience and Education criteria
    assert len(data["experience_requirements"]) >= 1
    assert any("4" in e for e in data["experience_requirements"])
    assert len(data["education_requirements"]) >= 1
    assert any("Master" in edu for edu in data["education_requirements"])

    # Raw text preserved
    assert data["raw_text"] == jd_payload["text"]


@pytest.mark.asyncio
async def test_api_parse_job_description_rejects_empty_or_short(async_client: AsyncClient):
    # Minimum length is 20 chars
    short_payload = {"text": "Too short"}
    response = await async_client.post("/api/v1/jobs/parse", json=short_payload)

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
