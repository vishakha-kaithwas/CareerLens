"""
Skill extraction service using exact alias matching and boundary regex.
Normalizes variants into canonical skill names using app.ml.skill_taxonomy.
"""

import re
from typing import List, Set, Tuple
from app.ml.skill_taxonomy import ALIAS_TO_CANONICAL, SOFT_ALIAS_TO_CANONICAL


class SkillExtractorService:
    """Extracts and normalizes technical and soft skills from arbitrary text."""

    def __init__(self):
        # Precompile regex word-boundary patterns for all taxonomy aliases
        # Sort by length descending so multi-word aliases (e.g. "spring boot") match before "spring"
        sorted_aliases = sorted(ALIAS_TO_CANONICAL.keys(), key=len, reverse=True)
        self.tech_patterns: List[Tuple[re.Pattern, str]] = []
        for alias in sorted_aliases:
            # Escape regex special characters like C++, C#, .NET
            escaped = re.escape(alias)
            # Use negative lookbehind and lookahead to avoid matching inside longer identifiers
            # Notice dot '.' is intentionally excluded from the lookahead so skills at the end of a sentence (e.g. "Python.") match correctly.
            pattern = re.compile(rf"(?<![A-Za-z0-9_+#]){escaped}(?![A-Za-z0-9_+#])", re.IGNORECASE)
            self.tech_patterns.append((pattern, ALIAS_TO_CANONICAL[alias]))

        sorted_soft = sorted(SOFT_ALIAS_TO_CANONICAL.keys(), key=len, reverse=True)
        self.soft_patterns: List[Tuple[re.Pattern, str]] = []
        for alias in sorted_soft:
            escaped = re.escape(alias)
            pattern = re.compile(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])", re.IGNORECASE)
            self.soft_patterns.append((pattern, SOFT_ALIAS_TO_CANONICAL[alias]))

    def extract_technical_skills(self, text: str) -> List[str]:
        """Extracts and returns deduplicated canonical technical skills found in text."""
        if not text:
            return []
        found: Set[str] = set()
        for pattern, canonical in self.tech_patterns:
            if pattern.search(text):
                found.add(canonical)
        return sorted(list(found))

    def extract_soft_skills(self, text: str) -> List[str]:
        """Extracts and returns deduplicated canonical soft skills found in text."""
        if not text:
            return []
        found: Set[str] = set()
        for pattern, canonical in self.soft_patterns:
            if pattern.search(text):
                found.add(canonical)
        return sorted(list(found))
