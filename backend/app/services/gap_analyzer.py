"""
Career Gap Analyzer Service.

Consumes intelligent skill matching results (Milestone 3) and applies transparent,
evidence-grounded heuristic rules to classify requirements:
1. Matched: Direct exact or normalized skill match with supporting contextual or listed evidence.
2. Partially Demonstrated: Semantic similarity or related concept exists, or skill is listed without
   measurable implementation details / professional work context.
3. Not Demonstrated: No supporting resume evidence found.

Computes explainable, non-misleading coverage scores for required, preferred, and overall criteria.
"""

import logging
from typing import List, Optional, Tuple

from app.core.config import settings
from app.schemas.gap_analysis import (
    CoverageBreakdown,
    GapAnalysisItem,
    GapAnalysisResponse,
    OverallCoverage,
    RequirementClassification,
    RequirementType,
)
from app.schemas.job import ParsedJobDescription
from app.schemas.matching import MatchMethod, SkillMatchItem, SkillMatchingResponse
from app.schemas.parsed_resume import ParsedResume
from app.services.skill_matcher import SkillMatcherService

logger = logging.getLogger("careerlens.gap_analyzer")


class GapAnalyzerService:
    """Evaluates candidate qualifications against job requirements and computes explainable coverage."""

    def __init__(
        self,
        skill_matcher_service: Optional[SkillMatcherService] = None,
        weight_matched: Optional[float] = None,
        weight_partial: Optional[float] = None,
        weight_not_demonstrated: Optional[float] = None,
        req_weight: Optional[float] = None,
        pref_weight: Optional[float] = None,
    ):
        self.skill_matcher = skill_matcher_service or SkillMatcherService()
        self.weight_matched = (
            weight_matched if weight_matched is not None else settings.SCORE_WEIGHT_MATCHED
        )
        self.weight_partial = (
            weight_partial if weight_partial is not None else settings.SCORE_WEIGHT_PARTIAL
        )
        self.weight_not_demonstrated = (
            weight_not_demonstrated
            if weight_not_demonstrated is not None
            else settings.SCORE_WEIGHT_NOT_DEMONSTRATED
        )
        self.req_weight = (
            req_weight if req_weight is not None else settings.OVERALL_REQUIRED_WEIGHT
        )
        self.pref_weight = (
            pref_weight if pref_weight is not None else settings.OVERALL_PREFERRED_WEIGHT
        )

    def analyze_gaps(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription,
    ) -> GapAnalysisResponse:
        """
        Executes skill matching (M3) and generates an explainable career gap analysis report.
        """
        # 1. Execute matching
        matching_response = self.skill_matcher.match_skills(resume, job_description)

        # 2. Evaluate required requirements
        required_items: List[GapAnalysisItem] = [
            self._classify_match_item(item, RequirementType.REQUIRED, resume)
            for item in matching_response.required_matches
        ]

        # 3. Evaluate preferred requirements
        preferred_items: List[GapAnalysisItem] = [
            self._classify_match_item(item, RequirementType.PREFERRED, resume)
            for item in matching_response.preferred_matches
        ]

        all_items = required_items + preferred_items

        # 4. Partition by classification for quick filtering
        matched_list = [i for i in all_items if i.classification == RequirementClassification.MATCHED]
        partial_list = [i for i in all_items if i.classification == RequirementClassification.PARTIALLY_DEMONSTRATED]
        not_dem_list = [i for i in all_items if i.classification == RequirementClassification.NOT_DEMONSTRATED]

        # 5. Compute coverage scores
        req_coverage = self._compute_category_coverage(required_items, "Required Requirements")
        pref_coverage = self._compute_category_coverage(preferred_items, "Preferred Requirements")
        overall_cov = self._compute_overall_coverage(req_coverage, pref_coverage)

        return GapAnalysisResponse(
            results=all_items,
            matched_requirements=matched_list,
            partially_demonstrated_requirements=partial_list,
            not_demonstrated_requirements=not_dem_list,
            required_coverage=req_coverage,
            preferred_coverage=pref_coverage,
            overall_coverage=overall_cov,
        )

    def _classify_match_item(
        self,
        item: SkillMatchItem,
        req_type: RequirementType,
        resume: ParsedResume,
    ) -> GapAnalysisItem:
        """
        Applies transparent rules to assign Matched, Partially Demonstrated, or Not Demonstrated.
        """
        req_name = item.job_requirement
        evidence = item.resume_evidence

        # Rule 1: No match identified
        if not item.is_matched or item.match_method == MatchMethod.NONE:
            return GapAnalysisItem(
                requirement=req_name,
                requirement_type=req_type,
                classification=RequirementClassification.NOT_DEMONSTRATED,
                match_method=MatchMethod.NONE,
                similarity_score=item.similarity_score,
                resume_evidence=None,
                job_evidence=item.job_evidence,
                explanation=f"The resume does not provide identifiable evidence for '{req_name}'. Highest semantic similarity found was {item.similarity_score:.2f}, which falls below the threshold.",
                suggested_improvement=f"Gain practical project or work experience with {req_name} and add a concrete achievement bullet to your resume.",
            )

        # Rule 2: Exact or Normalized Match
        if item.match_method in (MatchMethod.EXACT, MatchMethod.NORMALIZED):
            # Check whether evidence is rich contextual work/project experience vs. merely a keyword listed in skills
            is_contextual = evidence and (
                evidence.startswith("[") or " at " in evidence or len(evidence) > 40
            )

            if is_contextual:
                method_name = "exact string match" if item.match_method == MatchMethod.EXACT else "normalized taxonomy match"
                return GapAnalysisItem(
                    requirement=req_name,
                    requirement_type=req_type,
                    classification=RequirementClassification.MATCHED,
                    match_method=item.match_method,
                    similarity_score=item.similarity_score,
                    resume_evidence=evidence,
                    job_evidence=item.job_evidence,
                    explanation=f"Strong direct evidence identified via {method_name} with contextual implementation details.",
                    suggested_improvement=None,
                )
            else:
                # Skill is listed as a keyword, but lacks substantive description or outcome
                return GapAnalysisItem(
                    requirement=req_name,
                    requirement_type=req_type,
                    classification=RequirementClassification.PARTIALLY_DEMONSTRATED,
                    match_method=item.match_method,
                    similarity_score=item.similarity_score,
                    resume_evidence=evidence,
                    job_evidence=item.job_evidence,
                    explanation=f"'{req_name}' is explicitly listed on the resume, but lacks contextual bullet points demonstrating practical production implementation or project outcomes.",
                    suggested_improvement=f"Add an experience or project bullet detailing how you utilized {req_name} with measurable results.",
                )

        # Rule 3: Semantic Match
        if item.match_method == MatchMethod.SEMANTIC:
            # Semantic similarity alone denotes related concept rather than definitive proof of deep proficiency
            return GapAnalysisItem(
                requirement=req_name,
                requirement_type=req_type,
                classification=RequirementClassification.PARTIALLY_DEMONSTRATED,
                match_method=MatchMethod.SEMANTIC,
                similarity_score=item.similarity_score,
                resume_evidence=evidence,
                job_evidence=item.job_evidence,
                explanation=(
                    f"Related experience identified semantically with {item.similarity_score:.2f} similarity "
                    f"('{item.matched_resume_skill}'). While relevant experience is demonstrated, the resume does not directly verify full proficiency with '{req_name}'."
                ),
                suggested_improvement=f"Explicitly clarify your direct hands-on experience with {req_name} to turn this conceptual match into verified evidence.",
            )

        # Default fallback
        return GapAnalysisItem(
            requirement=req_name,
            requirement_type=req_type,
            classification=RequirementClassification.NOT_DEMONSTRATED,
            match_method=item.match_method,
            similarity_score=item.similarity_score,
            resume_evidence=None,
            job_evidence=item.job_evidence,
            explanation=f"Insufficient evidence found to demonstrate '{req_name}'.",
            suggested_improvement=f"Demonstrate experience with {req_name} through a practical project.",
        )

    def _compute_category_coverage(
        self,
        items: List[GapAnalysisItem],
        category_name: str,
    ) -> CoverageBreakdown:
        """
        Calculates category coverage score:
        Coverage = ( (matched * 1.0) + (partial * 0.5) + (not_dem * 0.0) ) / total * 100
        """
        total = len(items)
        if total == 0:
            return CoverageBreakdown(
                total_count=0,
                matched_count=0,
                partial_count=0,
                not_demonstrated_count=0,
                coverage_score=None,
                calculation_explanation=f"No {category_name.lower()} were present in the job description to evaluate.",
            )

        matched = sum(1 for i in items if i.classification == RequirementClassification.MATCHED)
        partial = sum(1 for i in items if i.classification == RequirementClassification.PARTIALLY_DEMONSTRATED)
        not_dem = sum(1 for i in items if i.classification == RequirementClassification.NOT_DEMONSTRATED)

        weighted_sum = (matched * self.weight_matched) + (partial * self.weight_partial) + (not_dem * self.weight_not_demonstrated)
        score = round((weighted_sum / total) * 100.0, 2)

        explanation = (
            f"Coverage ({score:.1f}%) = [({matched} matched × {self.weight_matched}) + "
            f"({partial} partial × {self.weight_partial}) + ({not_dem} not demonstrated × {self.weight_not_demonstrated})] / {total} total requirements × 100"
        )

        return CoverageBreakdown(
            total_count=total,
            matched_count=matched,
            partial_count=partial,
            not_demonstrated_count=not_dem,
            coverage_score=score,
            calculation_explanation=explanation,
        )

    def _compute_overall_coverage(
        self,
        req_cov: CoverageBreakdown,
        pref_cov: CoverageBreakdown,
    ) -> OverallCoverage:
        """
        Computes overall weighted requirement coverage.
        Default: 80% required + 20% preferred.
        If no preferred criteria exist, required coverage represents 100% of the score.
        If no criteria exist at all, returns null.
        """
        req_score = req_cov.coverage_score
        pref_score = pref_cov.coverage_score

        # Case 1: Neither exists
        if req_score is None and pref_score is None:
            return OverallCoverage(
                overall_score=None,
                required_weight_percent=self.req_weight * 100.0,
                preferred_weight_percent=self.pref_weight * 100.0,
                explanation="No required or preferred skills were identified in the job description.",
            )

        # Case 2: Only required skills exist
        if pref_score is None:
            return OverallCoverage(
                overall_score=req_score,
                required_weight_percent=100.0,
                preferred_weight_percent=0.0,
                explanation=f"Overall coverage is based 100% on required requirements ({req_score:.1f}%) because no preferred requirements were specified.",
            )

        # Case 3: Only preferred skills exist
        if req_score is None:
            return OverallCoverage(
                overall_score=pref_score,
                required_weight_percent=0.0,
                preferred_weight_percent=100.0,
                explanation=f"Overall coverage is based 100% on preferred requirements ({pref_score:.1f}%) because no mandatory requirements were specified.",
            )

        # Case 4: Both required and preferred exist -> weighted average
        overall = round((req_score * self.req_weight) + (pref_score * self.pref_weight), 2)
        req_pct = round(self.req_weight * 100.0, 1)
        pref_pct = round(self.pref_weight * 100.0, 1)

        explanation = (
            f"Overall coverage ({overall:.1f}%) = (Required score {req_score:.1f}% × {self.req_weight}) + "
            f"(Preferred score {pref_score:.1f}% × {self.pref_weight})"
        )

        return OverallCoverage(
            overall_score=overall,
            required_weight_percent=req_pct,
            preferred_weight_percent=pref_pct,
            explanation=explanation,
        )
