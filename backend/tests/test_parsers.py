"""
Unit tests for ResumeParserService, JobDescriptionParserService, and SkillExtractorService.
"""

import pytest
from app.services.skill_extractor import SkillExtractorService
from app.services.resume_parser import ResumeParserService
from app.services.job_parser import JobDescriptionParserService


def test_skill_extractor_normalization():
    service = SkillExtractorService()
    sample_text = (
        "Experienced in Python3, postgres, docker-compose, and building RESTful APIs. "
        "Also used scikit-learn, reactjs, and k8s for deployments."
    )
    skills = service.extract_technical_skills(sample_text)

    # Verifies normalization to canonical names
    assert "Python" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "RESTful APIs" in skills
    assert "Scikit-Learn" in skills
    assert "React" in skills


def test_skill_extractor_soft_skills():
    service = SkillExtractorService()
    text = "Demonstrated strong leadership, verbal communication, and problem solving skills."
    soft = service.extract_soft_skills(text)
    assert "Leadership" in soft
    assert "Communication" in soft
    assert "Problem Solving" in soft


def test_resume_parser_structured_sections():
    service = ResumeParserService()
    sample_resume = """
    Alex Morgan
    Email: alex.morgan@example.com | Phone: (555) 123-4567 | San Francisco, CA
    LinkedIn: linkedin.com/in/alexmorgan | GitHub: github.com/alexmorgan

    SUMMARY
    Senior Backend Architect with 6 years building high-throughput microservices in Python.

    TECHNICAL SKILLS
    Languages: Python, SQL, TypeScript
    Frameworks & Tools: FastAPI, Docker, PostgreSQL, Redis, AWS

    EXPERIENCE
    Staff Software Engineer - CloudCore Systems
    Jan 2022 - Present
    - Designed distributed API gateways processing 50M requests daily using FastAPI.
    - Optimized PostgreSQL query performance, saving $40k/yr on AWS RDS costs.

    Software Engineer - NextGen Labs
    Jun 2019 - Dec 2021
    - Containerized legacy services with Docker and deployed to Kubernetes.
    - Mentored 4 junior engineers on clean code and unit testing.

    EDUCATION
    Master of Science in Computer Science
    Stanford University
    Sep 2017 - Jun 2019

    PROJECTS
    CareerLens | Python, FastAPI, Docker
    - Built career gap intelligence system.
    - Extracted and normalized technical skills.

    CERTIFICATIONS
    AWS Certified Solutions Architect - Amazon Web Services
    """

    parsed = service.parse(sample_resume)

    # 1. Contact verification
    assert parsed.contact.name == "Alex Morgan"
    assert parsed.contact.email == "alex.morgan@example.com"
    assert parsed.contact.phone == "(555) 123-4567"
    assert parsed.contact.linkedin == "linkedin.com/in/alexmorgan"
    assert parsed.contact.github == "github.com/alexmorgan"

    # 2. Summary
    assert "Senior Backend Architect" in (parsed.summary or "")

    # 3. Skills
    assert "Python" in parsed.skills
    assert "FastAPI" in parsed.skills
    assert "Docker" in parsed.skills
    assert "PostgreSQL" in parsed.skills
    assert "Redis" in parsed.skills
    assert "AWS" in parsed.skills

    # 4. Experience entries
    assert len(parsed.experience) >= 2
    assert any("CloudCore" in (exp.company or "") or "Staff Software Engineer" in (exp.title or "") for exp in parsed.experience)
    assert any("NextGen" in (exp.company or "") or "Software Engineer" in (exp.title or "") for exp in parsed.experience)

    # 5. Education
    assert len(parsed.education) >= 1
    assert any("Stanford" in (edu.institution or "") for edu in parsed.education)
    assert any("Master" in (edu.degree or "") for edu in parsed.education)

    # 6. Projects
    assert len(parsed.projects) >= 1
    assert any("CareerLens" in p.title for p in parsed.projects)

    # 7. Certifications
    assert len(parsed.certifications) >= 1
    assert any("AWS Certified" in c.name for c in parsed.certifications)

    # 8. Source verification preservation
    assert parsed.raw_text == sample_resume


def test_resume_parser_handles_missing_sections():
    service = ResumeParserService()
    minimal_resume = """
    Jane Plain
    Email: plain@test.com

    EXPERIENCE
    Intern - Startup Inc
    Jun 2023 - Aug 2023
    - Wrote Python scripts.
    """
    parsed = service.parse(minimal_resume)

    assert parsed.contact.name == "Jane Plain"
    assert parsed.contact.email == "plain@test.com"
    assert parsed.summary is None
    assert parsed.education == []
    assert parsed.projects == []
    assert parsed.certifications == []
    assert "Python" in parsed.skills
    assert len(parsed.experience) == 1


def test_job_parser_structured_requirements():
    service = JobDescriptionParserService()
    sample_jd = """
    Job Title: Lead Backend Engineer

    About Us:
    TechCorp builds autonomous data infrastructure.

    Responsibilities:
    - Architect and scale backend services in Python and FastAPI.
    - Lead architecture discussions with cross-functional product teams.
    - Mentor junior and mid-level software engineers.

    Requirements:
    - 5+ years of software development experience with Python.
    - Strong proficiency in Docker and PostgreSQL.
    - Bachelor's degree in Computer Science or equivalent.
    - Excellent communication and problem solving skills.

    Preferred Qualifications:
    - Experience with Kubernetes and AWS.
    - Familiarity with Redis and GraphQL.
    """

    parsed = service.parse(sample_jd)

    assert parsed.title == "Lead Backend Engineer"
    assert "Python" in parsed.required_skills
    assert "FastAPI" in parsed.required_skills
    assert "PostgreSQL" in parsed.required_skills
    assert "Docker" in parsed.required_skills

    # Preferred qualifications should be separated
    assert "Kubernetes" in parsed.preferred_skills
    assert "AWS" in parsed.preferred_skills

    # Soft skills
    assert "Communication" in parsed.soft_skills or "Problem Solving" in parsed.soft_skills
    assert "Leadership" in parsed.soft_skills

    # Experience & Education
    assert len(parsed.experience_requirements) >= 1
    assert any("5" in req for req in parsed.experience_requirements)
    assert len(parsed.education_requirements) >= 1
    assert any("Bachelor" in req for req in parsed.education_requirements)

    # Responsibilities
    assert len(parsed.responsibilities) >= 2
    assert parsed.raw_text == sample_jd


def test_resume_parser_splits_multiple_projects_and_isolates_extracurriculars():
    """
    Verifies that multiple projects are parsed into individual ProjectEntry records,
    and extracurricular activities / student clubs / hackathons are isolated into
    parsed.extracurriculars instead of bleeding into the project section.
    """
    service = ResumeParserService()
    sample_text = """
    Rohan Sharma
    Email: rohan@example.com | Phone: +91 9876543210 | Pune, India
    GitHub: github.com/rohansharma | LinkedIn: linkedin.com/in/rohansharma

    TECHNICAL SKILLS
    Languages: Python, JavaScript, SQL
    Frameworks: FastAPI, React, PyTorch, Docker

    PROJECTS
    Insurance Premium Prediction System | Python, FastAPI, Scikit-Learn
    - Developed a machine learning-based insurance premium prediction system and exposed the trained model through a RESTful API using FastAPI.
    - Containerized the application using Docker and deployed with automated inference testing.

    Autonomous Drone Obstacle Detection | PyTorch, OpenCV, ROS
    - Implemented real-time vision algorithms for quadcopter obstacle avoidance.
    - Optimized model latency to achieve 45 FPS on edge hardware.

    EXTRACURRICULAR ACTIVITIES & LEADERSHIP
    CSI Student Branch - Technical Lead
    - Conducted hands-on technical workshops on Python programming and Git for 200+ students.

    Abhyudaya Coding Club - Active Member
    - Organized bi-weekly competitive coding contests and mentored first-year students.

    Smart India Hackathon - Team Lead & Finalist
    - Led a 6-member team to build an AI-based agricultural advisory system.
    """

    parsed = service.parse(sample_text)

    # 1. Verify multiple distinct projects
    assert len(parsed.projects) == 2, f"Expected 2 projects, got {len(parsed.projects)}"
    proj1 = parsed.projects[0]
    proj2 = parsed.projects[1]

    assert "Insurance Premium Prediction" in (proj1.title or "")
    assert "Drone" in (proj2.title or "")
    assert "FastAPI" in proj1.technologies or "Scikit-Learn" in proj1.technologies
    assert "PyTorch" in proj2.technologies or "OpenCV" in proj2.technologies

    # Ensure extracurricular text did NOT bleed into project description
    assert "CSI Student Branch" not in (proj1.description or "")
    assert "CSI Student Branch" not in (proj2.description or "")
    assert "Abhyudaya" not in (proj2.description or "")
    assert "Smart India Hackathon" not in (proj2.description or "")

    # 2. Verify extracurricular extraction
    assert len(parsed.extracurriculars) >= 2, f"Expected at least 2 extracurriculars, got {len(parsed.extracurriculars)}"
    titles = [e.title for e in parsed.extracurriculars]
    assert any("CSI Student Branch" in t for t in titles)
    assert any("Abhyudaya" in t for t in titles) or any("Smart India Hackathon" in t for t in titles)

