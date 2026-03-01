"""
resume_parser.py - Core module for parsing resumes.

Orchestrates the full resume parsing pipeline:
  1. Extract raw text from the file (PDF / DOCX / TXT).
  2. Extract contact info  — name (spaCy NER), email & phone (regex).
  3. Extract skills        — keyword matching via SkillExtractor.
  4. Extract education     — section-header + degree-keyword heuristics.
  5. Estimate experience   — year-range regex scanning.

Usage:
    parser = ResumeParser()
    result = parser.parse("resume.pdf")
    # result is a dict with keys:
    #   name, email, phone, skills, education, years_of_experience

    # Or parse from already-extracted text:
    result = parser.parse_text(raw_text)
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# Path to the skills list, anchored to the repo root via this file's location.
# Works correctly regardless of the working directory (e.g. on Streamlit Cloud).
_DEFAULT_SKILLS_PATH = str(Path(__file__).parent.parent / "data" / "skills_list.txt")

import spacy

from .text_extractor import TextExtractor
from .skill_extractor import SkillExtractor

# ---------------------------------------------------------------------------
# spaCy model — load once at import time.
# Falls back gracefully if the model is not installed.
# ---------------------------------------------------------------------------
try:
    _NLP = spacy.load("en_core_web_sm")
except OSError:
    _NLP = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Email
_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

# Phone — matches common formats: +91-9876543210, (123) 456-7890, 123.456.7890, etc.
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-.]?)?"          # optional country code
    r"(?:\(?\d{2,4}\)?[\s\-.]?)"        # area code
    r"\d{3,4}[\s\-.]?\d{4}",
    re.IGNORECASE,
)

# Year — four-digit years between 1950 and 2099
_YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-9]\d)\b")

# Year range: "2018 – 2022", "Jan 2019 - Present", "2020–Present"
_YEAR_RANGE_RE = re.compile(
    r"\b(19[5-9]\d|20[0-9]\d)\b"
    r"[\s\-–—to]+"
    r"(?:\b(19[5-9]\d|20[0-9]\d)\b|present|current|now)",
    re.IGNORECASE,
)

# Education section header
_EDU_SECTION_RE = re.compile(
    r"^\s*(education|academic|qualification|degree|university|college)\b",
    re.IGNORECASE | re.MULTILINE,
)

# Degree keywords
_DEGREE_RE = re.compile(
    r"\b(b\.?tech|b\.?e\.?|b\.?sc\.?|b\.?a\.?|b\.?com\.?|"
    r"m\.?tech|m\.?e\.?|m\.?sc\.?|m\.?a\.?|mba|ph\.?d\.?|"
    r"bachelor|master|doctorate|diploma|associate)\b",
    re.IGNORECASE,
)

# Experience section header
_EXP_SECTION_RE = re.compile(
    r"^\s*(experience|employment|work history|career|professional background)\b",
    re.IGNORECASE | re.MULTILINE,
)



class ResumeParser:
    """
    Parses resume documents and returns structured information as a dict.

    Attributes:
        text_extractor (TextExtractor): Extracts raw text from files.
        skill_extractor (SkillExtractor): Identifies skills from text.
    """

    def __init__(self, skills_list_path: str = _DEFAULT_SKILLS_PATH):
        """
        Initialize the ResumeParser.

        Args:
            skills_list_path (str): Path to the skills list file used by
                                    SkillExtractor.
        """
        self.text_extractor = TextExtractor()
        self.skill_extractor = SkillExtractor(skills_list_path)

    # ------------------------------------------------------------------
    # Top-level API
    # ------------------------------------------------------------------

    def parse(self, file_path: str) -> dict:
        """
        Parse a resume file and return structured data.

        Args:
            file_path (str): Path to the resume file (PDF / DOCX / TXT).

        Returns:
            dict: Structured resume data with keys:
                  ``name``, ``email``, ``phone``, ``skills``,
                  ``education``, ``years_of_experience``.
        """
        raw_text = self.text_extractor.extract(file_path)
        return self.parse_text(raw_text)

    def parse_text(self, text: str) -> dict:
        """
        Parse already-extracted resume text and return structured data.

        Useful when the caller has already obtained the raw text (e.g. from
        an upload stream).

        Args:
            text (str): Clean resume text.

        Returns:
            dict: Same structure as :meth:`parse`.
        """
        contact = self.extract_contact_info(text)
        skills = self.skill_extractor.extract(text)
        education = self.extract_education(text)
        years_exp = self._estimate_years_of_experience(text)

        return {
            "name": contact.get("name"),
            "email": contact.get("email"),
            "phone": contact.get("phone"),
            "skills": skills,
            "education": education,
            "years_of_experience": years_exp,
        }

    # ------------------------------------------------------------------
    # Contact info
    # ------------------------------------------------------------------

    def extract_contact_info(self, text: str) -> dict:
        """
        Extract contact information from resume text.

        - **Name**  — detected via spaCy PERSON entity from the first 20 lines.
          Falls back to the first non-empty line if spaCy is unavailable.
        - **Email** — first match of a standard email regex.
        - **Phone** — first match of a flexible phone-number regex.

        Args:
            text (str): Resume text.

        Returns:
            dict: ``{"name": str|None, "email": str|None, "phone": str|None}``
        """
        return {
            "name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
        }

    def _extract_name(self, text: str) -> Optional[str]:
        """Use spaCy NER to find the candidate's name from the top of the resume."""
        # Limit to the first 20 lines — the name is almost always at the top
        header = "\n".join(text.splitlines()[:20])

        if _NLP is not None:
            doc = _NLP(header)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text.strip()

        # Fallback: return the first non-empty, non-email, non-phone line
        for line in text.splitlines():
            line = line.strip()
            if (
                line
                and not _EMAIL_RE.search(line)
                and not _PHONE_RE.search(line)
                and len(line.split()) <= 6          # names are short
                and not line.startswith("http")
            ):
                return line

        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Return the first email address found in the text."""
        match = _EMAIL_RE.search(text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Return the first phone number found in the text."""
        match = _PHONE_RE.search(text)
        if match:
            # Normalise whitespace in the matched number
            return re.sub(r"\s+", " ", match.group(0)).strip()
        return None

    # ------------------------------------------------------------------
    # Education
    # ------------------------------------------------------------------

    def extract_education(self, text: str) -> list[dict]:
        """
        Extract education entries from resume text.

        Heuristic:
        1. Locate the education section by header keyword.
        2. Scan lines within that section for degree keywords.
        3. Also capture the year(s) mentioned on the same line.

        Args:
            text (str): Resume text.

        Returns:
            list[dict]: Each entry has keys ``degree``, ``institution``,
                        ``year``.  Fields may be ``None`` if not found.
        """
        lines = text.splitlines()
        edu_start = self._find_section_start(lines, _EDU_SECTION_RE)
        edu_end = self._find_next_section_start(lines, edu_start, _EDU_SECTION_RE)

        section_lines = lines[edu_start:edu_end] if edu_start is not None else lines

        entries: list[dict] = []
        for line in section_lines:
            if _DEGREE_RE.search(line):
                year_match = _YEAR_RE.search(line)
                entries.append({
                    "degree": line.strip(),
                    "institution": None,   # deeper parsing left for future work
                    "year": int(year_match.group(0)) if year_match else None,
                })

        return entries

    # ------------------------------------------------------------------
    # Experience (years estimation)
    # ------------------------------------------------------------------

    def extract_experience(self, text: str) -> list[dict]:
        """
        Extract work experience entries from resume text.

        Scans for year-range patterns (e.g. "2018 – 2022", "Jan 2020 – Present")
        within the experience section and returns each as a dict.

        Args:
            text (str): Resume text.

        Returns:
            list[dict]: Each entry has keys ``start_year`` and ``end_year``
                        (``None`` means "Present / ongoing").
        """
        lines = text.splitlines()
        exp_start = self._find_section_start(lines, _EXP_SECTION_RE)
        exp_end = self._find_next_section_start(lines, exp_start, _EXP_SECTION_RE)

        section_text = "\n".join(
            lines[exp_start:exp_end] if exp_start is not None else lines
        )

        current_year = datetime.now().year
        entries: list[dict] = []
        for match in _YEAR_RANGE_RE.finditer(section_text):
            start_year = int(match.group(1))
            end_raw = match.group(2)
            if end_raw is None or end_raw.lower() in ("present", "current", "now"):
                end_year = None
            else:
                end_year = int(end_raw)

            # Basic sanity: skip future start years
            if start_year <= current_year:
                entries.append({
                    "start_year": start_year,
                    "end_year": end_year,
                })

        return entries

    def _estimate_years_of_experience(self, text: str) -> int:
        """
        Estimate total years of professional experience.

        Merges overlapping year ranges before summing to avoid double-counting
        concurrent roles (e.g. two jobs with overlapping periods).

        Note: This is an approximation — ranges are year-granularity only,
        so partial years at boundaries may be off by up to ±1 year.

        Args:
            text (str): Resume text.

        Returns:
            int: Approximate total years of experience (≥ 0).
        """
        entries = self.extract_experience(text)
        if not entries:
            return 0

        current_year = datetime.now().year

        # Build (start, end) intervals; treat open-ended ranges as current year.
        intervals = []
        for e in entries:
            start = e["start_year"]
            end = e["end_year"] if e["end_year"] is not None else current_year
            if start <= end:
                intervals.append((start, end))

        if not intervals:
            return 0

        # Sort by start year, then merge overlapping/adjacent intervals.
        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]
        for start, end in intervals[1:]:
            prev_start, prev_end = merged[-1]
            if start <= prev_end:          # overlapping or adjacent — extend
                merged[-1] = (prev_start, max(prev_end, end))
            else:
                merged.append((start, end))

        # Sum durations of the merged (non-overlapping) intervals.
        # Approximate: result is in whole years.
        total = sum(end - start for start, end in merged)
        return max(0, total)

    # ------------------------------------------------------------------
    # Section-finding helpers
    # ------------------------------------------------------------------

    def _find_section_start(
        self, lines: list[str], header_re: re.Pattern
    ) -> Optional[int]:
        """Return the line index of the first line matching *header_re*, or None."""
        for i, line in enumerate(lines):
            if header_re.search(line):
                return i
        return None

    def _find_next_section_start(
        self,
        lines: list[str],
        current_start: Optional[int],
        current_re: re.Pattern,
    ) -> Optional[int]:
        """
        Return the line index of the *next* section header after *current_start*,
        or ``len(lines)`` if no subsequent header is found.
        """
        if current_start is None:
            return None

        # Common section header pattern (capitalised short lines)
        _GENERIC_SECTION_RE = re.compile(
            r"^\s*(education|experience|skills|employment|work|projects?|"
            r"certifications?|awards?|publications?|summary|objective|"
            r"profile|contact|references?|languages?|interests?|hobbies)\b",
            re.IGNORECASE,
        )

        for i in range(current_start + 1, len(lines)):
            if _GENERIC_SECTION_RE.search(lines[i]):
                return i

        return len(lines)
