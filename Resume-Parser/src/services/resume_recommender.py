"""
resume_recommender.py - Resume Improvement Recommendations.

Generates actionable suggestions for improving a resume based on:
  - Missing skills (from skill gap analysis)
  - Weak experience descriptions (lacking action verbs)
  - Absence of measurable achievements (numbers, percentages)

Usage:
    recommender = ResumeRecommender()
    suggestions = recommender.recommend(
        resume_text=raw_text,
        parsed_resume=parsed_dict,
        missing_skills=["Docker", "Kubernetes"],
    )
"""

import re


# ---------------------------------------------------------------------------
# Action verbs that signal strong experience descriptions
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

# Regex for measurable achievements
_METRIC_RE = re.compile(
    r"\b\d+[%+]?\b|"
    r"\$\s?\d[\d,]*|"
    r"\d+x\b",
    re.IGNORECASE,
)

# Experience-section header keywords
_EXP_HEADER_RE = re.compile(
    r"^\s*(experience|employment|work history|career|professional)\b",
    re.IGNORECASE,
)

# Generic section header (to detect end of experience section)
_SECTION_HEADER_RE = re.compile(
    r"^\s*(education|skills|projects?|certifications?|awards?|"
    r"publications?|summary|objective|profile|contact|references?|"
    r"languages?|interests?|hobbies)\b",
    re.IGNORECASE,
)


class ResumeRecommender:
    """
    Generates improvement suggestions for a resume.

    Each suggestion is a dict with:
        category (str): One of "missing_skills", "weak_experience",
                        "measurable_achievements", "general"
        message  (str): Human-readable recommendation.
    """

    def recommend(
        self,
        resume_text: str,
        parsed_resume: dict,
        missing_skills: list[str] | None = None,
    ) -> list[dict]:
        """
        Generate improvement suggestions.

        Args:
            resume_text: Full extracted resume text.
            parsed_resume: Output of ResumeParser.parse_text().
            missing_skills: Skills missing vs the JD (may be empty/None).

        Returns:
            list[dict]: Each with keys ``category`` and ``message``.
        """
        suggestions: list[dict] = []

        suggestions.extend(self._missing_skill_suggestions(missing_skills or []))
        suggestions.extend(self._weak_experience_suggestions(resume_text))
        suggestions.extend(self._metric_suggestions(resume_text))
        suggestions.extend(self._general_suggestions(resume_text, parsed_resume))

        return suggestions

    # ------------------------------------------------------------------
    # Missing skills
    # ------------------------------------------------------------------

    def _missing_skill_suggestions(
        self, missing_skills: list[str]
    ) -> list[dict]:
        """Suggest adding missing skills if any."""
        if not missing_skills:
            return []

        suggestions = []

        if len(missing_skills) <= 5:
            skill_list = ", ".join(missing_skills)
            suggestions.append({
                "category": "missing_skills",
                "message": (
                    f"Add the following skills to your resume if you have "
                    f"experience with them: {skill_list}."
                ),
            })
        else:
            top_five = ", ".join(missing_skills[:5])
            suggestions.append({
                "category": "missing_skills",
                "message": (
                    f"Your resume is missing {len(missing_skills)} skills "
                    f"from the job description. Prioritize adding: {top_five}."
                ),
            })

        return suggestions

    # ------------------------------------------------------------------
    # Weak experience descriptions
    # ------------------------------------------------------------------

    def _weak_experience_suggestions(self, resume_text: str) -> list[dict]:
        """Check if experience bullet points use strong action verbs."""
        exp_lines = self._get_experience_lines(resume_text)

        if not exp_lines:
            return [{
                "category": "weak_experience",
                "message": (
                    "No clear experience section detected. Consider adding "
                    "a dedicated 'Experience' section with role descriptions."
                ),
            }]

        # Count lines that start with an action verb
        strong_lines = 0
        for line in exp_lines:
            first_word = line.strip().split()[0].lower().rstrip(".,;:") if line.strip() else ""
            if first_word in _ACTION_VERBS:
                strong_lines += 1

        ratio = strong_lines / max(len(exp_lines), 1)

        suggestions = []
        if ratio < 0.4:
            suggestions.append({
                "category": "weak_experience",
                "message": (
                    "Most of your experience descriptions lack strong action "
                    "verbs. Start bullet points with verbs like 'Developed', "
                    "'Implemented', 'Optimized', or 'Led' to create impact."
                ),
            })

        return suggestions

    # ------------------------------------------------------------------
    # Measurable achievements
    # ------------------------------------------------------------------

    def _metric_suggestions(self, resume_text: str) -> list[dict]:
        """Check for presence of quantifiable achievements."""
        lines = resume_text.splitlines()
        metric_lines = sum(1 for line in lines if _METRIC_RE.search(line))

        suggestions = []
        if metric_lines < 3:
            suggestions.append({
                "category": "measurable_achievements",
                "message": (
                    "Your resume lacks measurable achievements. Add specific "
                    "metrics like 'Reduced load time by 40%', 'Managed a team "
                    "of 8', or 'Increased revenue by $50K' to demonstrate impact."
                ),
            })

        return suggestions

    # ------------------------------------------------------------------
    # General suggestions
    # ------------------------------------------------------------------

    def _general_suggestions(
        self, resume_text: str, parsed_resume: dict
    ) -> list[dict]:
        """General best-practice checks."""
        suggestions = []

        # Check if contact info is complete
        if not parsed_resume.get("email"):
            suggestions.append({
                "category": "general",
                "message": "No email address detected. Ensure your contact email is clearly visible at the top.",
            })

        if not parsed_resume.get("phone"):
            suggestions.append({
                "category": "general",
                "message": "No phone number detected. Consider adding a phone number for recruiter contact.",
            })

        # Check resume length
        word_count = len(resume_text.split())
        if word_count < 150:
            suggestions.append({
                "category": "general",
                "message": "Your resume appears very short. Aim for at least 300–600 words to adequately showcase your experience.",
            })

        # Check for skills section
        if not parsed_resume.get("skills"):
            suggestions.append({
                "category": "general",
                "message": "No skills detected. Add a clear 'Skills' section listing your technical and soft skills.",
            })

        return suggestions

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_experience_lines(self, resume_text: str) -> list[str]:
        """Extract lines within the experience section."""
        lines = resume_text.splitlines()

        # Find experience section start
        exp_start = None
        for i, line in enumerate(lines):
            if _EXP_HEADER_RE.search(line):
                exp_start = i + 1
                break

        if exp_start is None:
            return []

        # Find the next section header after experience
        exp_end = len(lines)
        for i in range(exp_start, len(lines)):
            if _SECTION_HEADER_RE.search(lines[i]):
                exp_end = i
                break

        # Return non-empty lines in the experience section
        return [
            line for line in lines[exp_start:exp_end]
            if line.strip() and len(line.strip()) > 10
        ]
