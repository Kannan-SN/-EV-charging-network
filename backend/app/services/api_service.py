
import httpx
import asyncio
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class ExternalAPIService:
    """Service for making calls to external APIs with rate limiting and error handling"""

    def __init__(self):
        self.session = None
        self.rate_limiter = asyncio.Semaphore(10)  # Max 10 concurrent requests

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=settings.external_api_timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def get(
        self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make GET request with rate limiting"""
        async with self.rate_limiter:
            try:
                response = await self.session.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for URL {url}")
                raise
            except Exception as e:
                logger.error(f"Request failed for URL {url}: {e}")
                raise

    async def post(
        self, url: str, json_data: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make POST request with rate limiting"""
        async with self.rate_limiter:
            try:
                response = await self.session.post(url, json=json_data, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for URL {url}")
                raise
            except Exception as e:
                logger.error(f"Request failed for URL {url}: {e}")
                raise
