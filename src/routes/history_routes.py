"""
history_routes.py - Resume history and analysis history endpoints.

All endpoints require JWT authentication.

GET /analysis/history        — list past analysis results
GET /resumes                 — list uploaded resumes
GET /resumes/{resume_id}     — get a specific resume by ID
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.auth import get_current_user
from src.models.response_models import AnalysisHistoryItem, ResumeHistoryItem
from src.services import analysis_service

router = APIRouter(tags=["History"])


# ---------------------------------------------------------------------------
# GET /analysis/history
# ---------------------------------------------------------------------------

@router.get("/analysis/history", response_model=list[AnalysisHistoryItem])
async def get_analysis_history(
    current_user: dict = Depends(get_current_user),
):
    """Return the authenticated user's analysis history (most recent first)."""
    results = await analysis_service.get_user_history(current_user["sub"])

    return [
        AnalysisHistoryItem(
            id=r["_id"],
            resume_id=r.get("resume_id", ""),
            ats_score=r.get("ats_score", 0),
            matched_skills=r.get("matched_skills", []),
            missing_skills=r.get("missing_skills", []),
            suggestions=r.get("suggestions", []),
            created_at=str(r.get("created_at", "")),
        )
        for r in results
    ]


# ---------------------------------------------------------------------------
# GET /resumes
# ---------------------------------------------------------------------------

@router.get("/resumes", response_model=list[ResumeHistoryItem])
async def get_resumes(
    current_user: dict = Depends(get_current_user),
):
    """Return the authenticated user's uploaded resumes (most recent first)."""
    resumes = await analysis_service.get_user_resumes(current_user["sub"])

    return [
        ResumeHistoryItem(
            id=r["_id"],
            filename=r.get("filename", ""),
            upload_date=str(r.get("upload_date", "")),
            parsed_data=r.get("parsed_data", {}),
        )
        for r in resumes
    ]


# ---------------------------------------------------------------------------
# GET /resumes/{resume_id}
# ---------------------------------------------------------------------------

@router.get("/resumes/{resume_id}", response_model=ResumeHistoryItem)
async def get_resume_by_id(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Return a specific resume by ID (must belong to the authenticated user)."""
    resume = await analysis_service.get_resume_by_id(
        resume_id=resume_id,
        user_id=current_user["sub"],
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    return ResumeHistoryItem(
        id=resume["_id"],
        filename=resume.get("filename", ""),
        upload_date=str(resume.get("upload_date", "")),
        parsed_data=resume.get("parsed_data", {}),
    )
