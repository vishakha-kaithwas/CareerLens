"""
Job Description Parser Service.

Extracts structured requirements from raw job descriptions:
- Inferred Job Title
- Required Skills (mandatory requirements)
- Preferred Skills (nice-to-have requirements)
- Tools & Technologies
- Soft Skills
- Experience Criteria (e.g. "5+ years of Python")
- Education Requirements (e.g. "Bachelor's degree in CS")
- Responsibilities / Key Duties

Preserves raw_text for verification and explainability.
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple
import spacy

from app.schemas.job import ParsedJobDescription
from app.services.skill_extractor import SkillExtractorService

logger = logging.getLogger("careerlens.job_parser")

# Section header patterns in job descriptions
REQUIRED_HEADERS = re.compile(
    r"^(?:requirements|what\s+you(?:'ll)?\s+need|minimum\s+qualifications|basic\s+qualifications|"
    r"what\s+we(?:'re)?\s+looking\s+for|must\s+haves?|required\s+skills)\b",
    re.IGNORECASE,
)
PREFERRED_HEADERS = re.compile(
    r"^(?:preferred\s+qualifications|nice\s+to\s+haves?|bonus\s+points|preferred\s+skills|"
    r"what\s+gives\s+you\s+an\s+edge|plus|desired\s+skills)\b",
    re.IGNORECASE,
)
RESPONSIBILITIES_HEADERS = re.compile(
    r"^(?:responsibilities|what\s+you(?:'ll)?\s+do|the\s+role|role\s+responsibilities|"
    r"key\s+duties|day\s+to\s+day)\b",
    re.IGNORECASE,
)

# Experience regex patterns (e.g. "3+ years", "5-7 years", "at least 4 years")
EXPERIENCE_PATTERN = re.compile(
    r"(?:(?:at\s+least|minimum|up\s+to|\+)?\s*\d+\s*(?:-|to|\+)?\s*\d*\s*years?(?:\s+of)?(?:\s+[a-zA-Z0-9\s,]+){1,5})",
    re.IGNORECASE,
)

# Education criteria pattern
EDUCATION_PATTERN = re.compile(
    r"(?:(?:Bachelor(?:'s)?|Master(?:'s)?|Ph\.D\.|B\.S\.|M\.S\.|B\.A\.|Degree)\s*(?:in\s+[A-Za-z\s,]+)?(?:\s*or\s+equivalent)?)",
    re.IGNORECASE,
)


class JobDescriptionParserService:
    """Parses raw job descriptions into structured requirements."""

    def __init__(self):
        self.skill_extractor = SkillExtractorService()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            logger.warning("en_core_web_sm not found, loading blank English model")
            self.nlp = spacy.blank("en")

    def parse(self, text: str) -> ParsedJobDescription:
        """Parses job description text into structured Pydantic model."""
        if not text or not text.strip():
            return ParsedJobDescription(raw_text=text or "")

        lines = [l.strip() for l in text.splitlines() if l.strip()]

        # 1. Title inference
        title = self._infer_title(lines)

        # 2. Section segmentation
        sections = self._segment_sections(lines)

        req_text = sections.get("required", "")
        pref_text = sections.get("preferred", "")
        resp_text = sections.get("responsibilities", "")

        # 3. Skills extraction
        # Technical skills
        all_tech = set(self.skill_extractor.extract_technical_skills(text))
        
        # Skills in responsibilities and requirements are required unless explicitly in preferred
        core_duty_text = (req_text + "\n" + resp_text).strip()
        required_tech = set(self.skill_extractor.extract_technical_skills(core_duty_text)) if core_duty_text else all_tech
        preferred_tech = set(self.skill_extractor.extract_technical_skills(pref_text)) if pref_text else set()

        # Any tech in preferred should be removed from strictly required
        required_tech = required_tech - preferred_tech

        # Soft skills
        soft_skills = self.skill_extractor.extract_soft_skills(text)

        # 4. Responsibilities
        responsibilities = self._extract_bullet_items(resp_text)

        # 5. Experience requirements
        experience_requirements = self._extract_experience_requirements(text)

        # 6. Education requirements
        education_requirements = self._extract_education_requirements(text)

        return ParsedJobDescription(
            title=title,
            required_skills=sorted(list(required_tech)),
            preferred_skills=sorted(list(preferred_tech)),
            tools_and_technologies=sorted(list(all_tech)),
            soft_skills=soft_skills,
            experience_requirements=experience_requirements,
            education_requirements=education_requirements,
            responsibilities=responsibilities,
            raw_text=text,
        )

    def _infer_title(self, lines: List[str]) -> Optional[str]:
        """Infers the job title from header lines or common phrasing."""
        if not lines:
            return None

        # Often the very first line is the job title e.g. "Senior Software Engineer"
        first_line = lines[0]
        # Strip prefixes like "Job Title:", "Role:"
        clean_first = re.sub(r"^(?:job\s+title|role|position):\s*", "", first_line, flags=re.IGNORECASE).strip()
        if len(clean_first.split()) <= 6 and not any(clean_first.lower().startswith(h) for h in ["about", "we are", "company"]):
            return clean_first

        # Look for title markers
        for line in lines[:5]:
            match = re.search(r"^(?:job\s+title|role|position):\s*(.+)$", line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _segment_sections(self, lines: List[str]) -> Dict[str, str]:
        """Segments lines into required, preferred, and responsibilities blocks."""
        sections: Dict[str, List[str]] = {"required": [], "preferred": [], "responsibilities": [], "other": []}
        current = "other"

        for line in lines:
            clean = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", line).strip()
            if len(clean.split()) <= 6:
                if PREFERRED_HEADERS.match(clean):
                    current = "preferred"
                    continue
                elif REQUIRED_HEADERS.match(clean):
                    current = "required"
                    continue
                elif RESPONSIBILITIES_HEADERS.match(clean):
                    current = "responsibilities"
                    continue

            sections[current].append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items()}

    def _extract_bullet_items(self, section_text: str) -> List[str]:
        """Extracts bullet lines or distinct sentences from a section."""
        if not section_text:
            return []
        items = []
        for line in section_text.splitlines():
            line = line.strip()
            if not line:
                continue
            clean = re.sub(r"^[•\-\*]\s*", "", line).strip()
            if len(clean) > 15:
                items.append(clean)
        return items

    def _extract_experience_requirements(self, text: str) -> List[str]:
        """Finds explicit experience statements (e.g. '5+ years of experience with Python')."""
        matches = EXPERIENCE_PATTERN.findall(text)
        cleaned = []
        for m in matches:
            m_clean = m.strip()
            if len(m_clean) > 8 and m_clean not in cleaned:
                cleaned.append(m_clean)
        return cleaned[:5]  # Cap at top 5 most specific

    def _extract_education_requirements(self, text: str) -> List[str]:
        """Finds explicit education criteria."""
        matches = EDUCATION_PATTERN.findall(text)
        cleaned = []
        for m in matches:
            m_clean = m.strip()
            if len(m_clean) > 5 and m_clean not in cleaned:
                cleaned.append(m_clean)
        return cleaned[:3]
