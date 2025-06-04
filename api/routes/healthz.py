"""
FastAPI route for the /healthz endpoint.

This is a simple health check for Kubernetes orchestration.
"""

from datetime import datetime, timezone
from typing import Dict
from fastapi import APIRouter, status
from ..config import settings

route = APIRouter()


@route.get(
    "/healthz",
    summary="Simple service health check.",
    tags=["main"],
    status_code=status.HTTP_200_OK,
)
async def get_healthz() -> Dict[str, str]:
    """
    Health check endpoint returns API metadata and current UTC time.
    """
    return {
        "status": "ok",
        "api": settings.version,
        "version": settings.releaseId,
        "description": "github webhook receiver",
        "time (UTC)": datetime.now(tz=timezone.utc).isoformat(),
    }
