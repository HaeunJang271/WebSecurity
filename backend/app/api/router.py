"""
Main API router
"""
from fastapi import APIRouter

from app.api.endpoints import auth, scans, vulnerabilities, reports

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["인증"]
)

api_router.include_router(
    scans.router,
    prefix="/scans",
    tags=["스캔"]
)

api_router.include_router(
    vulnerabilities.router,
    prefix="/vulnerabilities",
    tags=["취약점"]
)

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["보고서"]
)

