"""
Roadmap Generator Service.

Translates Career Gap Analysis results (M4) into a structured, dependency-ordered,
actionable learning roadmap:
1. Identifies missing and partially demonstrated requirements.
2. Traverses the SkillDependencyGraph to detect unfulfilled prerequisite skills.
3. Orders steps logically (foundations -> prerequisites -> target requirements).
4. Assigns priority levels:
   - CRITICAL: Missing required skill with prerequisite dependencies.
   - HIGH: Missing required skill.
   - MEDIUM: Partially demonstrated required skill OR missing preferred skill.
   - LOW: Partially demonstrated preferred skill.
5. Supplies specific practical projects, deliverables, and estimated hours.
"""

import logging
from typing import Dict, List, Optional, Set

from app.ml.dependency_graph import SkillDependencyGraph
from app.ml.skill_knowledge_base import SKILL_KNOWLEDGE_BASE, SkillDefinition
from app.ml.skill_taxonomy import ALIAS_TO_CANONICAL
from app.schemas.gap_analysis import (
    GapAnalysisItem,
    GapAnalysisResponse,
    RequirementClassification,
    RequirementType,
)
from app.schemas.job import ParsedJobDescription
from app.schemas.parsed_resume import ParsedResume
from app.schemas.roadmap import (
    RoadmapPriority,
    RoadmapResponse,
    RoadmapStep,
    RoadmapSummary,
)
from app.services.gap_analyzer import GapAnalyzerService

logger = logging.getLogger("careerlens.roadmap_generator")


class RoadmapGeneratorService:
    """Orchestrates gap analysis and dependency intelligence to generate personalized roadmaps."""

    def __init__(
        self,
        gap_analyzer: Optional[GapAnalyzerService] = None,
        dependency_graph: Optional[SkillDependencyGraph] = None,
    ):
        self.gap_analyzer = gap_analyzer or GapAnalyzerService()
        self.dependency_graph = dependency_graph or SkillDependencyGraph()

    def generate_roadmap(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription,
    ) -> RoadmapResponse:
        """
        Executes gap analysis and builds a personalized, prioritized, dependency-ordered learning roadmap.
        """
        # 1. Execute gap analysis (M4)
        gap_report = self.gap_analyzer.analyze_gaps(resume, job_description)

        # 2. Extract verified demonstrated skills from the candidate's resume
        demonstrated_skills = {
            item.requirement.lower()
            for item in gap_report.matched_requirements
        }
        # Also include any raw skills from resume
        for s in resume.skills:
            demonstrated_skills.add(s.lower())

        # 3. Identify gaps (Not Demonstrated & Partially Demonstrated)
        actionable_gaps: List[GapAnalysisItem] = [
            item for item in gap_report.results
            if item.classification in (
                RequirementClassification.NOT_DEMONSTRATED,
                RequirementClassification.PARTIALLY_DEMONSTRATED,
            )
        ]

        if not actionable_gaps:
            return RoadmapResponse(
                summary=RoadmapSummary(
                    total_steps=0,
                    critical_steps_count=0,
                    high_steps_count=0,
                    medium_steps_count=0,
                    low_steps_count=0,
                    total_estimated_hours=0,
                ),
                roadmap=[],
                gap_summary="Outstanding match! Your resume fully demonstrates all evaluated job requirements with verified evidence.",
            )

        # 4. Resolve prerequisites and gather candidate roadmap steps
        roadmap_steps_map: Dict[str, RoadmapStep] = {}
        target_skills_order: List[str] = []

        for gap in actionable_gaps:
            canonical_name = ALIAS_TO_CANONICAL.get(gap.requirement.lower(), gap.requirement)
            is_required = gap.requirement_type == RequirementType.REQUIRED
            is_partial = gap.classification == RequirementClassification.PARTIALLY_DEMONSTRATED

            # A. Check for unmet prerequisites
            unmet_prereqs = self.dependency_graph.get_unmet_prerequisites(
                canonical_name, demonstrated_skills
            )

            for prereq in unmet_prereqs:
                if prereq not in roadmap_steps_map:
                    prereq_defn = self._get_skill_definition(prereq)
                    roadmap_steps_map[prereq] = RoadmapStep(
                        step_number=0,  # Will be assigned after topological sort
                        skill_name=prereq,
                        category=prereq_defn.category,
                        priority=RoadmapPriority.CRITICAL if is_required else RoadmapPriority.MEDIUM,
                        is_prerequisite_for=canonical_name,
                        why_it_matters=f"Foundational prerequisite required before mastering {canonical_name} for this position.",
                        current_evidence="No prerequisite evidence identified on resume.",
                        learning_topics=prereq_defn.learning_topics,
                        practical_project=prereq_defn.practical_projects[0] if prereq_defn.practical_projects else f"Build a practical {prereq} starter project.",
                        expected_deliverable=prereq_defn.deliverables[0] if prereq_defn.deliverables else f"GitHub repository demonstrating {prereq}.",
                        estimated_hours=prereq_defn.estimated_hours,
                    )
                    target_skills_order.append(prereq)

            # B. Target requirement step
            priority = self._determine_priority(is_required, is_partial, bool(unmet_prereqs))
            why_it_matters = self._format_why_it_matters(gap, is_required)
            current_evidence = gap.resume_evidence or "No verified evidence demonstrated on resume."

            target_defn = self._get_skill_definition(canonical_name)

            if canonical_name not in roadmap_steps_map:
                roadmap_steps_map[canonical_name] = RoadmapStep(
                    step_number=0,
                    skill_name=canonical_name,
                    category=target_defn.category,
                    priority=priority,
                    is_prerequisite_for=None,
                    why_it_matters=why_it_matters,
                    current_evidence=current_evidence,
                    learning_topics=target_defn.learning_topics,
                    practical_project=target_defn.practical_projects[0] if target_defn.practical_projects else f"Build a project demonstrating {canonical_name}.",
                    expected_deliverable=target_defn.deliverables[0] if target_defn.deliverables else f"Demonstrated implementation of {canonical_name} added to resume.",
                    estimated_hours=target_defn.estimated_hours if not is_partial else max(5, target_defn.estimated_hours // 2),
                )
                target_skills_order.append(canonical_name)

        # 5. Order steps using Topological Sort + Priority ordering
        ordered_skill_names = self._order_roadmap(target_skills_order, roadmap_steps_map)

        final_steps: List[RoadmapStep] = []
        for idx, skill_name in enumerate(ordered_skill_names, 1):
            step = roadmap_steps_map[skill_name]
            step.step_number = idx
            final_steps.append(step)

        # 6. Aggregate summary metrics
        critical_count = sum(1 for s in final_steps if s.priority == RoadmapPriority.CRITICAL)
        high_count = sum(1 for s in final_steps if s.priority == RoadmapPriority.HIGH)
        medium_count = sum(1 for s in final_steps if s.priority == RoadmapPriority.MEDIUM)
        low_count = sum(1 for s in final_steps if s.priority == RoadmapPriority.LOW)
        total_hours = sum(s.estimated_hours for s in final_steps)

        summary = RoadmapSummary(
            total_steps=len(final_steps),
            critical_steps_count=critical_count,
            high_steps_count=high_count,
            medium_steps_count=medium_count,
            low_steps_count=low_count,
            total_estimated_hours=total_hours,
        )

        overall_score = gap_report.overall_coverage.overall_score
        score_text = f"{overall_score:.1f}%" if overall_score is not None else "N/A"
        gap_summary_text = (
            f"Overall requirement coverage is currently at {score_text}. "
            f"We identified {len(actionable_gaps)} requirement gap(s) requiring attention. "
            f"Following this {len(final_steps)}-step roadmap will systematically close your highest-impact skill and evidence gaps."
        )

        return RoadmapResponse(
            summary=summary,
            roadmap=final_steps,
            gap_summary=gap_summary_text,
        )

    def _determine_priority(
        self,
        is_required: bool,
        is_partial: bool,
        has_unmet_prereqs: bool,
    ) -> RoadmapPriority:
        """Assigns structured priority based on requirement criticality and evidence status."""
        if is_required:
            if not is_partial:
                return RoadmapPriority.CRITICAL if has_unmet_prereqs else RoadmapPriority.HIGH
            return RoadmapPriority.MEDIUM
        else:
            return RoadmapPriority.MEDIUM if not is_partial else RoadmapPriority.LOW

    def _format_why_it_matters(self, gap: GapAnalysisItem, is_required: bool) -> str:
        """Provides an explainable justification for why this skill must be developed."""
        req_type = "mandatory requirement" if is_required else "preferred qualification"
        if gap.job_evidence:
            return f"Listed as a {req_type}: \"{gap.job_evidence}\""
        return f"Explicitly listed as a {req_type} in the target job description."

    def _get_skill_definition(self, skill_name: str) -> SkillDefinition:
        """Retrieves or synthesizes a skill definition from the knowledge base."""
        if skill_name in SKILL_KNOWLEDGE_BASE:
            return SKILL_KNOWLEDGE_BASE[skill_name]

        # Generic fallback for skills not yet in curated knowledge base
        return SkillDefinition(
            name=skill_name,
            category="Domain Specific Skills",
            prerequisites=[],
            related_skills=[],
            learning_topics=[f"{skill_name} core architecture", f"Production best practices for {skill_name}"],
            practical_projects=[f"Develop a portfolio application integrating {skill_name}."],
            deliverables=[f"Documented implementation of {skill_name} on GitHub."],
            estimated_hours=20,
        )

    def _order_roadmap(
        self,
        skills: List[str],
        steps_map: Dict[str, RoadmapStep],
    ) -> List[str]:
        """
        Orders skills respecting topological dependency order, while giving precedence
        to higher priority categories (Critical -> High -> Medium -> Low).
        """
        # Deduplicate while preserving sequence
        seen = set()
        unique_skills = []
        for s in skills:
            if s not in seen and s in steps_map:
                seen.add(s)
                unique_skills.append(s)

        # Apply topological sort to ensure prerequisites come before dependents
        topo_sorted = self.dependency_graph.get_topological_sort(unique_skills)

        # Stable sort prioritizing earlier prerequisite steps and higher urgency
        priority_weight = {
            RoadmapPriority.CRITICAL: 0,
            RoadmapPriority.HIGH: 1,
            RoadmapPriority.MEDIUM: 2,
            RoadmapPriority.LOW: 3,
        }

        # Prerequisites must always precede their dependents regardless of priority
        return topo_sorted
