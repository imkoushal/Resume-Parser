"""
skill_gap_analyzer.py - Skill Gap Analysis module.

Compares pre-extracted resume skills against job description skills to
identify gaps. Does NOT re-extract skills — accepts already-extracted
lists from the caller.

Usage:
    analyzer = SkillGapAnalyzer()
    result = analyzer.analyze(resume_skills, jd_skills)
    # → {"matched_skills": [...], "missing_skills": [...], "match_percentage": 75.0}
"""


class SkillGapAnalyzer:
    """
    Compares resume skills against JD skills to find gaps.

    All comparisons are case-insensitive.  Original casing from the
    input lists is preserved in the output.
    """

    def analyze(
        self,
        resume_skills: list[str],
        jd_skills: list[str],
    ) -> dict:
        """
        Analyze the skill gap between resume and job description.

        Args:
            resume_skills: Skills already extracted from the resume.
            jd_skills: Skills already extracted from the job description.

        Returns:
            dict with keys:
                matched_skills  – list of JD skills found in resume
                missing_skills  – list of JD skills absent from resume
                match_percentage – float 0–100
        """
        if not jd_skills:
            return {
                "matched_skills": [],
                "missing_skills": [],
                "match_percentage": 0.0,
            }

        resume_lower = {s.lower() for s in resume_skills}

        matched = [s for s in jd_skills if s.lower() in resume_lower]
        missing = [s for s in jd_skills if s.lower() not in resume_lower]

        match_pct = (len(matched) / len(jd_skills)) * 100

        return {
            "matched_skills": sorted(matched, key=str.lower),
            "missing_skills": sorted(missing, key=str.lower),
            "match_percentage": round(match_pct, 1),
        }
