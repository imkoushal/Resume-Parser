"""
resume_routes.py - FastAPI route definitions for the Resume Intelligence API.

All endpoints are defined here and delegate business logic to service modules.
No processing logic lives in this file — routes only validate input, call
services, and return structured responses.
"""

import io

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.core.auth import get_optional_user
from src.models.response_models import (
    AnalyzeResumeResponse,
    EducationEntry,
    HealthResponse,
    JDMatchResponse,
    JDRequirements,
    ParsedResumeResponse,
    SkillsResponse,
    SuggestionItem,
)
from src.services.text_extractor import TextExtractor
from src.services.resume_parser import ResumeParser
from src.services.jd_matcher import JDMatcher
from src.services.ats_scorer import ATSScorer
from src.services.skill_gap_analyzer import SkillGapAnalyzer
from src.services.resume_recommender import ResumeRecommender
from src.services import analysis_service

router = APIRouter()

# ---------------------------------------------------------------------------
# Shared service instances (created once, reused across requests)
# ---------------------------------------------------------------------------
_text_extractor = TextExtractor()
_parser = ResumeParser()
_matcher = JDMatcher()
_ats_scorer = ATSScorer()
_gap_analyzer = SkillGapAnalyzer()
_recommender = ResumeRecommender()

# ---------------------------------------------------------------------------
# Allowed upload extensions
# ---------------------------------------------------------------------------
_ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _validate_and_read(file: UploadFile) -> io.BytesIO:
    """
    Validate the uploaded file extension and return a seekable BytesIO buffer.

    Raises:
        HTTPException 400: If the file type is not supported.
    """
    filename = file.filename or ""
    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[1].lower()

    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{ext}'. "
                f"Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}"
            ),
        )

    contents = file.file.read()
    buf = io.BytesIO(contents)
    buf.name = filename
    return buf


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check — returns service status."""
    return HealthResponse(status="ok")


# ---------------------------------------------------------------------------
# POST /parse-resume
# ---------------------------------------------------------------------------

@router.post("/parse-resume", response_model=ParsedResumeResponse)
async def parse_resume(file: UploadFile = File(...)):
    """
    Upload a resume (PDF or DOCX) and receive fully parsed structured data.
    """
    buf = _validate_and_read(file)

    try:
        raw_text = _text_extractor.extract(buf)
        result = _parser.parse_text(raw_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {exc}")

    return ParsedResumeResponse(
        name=result.get("name"),
        email=result.get("email"),
        phone=result.get("phone"),
        skills=result.get("skills", []),
        education=[
            EducationEntry(**edu) for edu in result.get("education", [])
        ],
        years_of_experience=result.get("years_of_experience", 0),
    )


# ---------------------------------------------------------------------------
# POST /extract-skills
# ---------------------------------------------------------------------------

@router.post("/extract-skills", response_model=SkillsResponse)
async def extract_skills(file: UploadFile = File(...)):
    """
    Upload a resume and receive the extracted skills list only.
    """
    buf = _validate_and_read(file)

    try:
        raw_text = _text_extractor.extract(buf)
        skills = _parser.skill_extractor.extract(raw_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Skill extraction failed: {exc}")

    return SkillsResponse(skills=skills, count=len(skills))


# ---------------------------------------------------------------------------
# POST /match-job-description
# ---------------------------------------------------------------------------

@router.post("/match-job-description", response_model=JDMatchResponse)
async def match_job_description(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Upload a resume and a job description text, receive a match analysis report.
    """
    buf = _validate_and_read(file)

    try:
        raw_text = _text_extractor.extract(buf)
        parsed = _parser.parse_text(raw_text)
        parsed["_raw_text"] = raw_text
        match_result = _matcher.match(parsed, job_description)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"JD matching failed: {exc}")

    return JDMatchResponse(
        match_score=match_result["match_score"],
        skill_score=match_result["skill_score"],
        semantic_score=match_result["semantic_score"],
        matched_skills=match_result["matched_skills"],
        missing_skills=match_result["missing_skills"],
        jd_skills=match_result["jd_skills"],
        resume_skills=match_result["resume_skills"],
        is_match=match_result["is_match"],
        jd_requirements=JDRequirements(**match_result["jd_requirements"]),
    )


# ---------------------------------------------------------------------------
# POST /analyze-resume
# ---------------------------------------------------------------------------

@router.post("/analyze-resume", response_model=AnalyzeResumeResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(default=""),
    current_user: dict | None = Depends(get_optional_user),
):
    """
    Full intelligence analysis pipeline:
    parse → skill extraction → optional JD skill gap → ATS scoring → recommendations.

    If ``job_description`` is provided, skill gap analysis and JD-aware ATS
    scoring are included.  Without a JD, ATS scoring runs in resume-only mode.

    If a valid JWT token is provided, results are persisted to the database.
    """
    buf = _validate_and_read(file)

    # Step 1: Text extraction
    try:
        raw_text = _text_extractor.extract(buf)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {exc}")

    # Step 2: Resume parsing + skill extraction
    try:
        parsed = _parser.parse_text(raw_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {exc}")

    resume_skills = parsed.get("skills", [])
    has_jd = bool(job_description.strip())

    # Step 3: Optional JD skill extraction + skill gap analysis
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    jd_skills: list[str] = []

    if has_jd:
        try:
            jd_skills = _matcher.skill_extractor.extract(job_description)
            gap_result = _gap_analyzer.analyze(resume_skills, jd_skills)
            matched_skills = gap_result["matched_skills"]
            missing_skills = gap_result["missing_skills"]
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {exc}")

    # Step 4: ATS scoring
    try:
        ats_result = _ats_scorer.score(
            resume_text=raw_text,
            resume_skills=resume_skills,
            job_description=job_description if has_jd else None,
            jd_skills=jd_skills if has_jd else None,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ATS scoring failed: {exc}")

    # Step 5: Resume recommendations
    try:
        suggestions_raw = _recommender.recommend(
            resume_text=raw_text,
            parsed_resume=parsed,
            missing_skills=missing_skills,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {exc}")

    # Step 6: Persist results if user is authenticated
    if current_user is not None:
        try:
            user_email = current_user["sub"]
            resume_id = await analysis_service.store_resume(
                user_id=user_email,
                filename=file.filename or "unknown",
                parsed_data=parsed,
            )
            await analysis_service.store_analysis(
                user_id=user_email,
                resume_id=resume_id,
                analysis_data={
                    "ats_score": ats_result["ats_score"],
                    "keyword_score": ats_result["keyword_score"],
                    "skill_coverage_score": ats_result["skill_coverage_score"],
                    "experience_score": ats_result["experience_score"],
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                    "suggestions": suggestions_raw,
                    "job_description": job_description if has_jd else "",
                },
            )
        except Exception:
            pass  # Persistence failure should not break the response

    return AnalyzeResumeResponse(
        name=parsed.get("name"),
        email=parsed.get("email"),
        skills=resume_skills,
        ats_score=ats_result["ats_score"],
        keyword_score=ats_result["keyword_score"],
        skill_coverage_score=ats_result["skill_coverage_score"],
        experience_score=ats_result["experience_score"],
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        suggestions=[
            SuggestionItem(**s) for s in suggestions_raw
        ],
    )


