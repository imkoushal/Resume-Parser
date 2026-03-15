"""
jd_matcher.py - Job Description Matcher module.

Compares a parsed resume against a job description using two complementary
strategies:

1. **Skill-set matching** (primary) — extracts skills from both the resume
   and the JD via SkillExtractor, then computes a Jaccard-based match score.

2. **TF-IDF cosine similarity** (secondary) — vectorises the full resume text
   and JD text to capture semantic overlap beyond the skills list.

The final ``match_score`` is a weighted blend of both scores.

Usage:
    matcher = JDMatcher()
    result  = matcher.match(resume_data, job_description_text)

    # result dict keys:
    #   match_score        – float 0-100 (percentage)
    #   skill_score        – float 0-100 (skill-set overlap %)
    #   semantic_score     – float 0-100 (TF-IDF cosine similarity %)
    #   matched_skills     – list of skills present in both resume & JD
    #   missing_skills     – list of JD skills absent from resume
    #   jd_skills          – all skills extracted from the JD
    #   resume_skills      – all skills extracted from the resume
    #   is_match           – bool (True if match_score >= threshold * 100)
    #   jd_requirements    – structured dict from extract_jd_requirements()
"""

import re
from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.core.config import SKILLS_FILE_PATH
from .skill_extractor import SkillExtractor

# ---------------------------------------------------------------------------
# Regex helpers for JD requirement extraction
# ---------------------------------------------------------------------------

_YEAR_EXP_RE = re.compile(
    r"(\d+)\+?\s*(?:to\s*\d+\s*)?years?\s+(?:of\s+)?(?:experience|exp)",
    re.IGNORECASE,
)

_DEGREE_RE = re.compile(
    r"\b(b\.?tech|b\.?e\.?|b\.?sc\.?|b\.?a\.?|b\.?com\.?|"
    r"m\.?tech|m\.?e\.?|m\.?sc\.?|m\.?a\.?|mba|ph\.?d\.?|"
    r"bachelor|master|doctorate|diploma|associate)\b",
    re.IGNORECASE,
)


class JDMatcher:
    """
    Matches a parsed resume against a job description.

    Attributes:
        threshold (float): Score threshold (0.0–1.0) for ``is_match``.
        skill_weight (float): Weight given to skill-set score in the blend.
        semantic_weight (float): Weight given to TF-IDF cosine score in the blend.
        skill_extractor (SkillExtractor): Shared extractor instance.
        _vectorizer (TfidfVectorizer): Fitted on each match call.
    """

    def __init__(
        self,
        threshold: float = 0.7,
        skill_weight: float = 0.7,
        semantic_weight: float = 0.3,
        skills_list_path: str = SKILLS_FILE_PATH,
    ):
        """
        Initialise the JDMatcher.

        Args:
            threshold (float): Minimum blended score (0–1) to flag as a match.
                               Defaults to 0.7 (70 %).
            skill_weight (float): Weight for the skill-overlap score (0–1).
                                  Defaults to 0.7.
            semantic_weight (float): Weight for the TF-IDF cosine score (0–1).
                                     Defaults to 0.3.
            skills_list_path (str): Path to the skills list used by
                                    SkillExtractor.
        """
        if abs(skill_weight + semantic_weight - 1.0) > 1e-6:
            raise ValueError("skill_weight + semantic_weight must equal 1.0")

        self.threshold = threshold
        self.skill_weight = skill_weight
        self.semantic_weight = semantic_weight
        self.skill_extractor = SkillExtractor(skills_list_path)
        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),   # unigrams + bigrams for better coverage
            sublinear_tf=True,
        )

    # ------------------------------------------------------------------
    # Primary API
    # ------------------------------------------------------------------

    def match(self, resume_data: dict, job_description: str) -> dict:
        """
        Compare a parsed resume against a job description.

        Args:
            resume_data (dict): Output of ``ResumeParser.parse()`` — must
                                contain at least a ``"skills"`` key (list)
                                and optionally a ``"_raw_text"`` key for
                                semantic scoring.  If ``"_raw_text"`` is
                                absent the skills list is used as a proxy.
            job_description (str): Raw job description text.

        Returns:
            dict: Full match report (see module docstring for keys).
        """
        # --- Extract skills from both sides ---
        resume_skills: list[str] = resume_data.get("skills", [])
        jd_skills: list[str] = self.skill_extractor.extract(job_description)
        jd_requirements: dict = self.extract_jd_requirements(job_description)

        # --- Skill-set score ---
        matched = self._get_matched_skills(resume_skills, jd_skills)
        missing = self.get_missing_skills(resume_skills, jd_skills)
        skill_score = self.compute_score(resume_skills, jd_skills)

        # --- Semantic (TF-IDF cosine) score ---
        resume_text = resume_data.get("_raw_text", " ".join(resume_skills))
        semantic_score = self._compute_semantic_score(resume_text, job_description)

        # --- Blended score ---
        blended = (
            self.skill_weight * skill_score
            + self.semantic_weight * semantic_score
        )

        return {
            "match_score": round(blended * 100, 2),
            "skill_score": round(skill_score * 100, 2),
            "semantic_score": round(semantic_score * 100, 2),
            "matched_skills": sorted(matched, key=str.lower),
            "missing_skills": sorted(missing, key=str.lower),
            "jd_skills": sorted(jd_skills, key=str.lower),
            "resume_skills": sorted(resume_skills, key=str.lower),
            "is_match": blended >= self.threshold,
            "jd_requirements": jd_requirements,
        }

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    def compute_score(
        self, resume_skills: list[str], required_skills: list[str]
    ) -> float:
        """
        Compute a Jaccard-based skill match score.

        Score = |resume ∩ jd| / |jd|

        Using JD size as the denominator means the score reflects how much
        of *what the employer wants* the candidate covers.  Falls back to
        standard Jaccard (|∩| / |∪|) when the JD skill list is empty.

        Args:
            resume_skills (list[str]): Skills from the resume.
            required_skills (list[str]): Skills required by the JD.

        Returns:
            float: Score in [0.0, 1.0].
        """
        if not required_skills:
            return 0.0

        resume_set = {s.lower() for s in resume_skills}
        jd_set = {s.lower() for s in required_skills}

        intersection = resume_set & jd_set
        return len(intersection) / len(jd_set)

    def get_missing_skills(
        self, resume_skills: list[str], required_skills: list[str]
    ) -> list[str]:
        """
        Return JD skills that are absent from the resume.

        Args:
            resume_skills (list[str]): Skills from the resume.
            required_skills (list[str]): Skills required by the JD.

        Returns:
            list[str]: Missing skills (original casing from JD list).
        """
        resume_lower = {s.lower() for s in resume_skills}
        return [s for s in required_skills if s.lower() not in resume_lower]

    # ------------------------------------------------------------------
    # JD requirement extraction
    # ------------------------------------------------------------------

    def extract_jd_requirements(self, job_description: str) -> dict:
        """
        Extract structured requirements from a job description.

        Parses:
        - **skills** — via SkillExtractor
        - **min_experience_years** — first "N years of experience" mention
        - **education** — degree keywords found in the JD

        Args:
            job_description (str): Raw JD text.

        Returns:
            dict: ``{"skills": list, "min_experience_years": int|None,
                     "education": list[str]}``
        """
        skills = self.skill_extractor.extract(job_description)

        # Minimum experience years
        exp_match = _YEAR_EXP_RE.search(job_description)
        min_exp: Optional[int] = int(exp_match.group(1)) if exp_match else None

        # Education requirements
        education = list(
            {m.group(0).strip() for m in _DEGREE_RE.finditer(job_description)}
        )

        return {
            "skills": skills,
            "min_experience_years": min_exp,
            "education": sorted(education),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_matched_skills(
        self, resume_skills: list[str], jd_skills: list[str]
    ) -> list[str]:
        """Return skills present in both resume and JD (JD casing)."""
        resume_lower = {s.lower() for s in resume_skills}
        return [s for s in jd_skills if s.lower() in resume_lower]

    def _compute_semantic_score(
        self, resume_text: str, jd_text: str
    ) -> float:
        """
        Compute TF-IDF cosine similarity between resume text and JD text.

        Args:
            resume_text (str): Full resume text (or skill list as fallback).
            jd_text (str): Full job description text.

        Returns:
            float: Cosine similarity in [0.0, 1.0].
        """
        if not resume_text.strip() or not jd_text.strip():
            return 0.0

        try:
            tfidf_matrix = self._vectorizer.fit_transform(
                [resume_text, jd_text]
            )
            score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(score[0][0])
        except ValueError:
            # Vectoriser can fail on very short / empty texts
            return 0.0
