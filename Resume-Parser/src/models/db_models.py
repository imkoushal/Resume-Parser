"""
db_models.py - MongoDB document schemas.

These are plain dicts with helper functions for creating standardised
documents. They are NOT Pydantic models — they represent the shape of
documents stored in MongoDB collections.
"""

from datetime import datetime, timezone


def create_user_document(
    email: str,
    hashed_password: str,
    full_name: str,
) -> dict:
    """Create a new user document for the 'users' collection."""
    return {
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "created_at": datetime.now(timezone.utc),
    }


def create_resume_document(
    user_id: str,
    filename: str,
    parsed_data: dict,
) -> dict:
    """Create a new resume document for the 'resumes' collection."""
    return {
        "user_id": user_id,
        "filename": filename,
        "upload_date": datetime.now(timezone.utc),
        "parsed_data": parsed_data,
    }


def create_analysis_document(
    user_id: str,
    resume_id: str,
    analysis_data: dict,
) -> dict:
    """Create a new analysis result document for 'analysis_results'."""
    return {
        "user_id": user_id,
        "resume_id": resume_id,
        "ats_score": analysis_data.get("ats_score", 0),
        "keyword_score": analysis_data.get("keyword_score", 0),
        "skill_coverage_score": analysis_data.get("skill_coverage_score", 0),
        "experience_score": analysis_data.get("experience_score", 0),
        "matched_skills": analysis_data.get("matched_skills", []),
        "missing_skills": analysis_data.get("missing_skills", []),
        "suggestions": analysis_data.get("suggestions", []),
        "job_description": analysis_data.get("job_description", ""),
        "created_at": datetime.now(timezone.utc),
    }
