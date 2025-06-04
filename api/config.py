"""
Configuration module for the GitHub webhook receiver API.

Defines app-level settings, route prefixes, and environment-driven options.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """base settings"""

    title: str = "github-webhook-receiver"
    description: str = "Python FastAPI-based GitHub webhook receiver."
    prefix: str = "/webhook"
    debug: bool = False
    releaseId: str = Field(
        default_factory=lambda: os.environ.get("API_VERSION", "snapshot")
    )
    version: str = "v1"
    server_info_url: str = "http://localhost:15000/server_info"


settings = Settings()
route_prefix = f"/{settings.version}{settings.prefix}"

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "secret_not_set")
MAX_PAYLOAD_SIZE = 2 * 1024 * 1024  # 2MB
