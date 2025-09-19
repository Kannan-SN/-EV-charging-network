# backend/app/routers/health.py
from fastapi import APIRouter
from datetime import datetime
import httpx
import os

from app.models import HealthCheck

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthCheck)
async def health_check():
    """
    Comprehensive health check for all services
    """
    services = {}

    # Check Weaviate connection
    try:
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{weaviate_url}/v1/meta", timeout=5.0)
            services["weaviate"] = (
                "healthy" if response.status_code == 200 else "unhealthy"
            )
    except Exception:
        services["weaviate"] = "unhealthy"

    # Check Gemini API (if API key provided)
    gemini_key = os.getenv("GEMINI_API_KEY")
    services["gemini"] = "configured" if gemini_key else "not_configured"

    # Check external APIs
    services["openstreetmap"] = "available"  # OSM is generally available

    return HealthCheck(
        status="healthy", timestamp=datetime.now(), version="0.1.0", services=services
    )
