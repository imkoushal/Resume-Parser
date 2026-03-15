"""
response_models.py - Pydantic schemas for API responses.

Defines structured response models used by the FastAPI endpoints to ensure
consistent, well-documented JSON output.
"""

from pydantic import BaseModel, Field
from typing import Optional


class HealthResponse(BaseModel):
    """Response for the GET /health endpoint."""
    status: str = Field(default="ok", examples=["ok"])


class EducationEntry(BaseModel):
    """A single education entry extracted from a resume."""
    degree: str = Field(..., examples=["B.Tech Computer Science 2020"])
    institution: Optional[str] = Field(default=None, examples=["MIT"])
    year: Optional[int] = Field(default=None, examples=[2020])


class ParsedResumeResponse(BaseModel):
    """Response for POST /parse-resume — full parsed resume data."""
    name: Optional[str] = Field(default=None, examples=["John Doe"])
    email: Optional[str] = Field(default=None, examples=["john@example.com"])
    phone: Optional[str] = Field(default=None, examples=["+1 234 567 8901"])
    skills: list[str] = Field(default_factory=list, examples=[["Python", "React", "Docker"]])
    education: list[EducationEntry] = Field(default_factory=list)
    years_of_experience: int = Field(default=0, examples=[5])


class SkillsResponse(BaseModel):
    """Response for POST /extract-skills — skills list only."""
    skills: list[str] = Field(default_factory=list, examples=[["Python", "React", "Docker"]])
    count: int = Field(default=0, examples=[3])


class JDRequirements(BaseModel):
    """Structured requirements extracted from a job description."""
    skills: list[str] = Field(default_factory=list)
    min_experience_years: Optional[int] = Field(default=None)
    education: list[str] = Field(default_factory=list)


class JDMatchResponse(BaseModel):
    """Response for POST /match-job-description — match analysis report."""
    match_score: float = Field(..., examples=[72.5])
    skill_score: float = Field(..., examples=[80.0])
    semantic_score: float = Field(..., examples=[55.0])
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    jd_skills: list[str] = Field(default_factory=list)
    resume_skills: list[str] = Field(default_factory=list)
    is_match: bool = Field(..., examples=[True])
    jd_requirements: JDRequirements


class SuggestionItem(BaseModel):
    """A single improvement suggestion."""
    category: str = Field(..., examples=["missing_skills"])
    message: str = Field(..., examples=["Add Docker to your resume."])


class AnalyzeResumeResponse(BaseModel):
    """Response for POST /analyze-resume — full analysis pipeline."""
    name: Optional[str] = Field(default=None, examples=["John Doe"])
    email: Optional[str] = Field(default=None, examples=["john@example.com"])
    skills: list[str] = Field(default_factory=list, examples=[["Python", "React"]])
    ats_score: float = Field(default=0.0, examples=[72.5])
    keyword_score: float = Field(default=0.0, examples=[65.0])
    skill_coverage_score: float = Field(default=0.0, examples=[80.0])
    experience_score: float = Field(default=0.0, examples=[60.0])
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[SuggestionItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Authentication models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Request body for POST /auth/register."""
    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=6, examples=["secret123"])
    full_name: str = Field(..., examples=["John Doe"])


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""
    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["secret123"])


class TokenResponse(BaseModel):
    """Response for POST /auth/login — JWT access token."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response for GET /auth/me — authenticated user info."""
    email: str
    full_name: str


# ---------------------------------------------------------------------------
# History models
# ---------------------------------------------------------------------------

class AnalysisHistoryItem(BaseModel):
    """A single analysis result from user history."""
    id: str
    resume_id: str
    ats_score: float
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[dict] = Field(default_factory=list)
    created_at: str


class ResumeHistoryItem(BaseModel):
    """A single resume from user history."""
    id: str
    filename: str
    upload_date: str
    parsed_data: dict

