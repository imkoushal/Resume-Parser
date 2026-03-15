"""
config.py - Centralized configuration for the Resume Intelligence Platform.

All path constants, API metadata, database settings, and authentication
parameters are defined here.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

# Project root directory (two levels up from this file: core/ → src/ → root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Path to the curated skills list used by SkillExtractor and dependents
SKILLS_FILE_PATH = str(PROJECT_ROOT / "data" / "skills_list.txt")

# ---------------------------------------------------------------------------
# API metadata
# ---------------------------------------------------------------------------

API_TITLE = "Resume Intelligence Platform"
API_DESCRIPTION = (
    "REST API for parsing resumes, extracting skills, "
    "matching candidates against job descriptions, "
    "and tracking resume improvements over time."
)
API_VERSION = "2.0.0"

# ---------------------------------------------------------------------------
# MongoDB
# ---------------------------------------------------------------------------

MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DATABASE = "resume_intelligence"

# ---------------------------------------------------------------------------
# JWT Authentication
# ---------------------------------------------------------------------------

JWT_SECRET_KEY = "resume-intelligence-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 60 * 24  # 24 hours
