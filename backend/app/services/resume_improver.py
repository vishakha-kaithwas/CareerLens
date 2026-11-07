"""
Resume Bullet Improvement Service.

Analyzes resume content across Experience, Projects, Skills, Summary, and Certifications
against target job description requirements and gap analysis findings.

Core Principles:
1. Grounded in Evidence: Every suggestion references existing candidate experience, projects, or declared skills.
2. Zero Hallucination: NEVER invent numbers, percentages, performance metrics, company names, or leadership roles.
3. Active Voice & Technical Specificity: Replaces weak verbs (e.g., 'worked on', 'helped with', 'responsible for')
   with precise action verbs without altering factual scope.
4. Meaningful Improvement Only: Never generate a suggestion that merely adds punctuation or capitalization.
5. Accurate Requirement Association: Associate a bullet with a job requirement ONLY when there is an actual supported relationship.
6. Honest Candidate Clarification: When impact, scale, or metrics would strengthen a bullet, generates specific questions
   for the candidate rather than fabricating details.
"""

import re
import uuid
from typing import Dict, List, Optional, Set, Tuple

from app.schemas.gap_analysis import GapAnalysisItem, GapAnalysisResponse
from app.schemas.job import ParsedJobDescription
from app.schemas.parsed_resume import ExperienceEntry, ParsedResume, ProjectEntry
from app.schemas.improvement import (
    BulletImprovement,
    CandidateQuestion,
    EvidenceReference,
    ImprovementSummary,
    JobRelevanceAnalysis,
    ResumeImprovementResponse,
    SectionRecommendation,
    SuggestionConfidence,
)
from app.services.gap_analyzer import GapAnalyzerService
from app.ml.skill_taxonomy import ALIAS_TO_CANONICAL


# Action verb enhancements (weak/passive -> strong/precise)
WEAK_VERB_PATTERNS: List[Tuple[str, str, str]] = [
    (r"^(?:worked on|was working on)\b", "Engineered", "Replaces passive phrasing with an engineering action verb."),
    (r"^(?:helped with|assisted with|assisted in)\b", "Collaborated on", "Clarifies collaborative technical contribution."),
    (r"^(?:responsible for building|responsible for creating|responsible for)\b", "Developed", "Focuses on active technical execution rather than passive duty assignment."),
    (r"^(?:did|made)\b", "Built", "Replaces vague verb with a clear construction action verb."),
    (r"^(?:used|utilized)\b", "Implemented", "Highlights active design and implementation rather than basic tool usage."),
    (r"^(?:handled|dealt with)\b", "Maintained", "Specifies system operation and maintenance responsibility."),
    (r"^(?:looked at|checked)\b", "Audited and monitored", "Converts casual observation into technical validation."),
    (r"^(?:involved in)\b", "Contributed to", "Converts passive involvement into active engineering contribution."),
]

# Vague technical qualifiers to flag
VAGUE_QUALIFIERS = [
    "various technologies",
    "different tools",
    "many features",
    "some bugs",
    "multiple tasks",
    "stuff",
    "things",
    "etc",
    "and more",
]


class ResumeImprovementService:
    """Generates evidence-backed resume improvements grounded in candidate data and job requirements."""

    def __init__(self, gap_analyzer_service: Optional[GapAnalyzerService] = None):
        self.gap_analyzer = gap_analyzer_service or GapAnalyzerService()

    def generate_improvements(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription,
        gap_analysis: Optional[GapAnalysisResponse] = None,
    ) -> ResumeImprovementResponse:
        """
        Produces a complete evidence-based improvement report for a resume tailored to a job description.
        """
        # 1. Obtain or compute gap analysis
        if gap_analysis is None:
            gap_analysis = self.gap_analyzer.analyze_gaps(resume, job_description)

        # 2. Extract candidate knowledge & tech context
        candidate_skills = set(resume.skills)
        candidate_tech_in_projects: Set[str] = set()
        for proj in resume.projects:
            candidate_tech_in_projects.update(proj.technologies)

        all_known_tech = candidate_skills.union(candidate_tech_in_projects)

        # 3. Analyze bullets across Experience, Projects, Summary
        bullet_improvements: List[BulletImprovement] = []
        all_questions: List[CandidateQuestion] = []

        # 3a. Experience Bullets
        for exp in resume.experience:
            comp = exp.company or "Work Experience"
            for bullet in exp.responsibilities:
                imp = self._analyze_bullet(
                    bullet=bullet,
                    section_name="experience",
                    parent_context=f"{exp.title or 'Role'} at {comp}",
                    candidate_tech=all_known_tech,
                    gap_analysis=gap_analysis,
                    job_desc=job_description,
                )
                if imp:
                    bullet_improvements.append(imp)
                    all_questions.extend(imp.candidate_questions)

        # 3b. Project Bullets / Descriptions
        for proj in resume.projects:
            proj_title = proj.title or "Project"
            if proj.description:
                # Split description into sentences or bullet fragments
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", proj.description) if len(s.strip()) > 10]
                for s in sentences:
                    imp = self._analyze_bullet(
                        bullet=s,
                        section_name="projects",
                        parent_context=f"Project: {proj_title}",
                        candidate_tech=all_known_tech.union(set(proj.technologies)),
                        gap_analysis=gap_analysis,
                        job_desc=job_description,
                        project_explicit_tech=proj.technologies,
                    )
                    if imp:
                        bullet_improvements.append(imp)
                        all_questions.extend(imp.candidate_questions)

        # 3c. Summary Section Analysis
        if resume.summary:
            summary_imp = self._analyze_summary(
                summary_text=resume.summary,
                job_desc=job_description,
                gap_analysis=gap_analysis,
                candidate_tech=all_known_tech,
            )
            if summary_imp:
                bullet_improvements.append(summary_imp)
                all_questions.extend(summary_imp.candidate_questions)

        # 4. Section-level recommendations
        section_recs = self._build_section_recommendations(
            resume=resume,
            job_desc=job_description,
            gap_analysis=gap_analysis,
            candidate_tech=all_known_tech,
        )

        # 5. Job Relevance Analysis
        job_relevance = self._build_job_relevance_analysis(
            resume=resume,
            job_desc=job_description,
            gap_analysis=gap_analysis,
            candidate_tech=all_known_tech,
        )

        # 6. Executive Summary
        high_conf = sum(1 for b in bullet_improvements if b.confidence == SuggestionConfidence.HIGH)
        total_imps = len(bullet_improvements)

        if total_imps == 0:
            readiness = "Well-articulated. Existing bullet points are specific and well-aligned with role requirements."
        elif high_conf >= 2:
            readiness = "Strong foundation with concrete improvement opportunities to highlight verified technical competencies."
        else:
            readiness = "Moderate alignment. Candidate should clarify project outcomes and highlight demonstrated skills relevant to target job requirements."

        summary = ImprovementSummary(
            total_bullet_improvements=total_imps,
            high_confidence_improvements=high_conf,
            questions_for_candidate=len(all_questions),
            overall_readiness=readiness,
        )

        return ResumeImprovementResponse(
            summary=summary,
            bullet_improvements=bullet_improvements,
            section_recommendations=section_recs,
            job_relevance=job_relevance,
            candidate_questions=all_questions,
        )

    def _analyze_bullet(
        self,
        bullet: str,
        section_name: str,
        parent_context: str,
        candidate_tech: Set[str],
        gap_analysis: GapAnalysisResponse,
        job_desc: ParsedJobDescription,
        project_explicit_tech: Optional[List[str]] = None,
    ) -> Optional[BulletImprovement]:
        """
        Evaluates a single resume bullet for weak verbs, vague phrasing, and relevance to target requirements.
        Only generates an improvement when there is a meaningful semantic/wording change.
        Excludes trivial punctuation or capitalization changes.
        """
        clean_bullet = bullet.strip().rstrip(".")
        if len(clean_bullet) < 12:
            return None

        improved_text = clean_bullet
        reasons: List[str] = []
        questions: List[CandidateQuestion] = []
        evidence_refs: List[EvidenceReference] = []
        related_job_req: Optional[str] = None
        confidence = SuggestionConfidence.MEDIUM

        # 1. Action Verb Replacement
        weak_verb_matched = False
        for pattern, replacement, reason in WEAK_VERB_PATTERNS:
            if re.search(pattern, clean_bullet, flags=re.IGNORECASE):
                improved_text = re.sub(pattern, replacement, improved_text, count=1, flags=re.IGNORECASE)
                reasons.append(reason)
                weak_verb_matched = True
                confidence = SuggestionConfidence.HIGH
                break

        # 2. Vague Qualifier Flagging
        vague_matched = False
        for vague in VAGUE_QUALIFIERS:
            if re.search(r"\b" + re.escape(vague) + r"\b", clean_bullet, flags=re.IGNORECASE):
                reasons.append(f"Contains vague descriptor '{vague}'. Specify the exact technologies or features implemented.")
                questions.append(
                    CandidateQuestion(
                        context=f"'{clean_bullet}' ({parent_context})",
                        question=f"What specific technologies, tools, or features were included when you mentioned '{vague}'?",
                        why_needed="Replacing vague generalities with explicit tools proves hands-on proficiency without inflating scope.",
                    )
                )
                vague_matched = True

        # 2b. Measurable Outcome Flagging for Impact / Optimization Claims Only
        # Prompt for measurable metrics ONLY when the bullet describes an optimization, reduction, or performance impact.
        # Never prompt on routine construction/implementation tasks.
        IMPACT_KEYWORDS = ["optimiz", "reduc", "improv", "increas", "scal", "accelerat", "boost"]
        has_impact_claim = any(kw in clean_bullet.lower() for kw in IMPACT_KEYWORDS)
        has_existing_metric = any(char.isdigit() for char in clean_bullet)
        if has_impact_claim and not has_existing_metric:
            questions.append(
                CandidateQuestion(
                    context=f"'{clean_bullet}' ({parent_context})",
                    question="What was the measurable outcome or scale (e.g. % improvement, latency reduction, queries optimized) from this work?",
                    why_needed="Quantifiable outcomes turn a general claim of optimization into verified engineering achievement.",
                )
            )

        # 3. Connect to relevant Job Requirements (Strict Association Only)
        # Match only when the bullet text explicitly mentions the requirement, its canonical name, or a known alias
        matched_item: Optional[GapAnalysisItem] = None
        for item in gap_analysis.results:
            req_name = item.requirement
            canonical = ALIAS_TO_CANONICAL.get(req_name.lower(), req_name)
            # Check if canonical or requirement name appears in clean_bullet with word boundaries
            pattern_str = rf"(?<![A-Za-z0-9_+#]){re.escape(req_name.lower())}(?![A-Za-z0-9_+#])"
            canonical_pattern = rf"(?<![A-Za-z0-9_+#]){re.escape(canonical.lower())}(?![A-Za-z0-9_+#])"
            if re.search(pattern_str, clean_bullet.lower()) or re.search(canonical_pattern, clean_bullet.lower()):
                matched_item = item
                related_job_req = req_name
                break

        # 4. Filter out meaningless improvements:
        # A suggestion is meaningful ONLY IF:
        # a) A weak verb was actually transformed into a strong engineering verb
        # b) OR a vague qualifier was detected and prompted
        # If neither occurred, do not generate a suggestion just to add a period.
        if not weak_verb_matched and not vague_matched:
            return None

        # Compare clean_bullet and improved_text ignoring punctuation and casing
        norm_orig = re.sub(r"[^A-Za-z0-9]", "", clean_bullet.lower())
        norm_imp = re.sub(r"[^A-Za-z0-9]", "", improved_text.lower())
        if norm_orig == norm_imp and not vague_matched:
            # Punctuation/casing only change -> skip!
            return None

        # Build evidence references
        evidence_refs.append(
            EvidenceReference(
                source_section=section_name,
                evidence_text=clean_bullet,
                related_job_requirement=related_job_req,
            )
        )

        why_useful = " ".join(reasons) if reasons else "Refines clarity and precision of technical contribution."
        if related_job_req:
            why_useful += f" Directly addresses target job requirement for '{related_job_req}'."

        final_suggested = improved_text.strip()
        if not final_suggested.endswith((".", "!", "?")):
            final_suggested += "."

        return BulletImprovement(
            id=f"imp-{uuid.uuid4().hex[:8]}",
            section_name=section_name,
            original_text=clean_bullet,
            suggested_text=final_suggested,
            why_useful=why_useful,
            relevant_job_requirement=related_job_req,
            evidence=evidence_refs,
            confidence=confidence,
            needs_candidate_info=len(questions) > 0,
            candidate_questions=questions,
        )

    def _analyze_summary(
        self,
        summary_text: str,
        job_desc: ParsedJobDescription,
        gap_analysis: GapAnalysisResponse,
        candidate_tech: Set[str],
    ) -> Optional[BulletImprovement]:
        """
        Evaluates the summary section for relevance to the target job title and verified skills.
        Only generates an improvement if the current summary is generic or weak.
        """
        clean_summary = summary_text.strip()
        if len(clean_summary) < 20:
            return None

        # If summary is already strong and mentions role/tech, do not generate redundant suggestion
        target_title = job_desc.title or "Software Engineer"
        if target_title.lower() in clean_summary.lower() and len(clean_summary.split()) > 15:
            return None

        # Identify verified matched skills from gap analysis
        verified_skills = [
            item.requirement for item in gap_analysis.matched_requirements
            if item.requirement.lower() in [s.lower() for s in candidate_tech]
        ]

        skill_str = ", ".join(verified_skills[:4]) if verified_skills else "software engineering"
        suggested = f"Results-focused software engineer with hands-on experience in {skill_str}. Demonstrated ability in designing reliable systems aligned with {target_title} requirements."

        questions = [
            CandidateQuestion(
                context="Professional Summary",
                question=f"What is your primary career narrative or core technical passion relating to the '{target_title}' role?",
                why_needed="Ensures your professional summary genuinely reflects your career goals and core technical identity.",
            )
        ]

        return BulletImprovement(
            id=f"imp-{uuid.uuid4().hex[:8]}",
            section_name="summary",
            original_text=clean_summary,
            suggested_text=suggested,
            why_useful=f"Tailors the professional summary to align with '{target_title}' while highlighting verified competencies.",
            relevant_job_requirement=job_desc.title,
            evidence=[
                EvidenceReference(
                    source_section="summary",
                    evidence_text=clean_summary,
                    related_job_requirement=job_desc.title,
                )
            ],
            confidence=SuggestionConfidence.MEDIUM,
            needs_candidate_info=True,
            candidate_questions=questions,
        )

    def _build_section_recommendations(
        self,
        resume: ParsedResume,
        job_desc: ParsedJobDescription,
        gap_analysis: GapAnalysisResponse,
        candidate_tech: Set[str],
    ) -> List[SectionRecommendation]:
        """Provides section-by-section strategic guidance."""
        sections: List[SectionRecommendation] = []

        # 1. Summary Section
        if not resume.summary:
            sections.append(
                SectionRecommendation(
                    section_name="summary",
                    status="missing",
                    recommendations=[
                        f"Consider adding a 2-3 sentence professional summary tailored to '{job_desc.title or 'the target role'}', highlighting your verified competencies."
                    ],
                    skills_to_highlight=[item.requirement for item in gap_analysis.matched_requirements[:3]],
                    irrelevant_or_repetitive_notes=[],
                )
            )
        else:
            sections.append(
                SectionRecommendation(
                    section_name="summary",
                    status="present",
                    recommendations=[
                        "Ensure the summary leads with technical competencies directly requested by the employer."
                    ],
                    skills_to_highlight=[item.requirement for item in gap_analysis.matched_requirements[:3]],
                    irrelevant_or_repetitive_notes=[],
                )
            )

        # 2. Technical Skills Section
        project_tech: Set[str] = set()
        for p in resume.projects:
            project_tech.update(p.technologies)
        
        buried = [t for t in project_tech if t.lower() not in [s.lower() for s in resume.skills]]

        skills_recs = []
        if buried:
            skills_recs.append(
                f"You have used {', '.join(buried)} in your projects, but they are omitted from your primary Skills section. Add them explicitly to ensure quick technical review visibility."
            )
        
        highlight_skills = [
            item.requirement for item in gap_analysis.matched_requirements + gap_analysis.partially_demonstrated_requirements
            if item.requirement.lower() in [s.lower() for s in candidate_tech.union(project_tech)]
        ]

        sections.append(
            SectionRecommendation(
                section_name="skills",
                status="needs_focus" if buried else "strong",
                recommendations=skills_recs or ["Skills section clearly reflects technical toolkit."],
                skills_to_highlight=highlight_skills[:6],
                irrelevant_or_repetitive_notes=[],
            )
        )

        # 3. Experience Section
        if not resume.experience:
            sections.append(
                SectionRecommendation(
                    section_name="experience",
                    status="missing",
                    recommendations=[
                        "No formal work experience listed. Focus on making your Project entries robust, detailing architectural decisions and testing practices."
                    ],
                    skills_to_highlight=[],
                    irrelevant_or_repetitive_notes=[],
                )
            )
        else:
            sections.append(
                SectionRecommendation(
                    section_name="experience",
                    status="present",
                    recommendations=[
                        "Focus each bullet on: Action Verb + Technical Implementation + Problem Solved + Truthful Outcome.",
                        "Avoid passive phrases like 'worked on' or 'responsible for'."
                    ],
                    skills_to_highlight=[item.requirement for item in gap_analysis.matched_requirements[:4]],
                    irrelevant_or_repetitive_notes=[],
                )
            )

        # 4. Projects Section
        if not resume.projects:
            sections.append(
                SectionRecommendation(
                    section_name="projects",
                    status="missing",
                    recommendations=[
                        "Add practical projects demonstrating end-to-end software development, including automated tests and deployment details."
                    ],
                    skills_to_highlight=[],
                    irrelevant_or_repetitive_notes=[],
                )
            )
        else:
            sections.append(
                SectionRecommendation(
                    section_name="projects",
                    status="strong",
                    recommendations=[
                        "Explicitly list technologies used for each project.",
                        "Link to active GitHub repositories or live demonstrations wherever possible."
                    ],
                    skills_to_highlight=[t for p in resume.projects for t in p.technologies][:5],
                    irrelevant_or_repetitive_notes=[],
                )
            )

        # 5. Certifications Section
        if not resume.certifications:
            sections.append(
                SectionRecommendation(
                    section_name="certifications",
                    status="missing",
                    recommendations=[
                        "Certifications are optional, but recognized vendor credentials (e.g. AWS, Kubernetes, GCP) can support early-career applications."
                    ],
                    skills_to_highlight=[],
                    irrelevant_or_repetitive_notes=[],
                )
            )

        return sections

    def _build_job_relevance_analysis(
        self,
        resume: ParsedResume,
        job_desc: ParsedJobDescription,
        gap_analysis: GapAnalysisResponse,
        candidate_tech: Set[str],
    ) -> JobRelevanceAnalysis:
        """Assesses overall alignment, buried skills, and missing critical requirements."""
        strengths = [
            f"{item.requirement} ({item.match_method.value} match with verified evidence)"
            for item in gap_analysis.matched_requirements
        ]

        project_tech: Set[str] = set()
        for p in resume.projects:
            project_tech.update(p.technologies)
        
        buried = [
            t for t in project_tech
            if t.lower() not in [s.lower() for s in resume.skills]
            and any(t.lower() == req.lower() for req in job_desc.required_skills + job_desc.preferred_skills)
        ]

        missing_critical = [
            item.requirement for item in gap_analysis.not_demonstrated_requirements
            if item.requirement_type.value == "required"
        ]

        return JobRelevanceAnalysis(
            top_aligned_strengths=strengths[:5],
            buried_skills=buried,
            missing_critical_evidence=missing_critical[:5],
        )
