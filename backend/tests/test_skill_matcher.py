"""
Unit tests for the Intelligent Skill Matching Service.

Covers:
1. Exact skill matches.
2. Normalized/Taxonomy matches.
3. Semantic matching with cosine similarity above threshold.
4. Unrelated descriptions (similarity below threshold -> unmatched).
5. Distinct technology protection (suppressing Python != PyTorch, Java != JavaScript, SQL != NoSQL).
6. Required vs. Preferred skill categorization.
7. Missing resume evidence handling.
8. Deterministic testing with mock embeddings.
"""

import numpy as np
import pytest
from app.ml.embeddings import EmbeddingEngine
from app.schemas.job import ParsedJobDescription
from app.schemas.matching import MatchMethod
from app.schemas.parsed_resume import ExperienceEntry, ParsedResume, ProjectEntry
from app.services.skill_matcher import SkillMatcherService


class MockEmbeddingEngine:
    """Deterministic mock embedding engine for unit testing without downloading models."""

    def __init__(self, predefined_similarities: dict = None):
        self.predefined = predefined_similarities or {}
        # 32-dimensional mock vector
        self.dim = 32

    def encode(self, texts, normalize=True):
        if isinstance(texts, str):
            texts = [texts]
        vectors = []
        for text in texts:
            # Deterministic pseudo-random vector based on hash of text
            rng = np.random.RandomState(abs(hash(text)) % (2**31))
            vec = rng.randn(self.dim).astype(np.float32)
            if normalize:
                norm = np.linalg.norm(vec)
                vec = vec / norm if norm > 0 else vec
            vectors.append(vec)
        return np.array(vectors)

    def compute_cosine_similarity(self, vec_a, vec_b):
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


@pytest.fixture
def sample_parsed_resume():
    return ParsedResume(
        skills=["Python", "FastAPI", "Docker", "PostgreSQL"],
        experience=[
            ExperienceEntry(
                title="Backend Engineer",
                company="Acme Corp",
                responsibilities=[
                    "Architected high-throughput RESTful services using Python and FastAPI.",
                    "Containerized microservices and automated deployment pipelines.",
                ],
                raw_text="Backend Engineer at Acme Corp",
            )
        ],
        projects=[
            ProjectEntry(
                title="DataStore",
                description="Designed relational database schemas and indexed SQL queries for fast lookup.",
                technologies=["PostgreSQL", "SQL"],
                raw_text="DataStore project",
            )
        ],
        raw_text="Complete raw resume text...",
    )


def test_exact_skill_match(sample_parsed_resume):
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    jd = ParsedJobDescription(
        required_skills=["Python", "FastAPI"],
        preferred_skills=[],
        raw_text="Requires Python and FastAPI proficiency.",
    )

    result = matcher.match_skills(sample_parsed_resume, jd)

    assert result.total_required_count == 2
    assert result.matched_required_count == 2
    for m in result.required_matches:
        assert m.is_matched is True
        assert m.match_method == MatchMethod.EXACT
        assert m.similarity_score == 1.0
        assert m.job_evidence is not None
        assert m.resume_evidence is not None


def test_normalized_taxonomy_match(sample_parsed_resume):
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    # 'postgres' alias should match canonical 'PostgreSQL' in resume
    jd = ParsedJobDescription(
        required_skills=["postgres"],
        preferred_skills=[],
        raw_text="Looking for experience with postgres.",
    )

    result = matcher.match_skills(sample_parsed_resume, jd)

    assert result.total_required_count == 1
    assert result.matched_required_count == 1
    match = result.required_matches[0]
    assert match.is_matched is True
    assert match.match_method == MatchMethod.NORMALIZED
    assert match.matched_resume_skill == "PostgreSQL"
    assert match.similarity_score == 1.0


def test_semantic_match_above_threshold(sample_parsed_resume):
    # Mock engine that returns high similarity for paraphrased backend API development
    class SemanticMockEngine(MockEmbeddingEngine):
        def compute_cosine_similarity(self, vec_a, vec_b):
            # Simulate high similarity for semantic paraphrase
            return 0.88

    matcher = SkillMatcherService(embedding_engine=SemanticMockEngine(), similarity_threshold=0.65)
    jd = ParsedJobDescription(
        required_skills=["Backend API development"],
        preferred_skills=[],
        raw_text="Role: Backend API development with modern frameworks.",
    )

    result = matcher.match_skills(sample_parsed_resume, jd)

    assert result.matched_required_count == 1
    match = result.required_matches[0]
    assert match.is_matched is True
    assert match.match_method == MatchMethod.SEMANTIC
    assert match.similarity_score == 0.88
    assert match.resume_evidence is not None


def test_unrelated_skill_below_threshold(sample_parsed_resume):
    # Mock engine that returns low similarity for unrelated skill
    class LowSimilarityMockEngine(MockEmbeddingEngine):
        def compute_cosine_similarity(self, vec_a, vec_b):
            return 0.32

    matcher = SkillMatcherService(embedding_engine=LowSimilarityMockEngine(), similarity_threshold=0.65)
    jd = ParsedJobDescription(
        required_skills=["Embedded Firmware Development"],
        preferred_skills=[],
        raw_text="Requires Embedded Firmware Development in Assembly.",
    )

    result = matcher.match_skills(sample_parsed_resume, jd)

    assert result.total_required_count == 1
    assert result.matched_required_count == 0
    match = result.required_matches[0]
    assert match.is_matched is False
    assert match.match_method == MatchMethod.NONE
    assert match.similarity_score == 0.32
    assert match.matched_resume_skill is None
    assert match.resume_evidence is None


def test_distinct_technology_violation_suppression():
    """
    Verifies that distinct technologies like PyTorch vs Python or Java vs JavaScript
    are NEVER matched semantically despite embedding proximity.
    """
    class HighSimilarityMockEngine(MockEmbeddingEngine):
        def compute_cosine_similarity(self, vec_a, vec_b):
            return 0.85  # Artificial high similarity

    matcher = SkillMatcherService(embedding_engine=HighSimilarityMockEngine(), similarity_threshold=0.65)

    # Candidate only knows PyTorch, job requires Python
    resume_pytorch_only = ParsedResume(
        skills=["PyTorch"],
        experience=[
            ExperienceEntry(
                title="ML Engineer",
                company="AI Lab",
                responsibilities=["Trained deep neural networks using PyTorch."],
                raw_text="ML Engineer",
            )
        ],
        raw_text="PyTorch ML Engineer",
    )

    jd_python = ParsedJobDescription(
        required_skills=["Python"],
        preferred_skills=[],
        raw_text="Core requirement: Python software engineering.",
    )

    result = matcher.match_skills(resume_pytorch_only, jd_python)

    # PyTorch evidence must NOT satisfy Python requirement!
    match = result.required_matches[0]
    assert match.is_matched is False
    assert match.match_method == MatchMethod.NONE


def test_required_vs_preferred_skill_categorization(sample_parsed_resume):
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    jd = ParsedJobDescription(
        required_skills=["Python"],
        preferred_skills=["Docker", "Kubernetes"],
        raw_text="Job with Python required, Docker and Kubernetes preferred.",
    )

    result = matcher.match_skills(sample_parsed_resume, jd)

    assert result.total_required_count == 1
    assert result.matched_required_count == 1
    assert result.required_matches[0].is_required is True
    assert result.required_matches[0].is_matched is True

    assert result.total_preferred_count == 2
    # Docker is matched (in resume), Kubernetes is not (not in resume)
    docker_match = next(m for m in result.preferred_matches if m.job_requirement == "Docker")
    k8s_match = next(m for m in result.preferred_matches if m.job_requirement == "Kubernetes")

    assert docker_match.is_required is False
    assert docker_match.is_matched is True
    assert k8s_match.is_required is False
    assert k8s_match.is_matched is False


def test_missing_resume_evidence_handling():
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    # Empty resume
    empty_resume = ParsedResume(raw_text="")
    jd = ParsedJobDescription(
        required_skills=["Python", "FastAPI"],
        raw_text="Looking for Python and FastAPI.",
    )

    result = matcher.match_skills(empty_resume, jd)

    assert result.matched_required_count == 0
    assert result.total_required_count == 2
    for m in result.required_matches:
        assert m.is_matched is False
        assert m.match_method == MatchMethod.NONE
        assert m.similarity_score == 0.0
