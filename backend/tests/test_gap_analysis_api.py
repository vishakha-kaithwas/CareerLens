"""
API integration tests for POST /api/v1/analysis/gaps.
"""

import pytest
from httpx import AsyncClient
from app.api.v1.routes.analysis import gap_analyzer_service
from tests.test_skill_matcher import MockEmbeddingEngine


@pytest.fixture(autouse=True)
def mock_analyzer_embeddings(monkeypatch):
    """Overrides the analyzer's skill matcher embedding engine with deterministic MockEmbeddingEngine."""
    mock_engine = MockEmbeddingEngine()
    monkeypatch.setattr(gap_analyzer_service.skill_matcher, "embedding_engine", mock_engine)


@pytest.mark.asyncio
async def test_api_gap_analysis_endpoint(async_client: AsyncClient):
    payload = {
        "resume": {
            "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
            "experience": [
                {
                    "title": "Backend Software Engineer",
                    "company": "Tech Corp",
                    "responsibilities": [
                        "Architected microservices in Python and FastAPI.",
                        "Containerized applications using Docker.",
                    ],
                    "raw_text": "Backend Software Engineer at Tech Corp",
                }
            ],
            "raw_text": "Complete candidate resume text",
        },
        "job_description": {
            "required_skills": ["Python", "Kubernetes"],
            "preferred_skills": ["Docker", "AWS"],
            "raw_text": "Looking for Python and Kubernetes engineers. Bonus: Docker and AWS.",
        },
    }

    response = await async_client.post("/api/v1/analysis/gaps", json=payload)

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True

    data = res_json["data"]
    # Check that classifications exist
    assert "results" in data
    assert "matched_requirements" in data
    assert "partially_demonstrated_requirements" in data
    assert "not_demonstrated_requirements" in data

    # Check coverage objects
    req_cov = data["required_coverage"]
    pref_cov = data["preferred_coverage"]
    overall_cov = data["overall_coverage"]

    assert req_cov["total_count"] == 2
    assert pref_cov["total_count"] == 2
    assert req_cov["coverage_score"] is not None
    assert pref_cov["coverage_score"] is not None
    assert overall_cov["overall_score"] is not None
    assert "NOT a hiring probability" in overall_cov["disclaimer"]


@pytest.mark.asyncio
async def test_api_gap_analysis_validation_error(async_client: AsyncClient):
    invalid_payload = {
        "resume": {"skills": ["Python"]}
        # Missing 'job_description'
    }

    response = await async_client.post("/api/v1/analysis/gaps", json=invalid_payload)
    assert response.status_code == 422
    res_json = response.json()
    assert res_json["success"] is False
