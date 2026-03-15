"""
app.py - FastAPI entry point for the Resume Intelligence Platform.

Run with:
    uvicorn app:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import API_TITLE, API_DESCRIPTION, API_VERSION
from src.core.database import connect_db, close_db
from src.routes.resume_routes import router as resume_router
from src.routes.auth_routes import router as auth_router
from src.routes.history_routes import router as history_router


# ---------------------------------------------------------------------------
# Application lifecycle — connect/disconnect MongoDB
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: open DB connection.  Shutdown: close DB connection."""
    await connect_db()
    yield
    await close_db()


# ---------------------------------------------------------------------------
# Create FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS middleware — permissive for development; lock down in production
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

app.include_router(resume_router)
app.include_router(auth_router)
app.include_router(history_router)
