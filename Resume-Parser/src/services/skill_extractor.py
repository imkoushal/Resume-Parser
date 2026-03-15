"""
skill_extractor.py - Skill Extraction module.

Identifies and extracts skills from resume text using a predefined
skills list loaded from data/skills_list.txt.

Usage:
    extractor = SkillExtractor()
    skills = extractor.extract("Proficient in Python, React, and Docker.")
    # → ['Python', 'React', 'Docker']
"""

import os
import re

from src.core.config import SKILLS_FILE_PATH


# ---------------------------------------------------------------------------
# Category keywords — maps category header keywords (from skills_list.txt
# comment lines) to a canonical category name.
# ---------------------------------------------------------------------------
_CATEGORY_PATTERNS = [
    (re.compile(r"programming\s+language", re.I), "Programming Languages"),
    (re.compile(r"web\s+dev", re.I),               "Web Development"),
    (re.compile(r"data\s+science|machine\s+learning|ml", re.I), "Data Science & ML"),
    (re.compile(r"database", re.I),                "Databases"),
    (re.compile(r"cloud|devops", re.I),            "Cloud & DevOps"),
    (re.compile(r"tools?\s*&?\s*platform", re.I), "Tools & Platforms"),
    (re.compile(r"soft\s+skill", re.I),            "Soft Skills"),
]


class SkillExtractor:
    """
    Extracts skills from resume text via keyword matching against a curated
    skills database.

    Attributes:
        skills_list_path (str): Path to the skills list file.
        skills_db (list[str]): Skills loaded from the file (original casing).
        _skills_lower (list[str]): Lower-cased skills for fast matching.
        _category_map (dict[str, str]): Maps lower-cased skill → category name.
    """

    def __init__(self, skills_list_path: str = SKILLS_FILE_PATH):
        """
        Initialize the SkillExtractor and load the skills database.

        Args:
            skills_list_path (str): Path to the skills list file.
        """
        self.skills_list_path = skills_list_path
        self.skills_db: list[str] = []
        self._skills_lower: list[str] = []
        self._category_map: dict[str, str] = {}

        self.skills_db = self._load_skills()
        self._skills_lower = [s.lower() for s in self.skills_db]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, text: str) -> list[str]:
        """
        Extract skills present in *text* by matching against the skills DB.

        Matching is case-insensitive and uses whole-word boundaries so that
        e.g. "C" does not match inside "CSS".

        Args:
            text (str): Resume text to scan.

        Returns:
            list[str]: Deduplicated list of matched skills (original casing
                       from the skills DB), sorted alphabetically.
        """
        if not text or not self.skills_db:
            return []

        text_lower = text.lower()
        found: list[str] = []

        for skill, skill_lower in zip(self.skills_db, self._skills_lower):
            # Build a word-boundary pattern; escape special regex chars
            pattern = r"(?<![a-zA-Z0-9+#])" + re.escape(skill_lower) + r"(?![a-zA-Z0-9+#])"
            if re.search(pattern, text_lower):
                found.append(skill)

        # Deduplicate while preserving order, then sort
        seen: set[str] = set()
        unique: list[str] = []
        for s in found:
            key = s.lower()
            if key not in seen:
                seen.add(key)
                unique.append(s)

        return sorted(unique, key=str.lower)

    def normalize_skill(self, skill: str) -> str:
        """
        Normalize a skill string: strip whitespace and collapse internal spaces.

        Args:
            skill (str): Raw skill string.

        Returns:
            str: Normalized skill string.
        """
        return re.sub(r"\s+", " ", skill.strip())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_skills(self) -> list[str]:
        """
        Load skills from the skills list file.

        Lines starting with ``#`` are treated as comments; blank lines are
        skipped.  Category headers (comment lines containing category keywords)
        are used to build the internal ``_category_map``.

        Returns:
            list[str]: Skills in the order they appear in the file.
        """
        if not os.path.isfile(self.skills_list_path):
            # Graceful degradation — return empty list, extraction still works
            return []

        skills: list[str] = []
        current_category = "Other"

        with open(self.skills_list_path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    # Attempt to detect a category from the comment text
                    for pattern, cat_name in _CATEGORY_PATTERNS:
                        if pattern.search(line):
                            current_category = cat_name
                            break
                    continue

                skill = self.normalize_skill(line)
                if skill:
                    skills.append(skill)
                    self._category_map[skill.lower()] = current_category

        return skills
