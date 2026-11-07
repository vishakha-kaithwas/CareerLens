"""
Unit tests for the Career Gap Analyzer Service (Milestone 4).

Covers:
1. Clearly matched requirements (exact/normalized with contextual evidence).
2. Partially demonstrated requirements (keyword listed without context, or semantic match).
3. Requirements with no resume evidence (not demonstrated).
4. Semantic similarity alone without direct proficiency evidence -> partially demonstrated.
5. Required and preferred coverage calculations.
6. Overall weighted score (80% req + 20% pref).
7. Scoring when no preferred requirements exist (100% req).
8. Scoring when empty requirement lists are provided (handles null without ZeroDivisionError).
9. Missing evidence and explanation generation.
"""

import pytest
from app.schemas.gap_analysis import RequirementClassification, RequirementType
from app.schemas.job import ParsedJobDescription
from app.schemas.matching import MatchMethod
from app.schemas.parsed_resume import ExperienceEntry, ParsedResume, ProjectEntry
from app.services.gap_analyzer import GapAnalyzerService
from app.services.skill_matcher import SkillMatcherService
from tests.test_skill_matcher import MockEmbeddingEngine


@pytest.fixture
def sample_resume():
    return ParsedResume(
        skills=["Python", "PostgreSQL", "Docker", "Redis"],
        experience=[
            ExperienceEntry(
                title="Senior Backend Engineer",
                company="DataCorp",
                responsibilities=[
                    "Engineered distributed REST APIs handling 50M requests using Python and FastAPI.",
                    "Optimized PostgreSQL queries, decreasing p99 latency by 40%.",
                ],
                raw_text="Senior Backend Engineer at DataCorp",
            )
        ],
        projects=[
            ProjectEntry(
                title="Container Cloud",
                description="Containerized multi-tier applications using Docker and orchestrated builds.",
                technologies=["Docker"],
                raw_text="Container Cloud project",
            )
        ],
        raw_text="Full resume text",
    )


def test_clearly_matched_requirements(sample_resume):
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)

    # Python has rich contextual experience at DataCorp
    jd = ParsedJobDescription(
        required_skills=["Python"],
        preferred_skills=[],
        raw_text="Requires Python.",
    )

    result = analyzer.analyze_gaps(sample_resume, jd)

    assert len(result.matched_requirements) == 1
    match = result.matched_requirements[0]
    assert match.requirement == "Python"
    assert match.classification == RequirementClassification.MATCHED
    assert match.match_method == MatchMethod.EXACT
    assert "DataCorp" in (match.resume_evidence or "")


def test_partially_demonstrated_keyword_only(sample_resume):
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)

    # Redis is in skills list, but not mentioned in experience bullets or project descriptions
    jd = ParsedJobDescription(
        required_skills=["Redis"],
        preferred_skills=[],
        raw_text="Requires Redis.",
    )

    result = analyzer.analyze_gaps(sample_resume, jd)

    assert len(result.partially_demonstrated_requirements) == 1
    match = result.partially_demonstrated_requirements[0]
    assert match.requirement == "Redis"
    assert match.classification == RequirementClassification.PARTIALLY_DEMONSTRATED
    assert "explicitly listed on the resume, but lacks contextual bullet points" in match.explanation


def test_partially_demonstrated_semantic_match(sample_resume):
    class SemanticMockEngine(MockEmbeddingEngine):
        def compute_cosine_similarity(self, vec_a, vec_b):
            return 0.82

    matcher = SkillMatcherService(embedding_engine=SemanticMockEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)

    # "Backend API Development" semantically relates to FastAPI/REST API bullets
    jd = ParsedJobDescription(
        required_skills=["Backend API Development"],
        preferred_skills=[],
        raw_text="Job requires Backend API Development.",
    )

    result = analyzer.analyze_gaps(sample_resume, jd)

    assert len(result.partially_demonstrated_requirements) == 1
    match = result.partially_demonstrated_requirements[0]
    assert match.classification == RequirementClassification.PARTIALLY_DEMONSTRATED
    assert match.match_method == MatchMethod.SEMANTIC
    assert "does not directly verify full proficiency" in match.explanation


def test_not_demonstrated_requirement(sample_resume):
    class LowSimEngine(MockEmbeddingEngine):
        def compute_cosine_similarity(self, vec_a, vec_b):
            return 0.20

    matcher = SkillMatcherService(embedding_engine=LowSimEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)

    jd = ParsedJobDescription(
        required_skills=["Rust"],
        preferred_skills=[],
        raw_text="Requires Rust systems programming.",
    )

    result = analyzer.analyze_gaps(sample_resume, jd)

    assert len(result.not_demonstrated_requirements) == 1
    not_dem = result.not_demonstrated_requirements[0]
    assert not_dem.requirement == "Rust"
    assert not_dem.classification == RequirementClassification.NOT_DEMONSTRATED
    assert not_dem.resume_evidence is None
    assert "does not provide identifiable evidence" in not_dem.explanation


def test_coverage_score_calculation(sample_resume):
    """
    Evaluates:
    - 2 required: 1 Matched (Python), 1 Not Demonstrated (Rust) -> (1.0 + 0.0)/2 = 50.0%
    - 2 preferred: 1 Partially Demonstrated (Redis), 1 Not Demonstrated (Kubernetes) -> (0.5 + 0.0)/2 = 25.0%
    - Overall: (50.0 * 0.8) + (25.0 * 0.2) = 40.0 + 5.0 = 45.0%
    """
    class TargetEngine(MockEmbeddingEngine):
        def compute_cosine_similarity(self, vec_a, vec_b):
            return 0.25

    matcher = SkillMatcherService(embedding_engine=TargetEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)

    jd = ParsedJobDescription(
        required_skills=["Python", "Rust"],
        preferred_skills=["Redis", "Kubernetes"],
        raw_text="Python and Rust required. Redis and Kubernetes preferred.",
    )

    result = analyzer.analyze_gaps(sample_resume, jd)

    # Required coverage
    assert result.required_coverage.total_count == 2
    assert result.required_coverage.matched_count == 1
    assert result.required_coverage.not_demonstrated_count == 1
    assert result.required_coverage.coverage_score == 50.0

    # Preferred coverage
    assert result.preferred_coverage.total_count == 2
    assert result.preferred_coverage.partial_count == 1
    assert result.preferred_coverage.not_demonstrated_count == 1
    assert result.preferred_coverage.coverage_score == 25.0

    # Overall coverage
    assert result.overall_coverage.overall_score == 45.0
    assert result.overall_coverage.required_weight_percent == 80.0
    assert result.overall_coverage.preferred_weight_percent == 20.0


def test_coverage_score_when_no_preferred_requirements(sample_resume):
    """When no preferred criteria exist, required score represents 100% of the overall score."""
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)

    jd = ParsedJobDescription(
        required_skills=["Python", "Docker"],
        preferred_skills=[],
        raw_text="Python and Docker required.",
    )

    result = analyzer.analyze_gaps(sample_resume, jd)

    assert result.required_coverage.coverage_score == 100.0
    assert result.preferred_coverage.coverage_score is None
    assert result.overall_coverage.overall_score == 100.0
    assert result.overall_coverage.required_weight_percent == 100.0
    assert result.overall_coverage.preferred_weight_percent == 0.0


def test_empty_requirements_handling(sample_resume):
    """When JD provides 0 skills, handles gracefully without ZeroDivisionError."""
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)

    jd = ParsedJobDescription(required_skills=[], preferred_skills=[], raw_text="General description.")

    result = analyzer.analyze_gaps(sample_resume, jd)

    assert result.required_coverage.coverage_score is None
    assert result.preferred_coverage.coverage_score is None
    assert result.overall_coverage.overall_score is None
    assert "No required or preferred skills were identified" in result.overall_coverage.explanation
