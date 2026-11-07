"""
Unit tests for Skill Dependency Intelligence and Personalized Improvement Roadmap (Milestone 5).

Covers:
1. Directed acyclic graph construction and cycle detection.
2. Unmet prerequisite resolution (e.g. Docker requires Linux; Kubernetes requires Docker & Linux).
3. Topological sorting of learning progressions.
4. Recommendation ordering: prerequisites precede dependent skills.
5. Priority assignment: Critical for missing required with unmet prereqs, High for missing required, Medium/Low for partial.
6. Filtering out skills already strongly demonstrated by the candidate.
7. Project and deliverable recommendations.
"""

import pytest
from app.ml.dependency_graph import SkillDependencyGraph
from app.schemas.gap_analysis import RequirementClassification, RequirementType
from app.schemas.job import ParsedJobDescription
from app.schemas.parsed_resume import ExperienceEntry, ParsedResume, ProjectEntry
from app.schemas.roadmap import RoadmapPriority
from app.services.gap_analyzer import GapAnalyzerService
from app.services.roadmap_generator import RoadmapGeneratorService
from app.services.skill_matcher import SkillMatcherService
from tests.test_skill_matcher import MockEmbeddingEngine


def test_dependency_graph_cycle_detection():
    graph = SkillDependencyGraph()
    has_cycle, path = graph.detect_cycle()
    assert has_cycle is False, f"Cycle detected in curated knowledge base: {path}"


def test_unmet_prerequisites_calculation():
    graph = SkillDependencyGraph()

    # Candidate knows nothing: Kubernetes requires [Linux, Docker]
    prereqs = graph.get_unmet_prerequisites("Kubernetes", demonstrated_skills=set())
    assert "Linux" in prereqs
    assert "Docker" in prereqs
    # Linux should come before Docker in order of foundation
    assert prereqs.index("Linux") < prereqs.index("Docker")

    # If candidate already demonstrates Linux and Docker, unmet prereqs should be empty
    prereqs_met = graph.get_unmet_prerequisites("Kubernetes", demonstrated_skills={"linux", "docker"})
    assert prereqs_met == []


def test_topological_sort_learning_order():
    graph = SkillDependencyGraph()
    # Unordered collection of skills
    shuffled = ["Kubernetes", "Linux", "FastAPI", "Python", "Docker", "RESTful APIs"]
    ordered = graph.get_topological_sort(shuffled)

    # Validate that prerequisites appear before their dependents
    assert ordered.index("Linux") < ordered.index("Docker")
    assert ordered.index("Docker") < ordered.index("Kubernetes")
    assert ordered.index("Python") < ordered.index("RESTful APIs")
    assert ordered.index("RESTful APIs") < ordered.index("FastAPI")


def test_roadmap_recommends_unmet_prerequisites_with_critical_priority():
    """
    Candidate knows Python, lacks Linux and Docker.
    Job requires Kubernetes.
    The roadmap must recommend:
    1. Linux (Prerequisite for Docker/Kubernetes)
    2. Docker (Prerequisite for Kubernetes)
    3. Kubernetes (Target job requirement)
    """
    class TargetEngine(MockEmbeddingEngine):
        def compute_cosine_similarity(self, vec_a, vec_b):
            return 0.20

    matcher = SkillMatcherService(embedding_engine=TargetEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)
    generator = RoadmapGeneratorService(gap_analyzer=analyzer)

    resume_python_only = ParsedResume(
        skills=["Python"],
        experience=[
            ExperienceEntry(
                title="Python Developer",
                company="Startup",
                responsibilities=["Wrote Python data scripts."],
                raw_text="Python Developer at Startup",
            )
        ],
        raw_text="Python Developer",
    )

    jd_kubernetes = ParsedJobDescription(
        required_skills=["Kubernetes"],
        preferred_skills=[],
        raw_text="Required: Kubernetes orchestration.",
    )

    response = generator.generate_roadmap(resume_python_only, jd_kubernetes)

    assert response.summary.total_steps >= 2
    step_names = [s.skill_name for s in response.roadmap]

    assert "Docker" in step_names
    assert "Kubernetes" in step_names
    # Prerequisites must precede target
    assert step_names.index("Docker") < step_names.index("Kubernetes")

    # Kubernetes is missing required with unmet prereqs -> CRITICAL
    k8s_step = next(s for s in response.roadmap if s.skill_name == "Kubernetes")
    assert k8s_step.priority == RoadmapPriority.CRITICAL
    assert k8s_step.practical_project is not None
    assert k8s_step.expected_deliverable is not None


def test_roadmap_skips_already_demonstrated_skills():
    """If candidate already has verified experience with Docker, it should NOT be recommended."""
    class TargetEngine(MockEmbeddingEngine):
        def compute_cosine_similarity(self, vec_a, vec_b):
            return 0.20

    matcher = SkillMatcherService(embedding_engine=TargetEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)
    generator = RoadmapGeneratorService(gap_analyzer=analyzer)

    resume_docker_expert = ParsedResume(
        skills=["Docker", "Linux"],
        experience=[
            ExperienceEntry(
                title="DevOps Engineer",
                company="OpsCorp",
                responsibilities=["Containerized 30+ services using Docker on Ubuntu Linux."],
                raw_text="DevOps Engineer at OpsCorp",
            )
        ],
        raw_text="DevOps Engineer",
    )

    jd_kubernetes = ParsedJobDescription(
        required_skills=["Kubernetes"],
        preferred_skills=[],
        raw_text="Required: Kubernetes orchestration.",
    )

    response = generator.generate_roadmap(resume_docker_expert, jd_kubernetes)

    step_names = [s.skill_name for s in response.roadmap]
    # Linux and Docker should NOT be recommended because they are already demonstrated
    assert "Linux" not in step_names
    assert "Docker" not in step_names
    assert "Kubernetes" in step_names


def test_roadmap_perfect_match_returns_empty_roadmap():
    matcher = SkillMatcherService(embedding_engine=MockEmbeddingEngine(), similarity_threshold=0.65)
    analyzer = GapAnalyzerService(skill_matcher_service=matcher)
    generator = RoadmapGeneratorService(gap_analyzer=analyzer)

    resume_perfect = ParsedResume(
        skills=["Python", "FastAPI"],
        experience=[
            ExperienceEntry(
                title="Backend Architect",
                company="BigTech",
                responsibilities=["Built microservices with Python and FastAPI."],
                raw_text="Backend Architect at BigTech",
            )
        ],
        raw_text="Backend Architect",
    )

    jd_matching = ParsedJobDescription(
        required_skills=["Python", "FastAPI"],
        preferred_skills=[],
        raw_text="Required: Python and FastAPI.",
    )

    response = generator.generate_roadmap(resume_perfect, jd_matching)

    assert response.summary.total_steps == 0
    assert response.roadmap == []
    assert "fully demonstrates" in response.gap_summary.lower()
