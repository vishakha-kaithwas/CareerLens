"""
API integration tests for POST /api/v1/roadmap/generate.
"""

import pytest
from httpx import AsyncClient
from app.api.v1.routes.roadmap import roadmap_generator_service
from tests.test_skill_matcher import MockEmbeddingEngine


@pytest.fixture(autouse=True)
def mock_roadmap_embeddings(monkeypatch):
    """Overrides the roadmap generator's gap analyzer embedding engine with MockEmbeddingEngine."""
    mock_engine = MockEmbeddingEngine()
    monkeypatch.setattr(
        roadmap_generator_service.gap_analyzer.skill_matcher,
        "embedding_engine",
        mock_engine,
    )


@pytest.mark.asyncio
async def test_api_generate_roadmap_endpoint(async_client: AsyncClient):
    payload = {
        "resume": {
            "skills": ["Python"],
            "experience": [
                {
                    "title": "Junior Python Developer",
                    "company": "StartUp",
                    "responsibilities": ["Wrote backend scripts in Python."],
                    "raw_text": "Junior Python Developer at StartUp",
                }
            ],
            "raw_text": "Junior Python Developer resume text",
        },
        "job_description": {
            "required_skills": ["Kubernetes"],
            "preferred_skills": ["Redis"],
            "raw_text": "Looking for Kubernetes and Redis skills.",
        },
    }

    response = await async_client.post("/api/v1/roadmap/generate", json=payload)

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True

    data = res_json["data"]
    assert "summary" in data
    assert "roadmap" in data
    assert "gap_summary" in data

    summary = data["summary"]
    assert summary["total_steps"] >= 2
    assert summary["total_estimated_hours"] > 0

    roadmap = data["roadmap"]
    # Check that steps are sequenced 1..N
    for i, step in enumerate(roadmap, 1):
        assert step["step_number"] == i
        assert step["skill_name"] is not None
        assert step["practical_project"] is not None
        assert step["expected_deliverable"] is not None


@pytest.mark.asyncio
async def test_api_generate_roadmap_validation_error(async_client: AsyncClient):
    invalid_payload = {
        "resume": {"skills": ["Python"]}
        # Missing 'job_description'
    }

    response = await async_client.post("/api/v1/roadmap/generate", json=invalid_payload)
    assert response.status_code == 422
    res_json = response.json()
    assert res_json["success"] is False
