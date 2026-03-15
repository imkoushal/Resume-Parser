"""
analysis_service.py - Persistence service for resume analyses.

Stores resume uploads and analysis results in MongoDB and retrieves
user history.
"""

from bson import ObjectId

from src.core.database import resumes_collection, analysis_collection
from src.models.db_models import create_resume_document, create_analysis_document


# ---------------------------------------------------------------------------
# Store operations
# ---------------------------------------------------------------------------

async def store_resume(
    user_id: str,
    filename: str,
    parsed_data: dict,
) -> str:
    """
    Store a parsed resume document.

    Returns:
        The inserted document's ID as a string.
    """
    doc = create_resume_document(user_id, filename, parsed_data)
    result = await resumes_collection().insert_one(doc)
    return str(result.inserted_id)


async def store_analysis(
    user_id: str,
    resume_id: str,
    analysis_data: dict,
) -> str:
    """
    Store an analysis result linked to a user and resume.

    Returns:
        The inserted document's ID as a string.
    """
    doc = create_analysis_document(user_id, resume_id, analysis_data)
    result = await analysis_collection().insert_one(doc)
    return str(result.inserted_id)


# ---------------------------------------------------------------------------
# Retrieve operations
# ---------------------------------------------------------------------------

async def get_user_history(user_id: str, limit: int = 50) -> list[dict]:
    """
    Get analysis history for a user, most recent first.

    Returns:
        List of analysis result documents.
    """
    cursor = (
        analysis_collection()
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def get_user_resumes(user_id: str, limit: int = 50) -> list[dict]:
    """
    Get all resumes uploaded by a user, most recent first.

    Returns:
        List of resume documents.
    """
    cursor = (
        resumes_collection()
        .find({"user_id": user_id})
        .sort("upload_date", -1)
        .limit(limit)
    )
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def get_resume_by_id(resume_id: str, user_id: str) -> dict | None:
    """
    Get a specific resume by ID, scoped to the authenticated user.

    Returns:
        The resume document, or None if not found / not owned.
    """
    try:
        obj_id = ObjectId(resume_id)
    except Exception:
        return None

    doc = await resumes_collection().find_one({
        "_id": obj_id,
        "user_id": user_id,
    })

    if doc is not None:
        doc["_id"] = str(doc["_id"])

    return doc
