"""
ats_scorer.py - ATS Compatibility Scorer.

Calculates an ATS (Applicant Tracking System) compatibility score for a
resume, optionally compared against a job description.

Operates in two modes:
  - **Resume-only**: Scores based on content quality, skill density, and
    experience signals.
  - **Resume + JD**: Scores based on keyword match against JD, skill
    coverage of JD requirements, and experience signals.

Usage:
    scorer = ATSScorer()
    result = scorer.score(resume_text, resume_skills)
    result = scorer.score(resume_text, resume_skills, job_description="...")
"""

import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# Action verbs commonly expected in strong resumes
# ---------------------------------------------------------------------------
_ACTION_VERBS = {
    "achieved", "administered", "analyzed", "built", "collaborated",
    "created", "decreased", "delivered", "designed", "developed",
    "directed", "engineered", "established", "executed", "generated",
    "implemented", "improved", "increased", "launched", "led",
    "managed", "mentored", "negotiated", "optimized", "orchestrated",
    "organized", "performed", "pioneered", "planned", "produced",
    "reduced", "resolved", "restructured", "scaled", "spearheaded",
    "streamlined", "supervised", "transformed", "upgraded",
}

# Regex for measurable achievements: numbers, percentages, dollar amounts
_METRIC_RE = re.compile(
    r"\b\d+[%+]?\b|"          # plain numbers or percentages
    r"\$\s?\d[\d,]*|"         # dollar amounts
    r"\d+x\b",               # multipliers like "3x"
    re.IGNORECASE,
)


class ATSScorer:
    """
    Calculates an ATS compatibility score (0–100) for a resume.

    Score components (weights):
        - Keyword match   (40%): TF-IDF cosine vs JD, or content quality heuristic
        - Skill coverage  (40%): JD skill coverage %, or skill density
        - Experience      (20%): Action verbs and measurable achievements
    """

    KEYWORD_WEIGHT = 0.40
    SKILL_WEIGHT = 0.40
    EXPERIENCE_WEIGHT = 0.20

    def __init__(self):
        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

    def score(
        self,
        resume_text: str,
        resume_skills: list[str],
        job_description: str | None = None,
        jd_skills: list[str] | None = None,
    ) -> dict:
        """
        Calculate the ATS compatibility score.

        Args:
            resume_text: Full extracted resume text.
            resume_skills: Skills already extracted from the resume.
            job_description: Optional JD text for keyword matching.
            jd_skills: Optional skills extracted from the JD.

        Returns:
            dict with keys: ats_score, keyword_score,
                            skill_coverage_score, experience_score
                            (all floats 0–100).
        """
        has_jd = bool(job_description and job_description.strip())

        keyword_score = (
            self._keyword_score_with_jd(resume_text, job_description)
            if has_jd
            else self._keyword_score_resume_only(resume_text)
        )

        skill_coverage_score = (
            self._skill_coverage_with_jd(resume_skills, jd_skills or [])
            if has_jd
            else self._skill_density(resume_text, resume_skills)
        )

        experience_score = self._experience_score(resume_text)

        ats_score = (
            self.KEYWORD_WEIGHT * keyword_score
            + self.SKILL_WEIGHT * skill_coverage_score
            + self.EXPERIENCE_WEIGHT * experience_score
        )

        return {
            "ats_score": round(ats_score, 1),
            "keyword_score": round(keyword_score, 1),
            "skill_coverage_score": round(skill_coverage_score, 1),
            "experience_score": round(experience_score, 1),
        }

    # ------------------------------------------------------------------
    # Keyword scoring
    # ------------------------------------------------------------------

    def _keyword_score_with_jd(
        self, resume_text: str, job_description: str
    ) -> float:
        """TF-IDF cosine similarity between resume and JD (0–100)."""
        if not resume_text.strip() or not job_description.strip():
            return 0.0
        try:
            matrix = self._vectorizer.fit_transform(
                [resume_text, job_description]
            )
            sim = cosine_similarity(matrix[0:1], matrix[1:2])
            return float(sim[0][0]) * 100
        except ValueError:
            return 0.0

    def _keyword_score_resume_only(self, resume_text: str) -> float:
        """
        Heuristic content quality score when no JD is available.

        Based on: word count adequacy, section diversity, and vocabulary
        richness (unique-word ratio).
        """
        if not resume_text.strip():
            return 0.0

        words = resume_text.lower().split()
        word_count = len(words)
        unique_ratio = len(set(words)) / max(word_count, 1)

        # Word count score: 200–800 words is ideal
        if word_count < 100:
            length_score = 30
        elif word_count < 200:
            length_score = 60
        elif word_count <= 800:
            length_score = 90
        else:
            length_score = 75  # too long

        # Vocabulary richness: higher unique ratio = better
        vocab_score = min(unique_ratio * 150, 100)

        return (length_score * 0.5) + (vocab_score * 0.5)

    # ------------------------------------------------------------------
    # Skill coverage scoring
    # ------------------------------------------------------------------

    def _skill_coverage_with_jd(
        self, resume_skills: list[str], jd_skills: list[str]
    ) -> float:
        """Percentage of JD skills covered by resume (0–100)."""
        if not jd_skills:
            return 0.0
        resume_lower = {s.lower() for s in resume_skills}
        jd_lower = {s.lower() for s in jd_skills}
        matched = resume_lower & jd_lower
        return (len(matched) / len(jd_lower)) * 100

    def _skill_density(
        self, resume_text: str, resume_skills: list[str]
    ) -> float:
        """
        Skill density heuristic when no JD is available.

        Ratio of detected skills to total word count, scaled to 0–100.
        A resume with ~10+ skills per 400 words scores well.
        """
        word_count = max(len(resume_text.split()), 1)
        skill_count = len(resume_skills)
        # Normalize: 1 skill per 40 words ≈ 100%
        density = (skill_count / word_count) * 40
        return min(density * 100, 100)

    # ------------------------------------------------------------------
    # Experience signal scoring
    # ------------------------------------------------------------------

    def _experience_score(self, resume_text: str) -> float:
        """
        Score based on action verbs and measurable achievements (0–100).

        Checks for:
        - Presence of strong action verbs (50%)
        - Measurable metrics like numbers, percentages, dollar amounts (50%)
        """
        text_lower = resume_text.lower()
        words = set(text_lower.split())

        # Action verb score: count unique action verbs found
        verb_hits = words & _ACTION_VERBS
        verb_score = min(len(verb_hits) / 8 * 100, 100)  # 8+ verbs = full score

        # Metrics score: count lines with measurable achievements
        lines = resume_text.splitlines()
        metric_lines = sum(1 for line in lines if _METRIC_RE.search(line))
        metric_score = min(metric_lines / 5 * 100, 100)  # 5+ metric lines = full

        return (verb_score * 0.5) + (metric_score * 0.5)
