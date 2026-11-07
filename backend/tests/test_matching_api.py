"""
API integration tests for POST /api/v1/matching/skills.
"""

import pytest
from httpx import AsyncClient
from app.api.v1.routes.matching import skill_matcher_service
from tests.test_skill_matcher import MockEmbeddingEngine


@pytest.fixture(autouse=True)
def mock_matcher_embeddings(monkeypatch):
    """Overrides the global embedding engine with MockEmbeddingEngine for fast, isolated API tests."""
    mock_engine = MockEmbeddingEngine()
    monkeypatch.setattr(skill_matcher_service, "embedding_engine", mock_engine)


@pytest.mark.asyncio
async def test_api_matching_skills_endpoint(async_client: AsyncClient):
    payload = {
        "resume": {
            "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
            "experience": [
                {
                    "title": "Backend Software Engineer",
                    "company": "Tech Innovations",
                    "responsibilities": [
                        "Architected scalable RESTful microservices in Python.",
                        "Optimized PostgreSQL database performance.",
                    ],
                    "raw_text": "Backend Software Engineer at Tech Innovations",
                }
            ],
            "raw_text": "Sample resume text",
        },
        "job_description": {
            "required_skills": ["Python", "Docker"],
            "preferred_skills": ["Kubernetes", "AWS"],
            "raw_text": "Looking for Python and Docker experts. Bonus: Kubernetes and AWS.",
        },
    }

    response = await async_client.post("/api/v1/matching/skills", json=payload)

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]

    assert data["total_required_count"] == 2
    assert data["matched_required_count"] == 2
    assert data["total_preferred_count"] == 2
    assert data["matched_preferred_count"] == 0

    req_matches = data["required_matches"]
    assert any(m["job_requirement"] == "Python" and m["is_matched"] is True for m in req_matches)
    assert any(m["job_requirement"] == "Docker" and m["is_matched"] is True for m in req_matches)


@pytest.mark.asyncio
async def test_api_matching_skills_validation_error(async_client: AsyncClient):
    # Missing required 'job_description' key
    invalid_payload = {
        "resume": {
            "skills": ["Python"],
            "raw_text": "Some text",
        }
    }

    response = await async_client.post("/api/v1/matching/skills", json=invalid_payload)
    assert response.status_code == 422
    res_json = response.json()
    assert res_json["success"] is False
