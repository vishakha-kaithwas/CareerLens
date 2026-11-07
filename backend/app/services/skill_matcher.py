"""
Intelligent Skill Matching Service.

Evaluates job requirements against candidate resume data across three strategies:
1. Exact Matching: Case-insensitive identical skill strings.
2. Normalized Matching: Maps synonyms and aliases via app.ml.skill_taxonomy.
3. Semantic Matching: Generates dense vector embeddings via EmbeddingEngine
   and compares cosine similarity against resume skills and experience bullet evidence.

Distinction Rules:
- Enforces strict false-positive suppression for commonly confused but distinct technologies:
  (e.g., Python != PyTorch, Java != JavaScript, SQL != NoSQL).
"""

import logging
import re
from typing import Dict, List, Optional, Set, Tuple

from app.core.config import settings
from app.ml.embeddings import EmbeddingEngine
from app.ml.skill_taxonomy import ALIAS_TO_CANONICAL
from app.schemas.job import ParsedJobDescription
from app.schemas.matching import (
    MatchMethod,
    SkillMatchItem,
    SkillMatchingResponse,
)
from app.schemas.parsed_resume import ParsedResume

logger = logging.getLogger("careerlens.skill_matcher")

# Distinct technology pairs that must NEVER be matched semantically as equivalent
DISTINCT_TECH_PAIRS: Set[Tuple[str, str]] = {
    ("python", "pytorch"),
    ("pytorch", "python"),
    ("java", "javascript"),
    ("javascript", "java"),
    ("sql", "nosql"),
    ("nosql", "sql"),
    ("c", "c++"),
    ("c++", "c"),
    ("c", "c#"),
    ("c#", "c"),
}


class SkillMatcherService:
    """Service orchestrating exact, normalized, and semantic skill matching."""

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        similarity_threshold: Optional[float] = None,
    ):
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.similarity_threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else settings.SEMANTIC_SIMILARITY_THRESHOLD
        )

    def match_skills(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription,
    ) -> SkillMatchingResponse:
        """
        Matches mandatory and preferred job skills against candidate resume evidence.
        """
        # 1. Collect and index all resume evidence snippets and normalized skills
        resume_skills_canonical = {s.lower(): s for s in resume.skills}
        resume_evidence_corpus = self._build_resume_evidence_corpus(resume)

        # 2. Match Required Skills
        required_matches = [
            self._evaluate_requirement(req, is_required=True, resume_skills=resume_skills_canonical, resume_evidence=resume_evidence_corpus, job_raw=job_description.raw_text)
            for req in job_description.required_skills
        ]

        # 3. Match Preferred Skills
        preferred_matches = [
            self._evaluate_requirement(pref, is_required=False, resume_skills=resume_skills_canonical, resume_evidence=resume_evidence_corpus, job_raw=job_description.raw_text)
            for pref in job_description.preferred_skills
        ]

        total_req = len(required_matches)
        total_pref = len(preferred_matches)
        matched_req = sum(1 for m in required_matches if m.is_matched)
        matched_pref = sum(1 for m in preferred_matches if m.is_matched)

        return SkillMatchingResponse(
            required_matches=required_matches,
            preferred_matches=preferred_matches,
            total_required_count=total_req,
            total_preferred_count=total_pref,
            matched_required_count=matched_req,
            matched_preferred_count=matched_pref,
        )

    def _evaluate_requirement(
        self,
        requirement: str,
        is_required: bool,
        resume_skills: Dict[str, str],
        resume_evidence: List[Tuple[str, str]],  # (clean_text, original_snippet)
        job_raw: str,
    ) -> SkillMatchItem:
        """Evaluates a single requirement through exact -> normalized -> semantic strategies."""
        req_clean = requirement.strip()
        req_lower = req_clean.lower()
        job_evidence_snippet = self._find_job_evidence(req_clean, job_raw)

        # Strategy A: Exact Match
        if req_lower in resume_skills:
            matched_skill = resume_skills[req_lower]
            evidence = self._find_resume_evidence_for_skill(matched_skill, resume_evidence)
            return SkillMatchItem(
                job_requirement=req_clean,
                is_required=is_required,
                is_matched=True,
                match_method=MatchMethod.EXACT,
                similarity_score=1.0,
                matched_resume_skill=matched_skill,
                resume_evidence=evidence or f"Explicit skill listed: {matched_skill}",
                job_evidence=job_evidence_snippet,
            )

        # Strategy B: Normalized / Taxonomy Match
        req_canonical = ALIAS_TO_CANONICAL.get(req_lower)
        if req_canonical:
            # Check if canonical name is in resume
            if req_canonical.lower() in resume_skills:
                matched_skill = resume_skills[req_canonical.lower()]
                evidence = self._find_resume_evidence_for_skill(matched_skill, resume_evidence)
                return SkillMatchItem(
                    job_requirement=req_clean,
                    is_required=is_required,
                    is_matched=True,
                    match_method=MatchMethod.NORMALIZED,
                    similarity_score=1.0,
                    matched_resume_skill=matched_skill,
                    resume_evidence=evidence or f"Normalized skill match via taxonomy: {matched_skill}",
                    job_evidence=job_evidence_snippet,
                )

        # Strategy C: Semantic Match using Sentence Embeddings
        best_match = self._find_best_semantic_match(req_clean, resume_evidence)

        if best_match and best_match["similarity"] >= self.similarity_threshold:
            # Distinct technology safety check
            matched_text = best_match["text"].lower()
            if self._is_distinct_technology_violation(req_lower, matched_text):
                logger.info(
                    "Suppressed semantic match between distinct technologies '%s' and '%s'",
                    req_clean,
                    best_match["text"],
                )
            else:
                return SkillMatchItem(
                    job_requirement=req_clean,
                    is_required=is_required,
                    is_matched=True,
                    match_method=MatchMethod.SEMANTIC,
                    similarity_score=round(best_match["similarity"], 4),
                    matched_resume_skill=best_match["text"][:80],
                    resume_evidence=best_match["original_snippet"],
                    job_evidence=job_evidence_snippet,
                )

        # Fallback: No Match Found
        highest_score = best_match["similarity"] if best_match else 0.0
        return SkillMatchItem(
            job_requirement=req_clean,
            is_required=is_required,
            is_matched=False,
            match_method=MatchMethod.NONE,
            similarity_score=round(highest_score, 4),
            matched_resume_skill=None,
            resume_evidence=None,
            job_evidence=job_evidence_snippet,
        )

    def _build_resume_evidence_corpus(self, resume: ParsedResume) -> List[Tuple[str, str]]:
        """Collects candidate skills, experience bullets, and project bullets as evidence items."""
        corpus: List[Tuple[str, str]] = []

        # Skills
        for skill in resume.skills:
            corpus.append((skill, f"Listed skill: {skill}"))

        # Summary
        if resume.summary:
            corpus.append((resume.summary, resume.summary))

        # Experience responsibilities
        for exp in resume.experience:
            for bullet in exp.responsibilities:
                if len(bullet) > 10:
                    corpus.append((bullet, f"[{exp.title or 'Experience'} at {exp.company or 'Company'}] {bullet}"))

        # Projects
        for proj in resume.projects:
            if proj.description:
                for line in proj.description.splitlines():
                    clean = line.strip()
                    if len(clean) > 10:
                        corpus.append((clean, f"[Project: {proj.title or 'Project'}] {clean}"))

        return corpus

    def _find_best_semantic_match(
        self,
        requirement: str,
        evidence_corpus: List[Tuple[str, str]],
    ) -> Optional[Dict]:
        """Encodes requirement and candidate snippets, computing cosine similarities."""
        if not evidence_corpus:
            return None

        clean_texts = [item[0] for item in evidence_corpus]
        # Generate embeddings
        req_emb = self.embedding_engine.encode([requirement], normalize=True)[0]
        corpus_embs = self.embedding_engine.encode(clean_texts, normalize=True)

        best_score = -1.0
        best_idx = -1

        for idx, emb in enumerate(corpus_embs):
            sim = self.embedding_engine.compute_cosine_similarity(req_emb, emb)
            if sim > best_score:
                best_score = sim
                best_idx = idx

        if best_idx >= 0:
            return {
                "similarity": best_score,
                "text": evidence_corpus[best_idx][0],
                "original_snippet": evidence_corpus[best_idx][1],
            }
        return None

    def _find_resume_evidence_for_skill(
        self,
        skill: str,
        evidence_corpus: List[Tuple[str, str]],
    ) -> Optional[str]:
        """Finds the most specific bullet point containing the matched skill."""
        skill_re = re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)
        for clean, original in evidence_corpus:
            # Prefer contextual bullets over just "Listed skill: X"
            if not original.startswith("Listed skill:") and skill_re.search(clean):
                return original

        for clean, original in evidence_corpus:
            if skill_re.search(clean):
                return original
        return None

    def _find_job_evidence(self, requirement: str, job_raw: str) -> Optional[str]:
        """Extracts the verbatim sentence or line in the job description referencing the requirement."""
        if not job_raw:
            return None
        req_re = re.compile(rf"\b{re.escape(requirement)}\b", re.IGNORECASE)
        for line in job_raw.splitlines():
            line_str = line.strip()
            if req_re.search(line_str) and len(line_str) > 10:
                return re.sub(r"^[•\-\*]\s*", "", line_str)
        return None

    def _is_distinct_technology_violation(self, req: str, evidence: str) -> bool:
        """
        Guards against semantic false positives between distinct technologies
        (e.g., matching 'PyTorch' bullet for a 'Python' requirement or vice versa).
        """
        for a, b in DISTINCT_TECH_PAIRS:
            # If the requirement mentions technology A
            if re.search(rf"\b{re.escape(a)}\b", req, re.IGNORECASE):
                # But the evidence mentions technology B while completely lacking technology A
                if re.search(rf"\b{re.escape(b)}\b", evidence, re.IGNORECASE) and not re.search(rf"\b{re.escape(a)}\b", evidence, re.IGNORECASE):
                    return True
        return False
