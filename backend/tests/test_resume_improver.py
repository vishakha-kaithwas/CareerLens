"""
Unit tests for Milestone 6: Evidence-Based Resume Improvement Service.
"""

import pytest
from app.schemas.gap_analysis import GapAnalysisResponse
from app.schemas.job import ParsedJobDescription
from app.schemas.parsed_resume import (
    ContactInfo,
    ExperienceEntry,
    ParsedResume,
    ProjectEntry,
)
from app.schemas.improvement import SuggestionConfidence
from app.services.gap_analyzer import GapAnalyzerService
from app.services.resume_improver import ResumeImprovementService
from app.services.skill_matcher import SkillMatcherService
from tests.test_skill_matcher import MockEmbeddingEngine


@pytest.fixture
def improver_service():
    mock_engine = MockEmbeddingEngine()
    matcher = SkillMatcherService(embedding_engine=mock_engine)
    gap_analyzer = GapAnalyzerService(skill_matcher_service=matcher)
    return ResumeImprovementService(gap_analyzer_service=gap_analyzer)


@pytest.fixture
def sample_resume():
    return ParsedResume(
        contact=ContactInfo(name="Alex Doe", email="alex@example.com"),
        summary="Software developer with experience in building web applications.",
        skills=["Python", "FastAPI", "PostgreSQL", "Git"],
        experience=[
            ExperienceEntry(
                title="Backend Developer",
                company="TechCorp",
                responsibilities=[
                    "Worked on backend APIs using FastAPI and PostgreSQL",
                    "Responsible for building user authentication microservices",
                    "Helped with database query optimizations",
                ],
                raw_text="Backend Developer at TechCorp\nWorked on backend APIs using FastAPI and PostgreSQL\nResponsible for building user authentication microservices\nHelped with database query optimizations",
            )
        ],
        education=[],
        projects=[
            ProjectEntry(
                title="Task Tracker",
                description="Built a task tracking application with various technologies and tools.",
                technologies=["FastAPI", "Docker"],
                raw_text="Task Tracker: Built a task tracking application with various technologies and tools.",
            )
        ],
        certifications=[],
        raw_text="Full resume text...",
    )


@pytest.fixture
def sample_job():
    return ParsedJobDescription(
        title="Senior Python Backend Engineer",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        preferred_skills=["Redis", "Kubernetes"],
        tools_and_technologies=["FastAPI", "Docker", "PostgreSQL"],
        soft_skills=["Leadership"],
        experience_requirements=["3+ years backend experience"],
        education_requirements=["B.S. in Computer Science"],
        responsibilities=["Design and deploy scalable APIs"],
        raw_text="Senior Python Backend Engineer job posting...",
    )


def test_weak_verb_replacement(improver_service, sample_resume, sample_job):
    """Verifies that passive/weak verbs are replaced with strong action verbs."""
    report = improver_service.generate_improvements(sample_resume, sample_job)

    orig_texts = [b.original_text for b in report.bullet_improvements]
    suggested_texts = [b.suggested_text for b in report.bullet_improvements]

    # Check that "Worked on" was replaced
    assert any("Worked on backend APIs" in t for t in orig_texts)
    assert any("Engineered backend APIs" in t for t in suggested_texts)

    # Check that "Responsible for building" was replaced
    assert any("Responsible for building user authentication" in t for t in orig_texts)
    assert any("Developed user authentication" in t for t in suggested_texts)

    # Check that "Helped with" was replaced
    assert any("Helped with database query optimizations" in t for t in orig_texts)
    assert any("Collaborated on database query optimizations" in t for t in suggested_texts)


def test_zero_hallucinated_metrics(improver_service, sample_resume, sample_job):
    """
    Verifies that the improvement engine NEVER invents numerical metrics or percentages.
    Instead, it must formulate clarification questions for the candidate.
    """
    report = improver_service.generate_improvements(sample_resume, sample_job)

    for bullet in report.bullet_improvements:
        # Check suggested text does not contain invented percentages or metrics that weren't in original
        orig = bullet.original_text
        suggested = bullet.suggested_text

        # If original didn't have numbers, suggested text should not inject fake numbers
        orig_has_numbers = any(char.isdigit() for char in orig)
        suggested_has_numbers = any(char.isdigit() for char in suggested)

        if not orig_has_numbers:
            # If the suggestion has numbers, it must only be from job title/references, not invented stats
            assert not any(f"{n}%" in suggested for n in range(1, 100)), f"Invented percentage found in {suggested}"

    # Verifies that questions are asked instead of guessing metrics
    assert len(report.candidate_questions) > 0
    assert any("measurable outcome" in q.question.lower() for q in report.candidate_questions)


def test_vague_qualifier_detection_and_questioning(improver_service, sample_resume, sample_job):
    """Verifies that vague descriptors ('various technologies') trigger clarification questions."""
    report = improver_service.generate_improvements(sample_resume, sample_job)

    # Look for question about "various technologies"
    vague_questions = [
        q for q in report.candidate_questions
        if "various technologies" in q.context.lower() or "various technologies" in q.question.lower()
    ]
    assert len(vague_questions) > 0
    assert "what specific technologies" in vague_questions[0].question.lower()


def test_buried_skills_identification(improver_service, sample_resume, sample_job):
    """
    Verifies that skills demonstrated in projects (e.g. Docker) but omitted from the primary
    skills list are flagged for visibility.
    """
    # In sample_resume: Docker is in projects, but NOT in skills list!
    assert "Docker" not in sample_resume.skills
    assert "Docker" in sample_resume.projects[0].technologies

    report = improver_service.generate_improvements(sample_resume, sample_job)

    # Check job_relevance.buried_skills
    assert "Docker" in report.job_relevance.buried_skills

    # Check section recommendations for skills
    skills_sec = next(s for s in report.section_recommendations if s.section_name == "skills")
    assert any("Docker" in rec for rec in skills_sec.recommendations)


def test_empty_resume_sections_handling(improver_service, sample_job):
    """Verifies graceful handling when resume sections are empty."""
    empty_resume = ParsedResume(
        contact=ContactInfo(name="Jane Doe"),
        summary=None,
        skills=[],
        experience=[],
        education=[],
        projects=[],
        certifications=[],
        raw_text="Jane Doe",
    )

    report = improver_service.generate_improvements(empty_resume, sample_job)

    assert report.summary.total_bullet_improvements == 0
    assert report.summary.high_confidence_improvements == 0

    # Section recommendations should cleanly identify missing sections
    missing_sections = {s.section_name: s.status for s in report.section_recommendations}
    assert missing_sections.get("experience") == "missing"
    assert missing_sections.get("projects") == "missing"
    assert missing_sections.get("summary") == "missing"


def test_no_available_improvements_when_bullets_already_strong(improver_service, sample_job):
    """
    Verifies that when bullets already use strong active verbs and specific tech,
    unnecessary improvements are not generated.
    """
    strong_resume = ParsedResume(
        contact=ContactInfo(name="Expert Dev"),
        summary=None,
        skills=["Python", "FastAPI"],
        experience=[
            ExperienceEntry(
                title="Senior Engineer",
                company="Apex Corp",
                responsibilities=[
                    "Engineered asynchronous data pipeline processing 100k events/sec using Python and FastAPI."
                ],
                raw_text="Senior Engineer at Apex Corp",
            )
        ],
        education=[],
        projects=[],
        certifications=[],
        raw_text="Expert Dev resume",
    )

    report = improver_service.generate_improvements(strong_resume, sample_job)
    # The bullet is already strong with active verb "Engineered" and explicit metrics (100k events/sec)
    assert len(report.bullet_improvements) == 0


def test_no_identical_or_punctuation_only_suggestions(improver_service, sample_job):
    """
    Verifies that the engine does NOT produce suggestions that are identical or
    differ only by trailing punctuation from the original text (e.g. adding a period to a fragment).
    """
    resume = ParsedResume(
        contact=ContactInfo(name="Candidate"),
        skills=["FastAPI", "Python"],
        experience=[
            ExperienceEntry(
                title="Developer",
                company="Corp",
                responsibilities=[
                    "a RESTful API using FastAPI",
                    "Developed a machine learning-based insurance premium prediction system and exposed the trained model through",
                ],
                raw_text="...",
            )
        ],
        raw_text="...",
    )

    report = improver_service.generate_improvements(resume, sample_job)

    for imp in report.bullet_improvements:
        orig = imp.original_text.strip().rstrip(".").lower()
        suggested = imp.suggested_text.strip().rstrip(".").lower()
        # The suggested text must be meaningfully different from the original text
        assert orig != suggested, (
            f"Found identical or punctuation-only suggestion: '{imp.original_text}' vs '{imp.suggested_text}'"
        )


def test_no_spurious_job_requirement_targets_like_javascript_on_fastapi_bullet(improver_service):
    """
    Verifies that bullets describing FastAPI / backend technologies are NOT tagged
    with unrelated job requirements such as 'JavaScript' unless JavaScript is explicitly
    mentioned in the bullet itself.
    """
    job = ParsedJobDescription(
        title="Full Stack Engineer",
        required_skills=["Python", "FastAPI", "JavaScript", "React"],
        preferred_skills=[],
        tools_and_technologies=["FastAPI", "React", "JavaScript"],
        soft_skills=[],
        experience_requirements=[],
        education_requirements=[],
        responsibilities=[],
        raw_text="...",
    )

    resume = ParsedResume(
        contact=ContactInfo(name="Alex"),
        skills=["Python", "FastAPI", "JavaScript"],
        experience=[
            ExperienceEntry(
                title="Backend Developer",
                company="StartUp",
                responsibilities=[
                    "Worked on backend APIs using FastAPI and PostgreSQL",
                ],
                raw_text="...",
            )
        ],
        projects=[
            ProjectEntry(
                title="ML Insurance System",
                description="Assisted in developing predictive models using Scikit-Learn and FastAPI.",
                technologies=["Python", "FastAPI", "JavaScript"],  # JavaScript might be in project tech
                raw_text="...",
            )
        ],
        raw_text="...",
    )

    report = improver_service.generate_improvements(resume, job)

    for imp in report.bullet_improvements:
        # None of these bullets mention JavaScript, so target requirement must NEVER be JavaScript!
        assert imp.relevant_job_requirement != "JavaScript", (
            f"Spurious target 'JavaScript' associated with bullet: '{imp.original_text}'"
        )
        if "FastAPI" in imp.original_text:
            assert imp.relevant_job_requirement in ("FastAPI", "Python", None)


def test_routine_implementation_bullets_do_not_get_blanket_metric_questions(improver_service, sample_job):
    """
    Verifies that routine construction bullets (e.g. building an API, configuring Swagger)
    do not trigger blanket questions demanding % improvement or metrics.
    """
    resume = ParsedResume(
        contact=ContactInfo(name="Alex"),
        skills=["Python", "FastAPI"],
        experience=[
            ExperienceEntry(
                title="Developer",
                company="TechCorp",
                responsibilities=[
                    "Responsible for building user authentication microservices",
                ],
                raw_text="...",
            )
        ],
        raw_text="...",
    )

    report = improver_service.generate_improvements(resume, sample_job)

    # Bullet describes building an auth microservice, not an optimization or performance tuning
    # It should NOT have a question demanding % improvement or measurable outcome metrics
    metric_questions = [
        q for q in report.candidate_questions
        if "measurable outcome" in q.question.lower() or "latency reduction" in q.question.lower()
    ]
    assert len(metric_questions) == 0, f"Unexpected metric question on routine construction task: {metric_questions}"

