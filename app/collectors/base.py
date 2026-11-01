import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, Any, Optional

class BaseCollector:
    """Abstract base collector handling HTTP connections, timeouts, and rate-limit retries."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.headers = {"User-Agent": "STIXThreatEngine/1.0 (Research)"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def fetch_json(self, url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Executes an async HTTP request with exponential backoff for rate limits."""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method, url, headers=self.headers, timeout=15.0, **kwargs
            )
            response.raise_for_status()
            return response.json()