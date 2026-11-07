"""
Resume Parser Service.

Extracts structured sections from clean PDF text:
- Personal Contact Information (Name, Email, Phone, LinkedIn, GitHub, Portfolio)
- Professional Summary / Objective
- Skills (extracted and normalized via taxonomy)
- Work Experience & Internships
- Education & Degrees
- Projects (segmented into discrete project records)
- Certifications
- Extracurricular Activities / Leadership / Competitions

Preserves raw_text on every entry for downstream explainability and evidence verification.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
import spacy

from app.schemas.parsed_resume import (
    CertificationEntry,
    ContactInfo,
    EducationEntry,
    ExperienceEntry,
    ExtracurricularEntry,
    ParsedResume,
    ProjectEntry,
)
from app.services.skill_extractor import SkillExtractorService

logger = logging.getLogger("careerlens.resume_parser")

# Standard section header regexes
SECTION_PATTERNS = {
    "summary": re.compile(
        r"^(?:professional\s+summary|career\s+summary|summary|profile|about\s+me|objective)\b",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^(?:work\s+experience|professional\s+experience|employment\s+history|experience|internships?)\b",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"^(?:education|academic\s+background|qualifications|academic\s+history)\b",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"^(?:technical\s+skills|core\s+competencies|technologies|skills\s+&\s+tools|skills)\b",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"^(?:academic\s+projects|personal\s+projects|key\s+projects|technical\s+projects|projects)\b",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"^(?:certifications?|licenses?|credentials?|certificates?)\b",
        re.IGNORECASE,
    ),
    "extracurriculars": re.compile(
        r"^(?:extracurricular\s+activities|extracurriculars?|leadership\s+&\s+activities|leadership|activities|volunteer(?:ing)?|achievements?|hackathons?)\b",
        re.IGNORECASE,
    ),
}

# Regexes for contact extraction
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
LINKEDIN_PATTERN = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([A-Za-z0-9_-]+)\/?",
    re.IGNORECASE,
)
GITHUB_PATTERN = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?github\.com\/([A-Za-z0-9_-]+)\/?",
    re.IGNORECASE,
)
DATE_RANGE_PATTERN = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{4})"
    r"\s*(?:–|-|to)\s*(?:Present|Current|\d{4}|Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
    r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
    r"Nov(?:ember)?|Dec(?:ember)?)\b",
    re.IGNORECASE,
)


class ResumeParserService:
    """Service to parse extracted resume text into structured Pydantic models."""

    def __init__(self):
        self.skill_extractor = SkillExtractorService()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            logger.warning("en_core_web_sm not found, loading blank English model")
            self.nlp = spacy.blank("en")

    def parse(self, text: str) -> ParsedResume:
        """Parses full resume text into structured sections and entities."""
        if not text or not text.strip():
            return ParsedResume(raw_text=text or "")

        lines = text.splitlines()

        # 1. Segment text into labeled sections
        sections, header_lines = self._segment_sections(lines)

        # 2. Extract Contact Information from header or full text
        contact = self._extract_contact_info(header_lines, text)

        # 3. Extract Summary
        summary = sections.get("summary")

        # 4. Extract Skills (from explicit skills section + full text)
        skills_text = (sections.get("skills") or "") + "\n" + text
        skills = self.skill_extractor.extract_technical_skills(skills_text)

        # 5. Extract Experience
        experience = self._parse_experience(sections.get("experience"))

        # 6. Extract Education
        education = self._parse_education(sections.get("education"))

        # 7. Extract Projects (discrete entries)
        projects = self._parse_projects(sections.get("projects"))

        # 8. Extract Certifications
        certifications = self._parse_certifications(sections.get("certifications"))

        # 9. Extract Extracurriculars / Leadership
        extracurriculars = self._parse_extracurriculars(sections.get("extracurriculars"))

        return ParsedResume(
            contact=contact,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=certifications,
            extracurriculars=extracurriculars,
            raw_text=text,
        )

    def _segment_sections(self, lines: List[str]) -> Tuple[Dict[str, str], List[str]]:
        """Segments lines into named sections based on header patterns."""
        sections: Dict[str, List[str]] = {}
        header_lines: List[str] = []
        current_section: Optional[str] = None

        for line in lines:
            line_str = line.strip()
            matched_section = None
            if line_str and len(line_str.split()) <= 6:
                clean_line = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", line_str).strip()
                for sec_name, pattern in SECTION_PATTERNS.items():
                    if pattern.match(clean_line):
                        matched_section = sec_name
                        break

            if matched_section:
                current_section = matched_section
                if current_section not in sections:
                    sections[current_section] = []
            elif current_section is None:
                if line_str:
                    header_lines.append(line_str)
            else:
                sections[current_section].append(line_str)

        joined_sections = {sec: "\n".join(sec_lines).strip() for sec, sec_lines in sections.items()}
        return joined_sections, header_lines

    def _extract_contact_info(self, header_lines: List[str], full_text: str) -> ContactInfo:
        """Extracts candidate contact details using regex and spaCy NER."""
        header_text = "\n".join(header_lines) if header_lines else full_text[:1000]

        name = None
        for line in header_lines[:5]:
            clean = re.sub(r"[|\-•,].*", "", line).strip()
            if re.match(r"^Page\s+\d+", clean, re.IGNORECASE):
                continue
            if clean and len(clean.split()) in (2, 3, 4) and not any(char in clean for char in "@/:0123456789"):
                name = clean
                break

        if not name:
            doc = self.nlp(header_text)
            for ent in doc.ents:
                if ent.label_ == "PERSON" and len(ent.text.split()) in (2, 3):
                    if not re.match(r"^Page\s+\d+", ent.text, re.IGNORECASE):
                        name = ent.text.strip()
                        break

        email_match = EMAIL_PATTERN.search(full_text)
        email = email_match.group(0) if email_match else None

        phone_match = PHONE_PATTERN.search(full_text)
        phone = phone_match.group(0) if phone_match else None

        li_match = LINKEDIN_PATTERN.search(full_text)
        linkedin = li_match.group(0) if li_match else None

        gh_match = GITHUB_PATTERN.search(full_text)
        github = gh_match.group(0) if gh_match else None

        location = None
        for line in header_lines:
            if re.search(r"\b[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\b|\b[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z]+\b", line):
                loc_match = re.search(r"([A-Za-z\s]+,\s*[A-Za-z\s]+)", line)
                if loc_match:
                    location = loc_match.group(1).strip()
                    break

        return ContactInfo(
            name=name,
            email=email,
            phone=phone,
            location=location,
            linkedin=linkedin,
            github=github,
        )

    def _parse_experience(self, exp_text: Optional[str]) -> List[ExperienceEntry]:
        """Splits experience section into discrete employment entries."""
        if not exp_text:
            return []

        entries: List[ExperienceEntry] = []
        blocks = re.split(r"\n\s*\n", exp_text)

        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            first_line = lines[0]
            dates_match = DATE_RANGE_PATTERN.search(block)
            dates = dates_match.group(0) if dates_match else None

            title = None
            company = None
            if " at " in first_line:
                parts = first_line.split(" at ", 1)
                title, company = parts[0].strip(), parts[1].strip()
            elif " - " in first_line or " | " in first_line:
                parts = re.split(r"\s+[-|]\s+", first_line, maxsplit=1)
                title, company = parts[0].strip(), parts[1].strip()
            else:
                title = first_line

            bullets = [
                re.sub(r"^[•\-\*]\s*", "", l)
                for l in lines[1:]
                if l.startswith(("•", "-", "*")) or len(l) > 20
            ]

            entries.append(
                ExperienceEntry(
                    title=title,
                    company=company,
                    dates=dates,
                    responsibilities=bullets,
                    raw_text=block,
                )
            )

        return entries

    def _parse_education(self, edu_text: Optional[str]) -> List[EducationEntry]:
        """Extracts education records and degrees."""
        if not edu_text:
            return []

        entries: List[EducationEntry] = []
        blocks = re.split(r"\n\s*\n", edu_text) if "\n\n" in edu_text else [edu_text]

        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            institution = None
            degree = None
            dates = None

            dates_match = DATE_RANGE_PATTERN.search(block) or re.search(r"\b(19\d{2}|20\d{2})\b", block)
            if dates_match:
                dates = dates_match.group(0)

            deg_pattern = re.compile(
                r"\b(Bachelor(?:'s)?|Master(?:'s)?|B\.S\.|M\.S\.|B\.A\.|M\.A\.|Ph\.D\.|B\.E\.|B\.Tech|Associate)\b[^\n,]*",
                re.IGNORECASE,
            )
            for line in lines:
                deg_match = deg_pattern.search(line)
                if deg_match:
                    degree = deg_match.group(0).strip()
                elif any(word in line.lower() for word in ["university", "college", "institute", "school"]):
                    institution = line.strip()

            if not institution and lines:
                institution = lines[0]

            entries.append(
                EducationEntry(
                    institution=institution,
                    degree=degree,
                    dates=dates,
                    raw_text=block,
                )
            )

        return entries

    def _parse_projects(self, proj_text: Optional[str]) -> List[ProjectEntry]:
        """
        Extracts individual projects as separate records.
        Handles both double-newline separated projects and inline bulleted project titles.
        """
        if not proj_text:
            return []

        raw_blocks = [b.strip() for b in re.split(r"\n\s*\n", proj_text) if b.strip()]
        
        # If single giant block, attempt splitting by project header line patterns
        # e.g., lines ending with technologies or not starting with bullet
        if len(raw_blocks) <= 1:
            raw_lines = [l.strip() for l in proj_text.splitlines() if l.strip()]
            reconstructed_blocks: List[List[str]] = []
            curr_block: List[str] = []

            for line in raw_lines:
                # A project header candidate is a non-bullet line with few words or containing '|'
                is_bullet = line.startswith(("•", "-", "*"))
                is_header_candidate = not is_bullet and (
                    "|" in line or
                    re.search(r"\b(?:Python|FastAPI|React|ML|Flask|Django|Java|C\+\+|SQL|Docker)\b", line) or
                    len(line.split()) <= 6
                )

                if is_header_candidate and curr_block:
                    reconstructed_blocks.append(curr_block)
                    curr_block = [line]
                else:
                    curr_block.append(line)

            if curr_block:
                reconstructed_blocks.append(curr_block)

            blocks = ["\n".join(b) for b in reconstructed_blocks]
        else:
            blocks = raw_blocks

        entries: List[ProjectEntry] = []
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            first_line = lines[0]
            # Strip bullet marker if title was accidentally bulleted
            first_line_clean = re.sub(r"^[•\-\*]\s*", "", first_line)

            title = first_line_clean
            if "|" in first_line_clean:
                parts = first_line_clean.split("|", 1)
                title = parts[0].strip()
            elif " - " in first_line_clean and len(first_line_clean.split(" - ")[0].split()) <= 5:
                parts = first_line_clean.split(" - ", 1)
                title = parts[0].strip()

            technologies = self.skill_extractor.extract_technical_skills(block)
            desc_lines = [re.sub(r"^[•\-\*]\s*", "", l) for l in lines[1:]]

            entries.append(
                ProjectEntry(
                    title=title,
                    description="\n".join(desc_lines) if desc_lines else None,
                    technologies=technologies,
                    raw_text=block,
                )
            )

        return entries

    def _parse_certifications(self, cert_text: Optional[str]) -> List[CertificationEntry]:
        """Extracts certifications and licenses."""
        if not cert_text:
            return []

        entries: List[CertificationEntry] = []
        lines = [l.strip() for l in cert_text.splitlines() if l.strip()]

        for line in lines:
            clean = re.sub(r"^[•\-\*]\s*", "", line)
            issuer = None
            if " - " in clean:
                parts = clean.split(" - ", 1)
                name, issuer = parts[0].strip(), parts[1].strip()
            elif " by " in clean:
                parts = clean.split(" by ", 1)
                name, issuer = parts[0].strip(), parts[1].strip()
            else:
                name = clean

            entries.append(CertificationEntry(name=name, issuer=issuer, raw_text=line))

        return entries

    def _parse_extracurriculars(self, extra_text: Optional[str]) -> List[ExtracurricularEntry]:
        """Extracts extracurricular activities, student clubs, hackathons, and leadership."""
        if not extra_text:
            return []

        entries: List[ExtracurricularEntry] = []
        blocks = [b.strip() for b in re.split(r"\n\s*\n", extra_text) if b.strip()]

        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            first_line = re.sub(r"^[•\-\*]\s*", "", lines[0])
            title = first_line
            role_org = None

            if " - " in first_line:
                parts = first_line.split(" - ", 1)
                title, role_org = parts[0].strip(), parts[1].strip()
            elif " | " in first_line:
                parts = first_line.split(" | ", 1)
                title, role_org = parts[0].strip(), parts[1].strip()
            elif " at " in first_line:
                parts = first_line.split(" at ", 1)
                role_org, title = parts[0].strip(), parts[1].strip()

            desc_lines = [re.sub(r"^[•\-\*]\s*", "", l) for l in lines[1:]]
            description = "\n".join(desc_lines) if desc_lines else None

            entries.append(
                ExtracurricularEntry(
                    title=title,
                    role_or_organization=role_org,
                    description=description,
                    raw_text=block,
                )
            )

        return entries
