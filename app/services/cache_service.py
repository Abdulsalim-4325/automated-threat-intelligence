import json
import redis.asyncio as redis
from typing import Optional, Dict, Any
from app.core.config import settings

class CacheService:
    """Async Redis cache for STIX indicators."""
    
    def __init__(self):
        # decode_responses=True automatically converts Redis bytes to Python strings
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.ttl = settings.CACHE_TTL_SECONDS

    async def get_indicator(self, ioc_value: str) -> Optional[Dict[str, Any]]:
        """Fetch an indicator from Redis."""
        data = await self.redis_client.get(f"ioc:{ioc_value}")
        if data:
            return json.loads(data)
        return None

    async def set_indicator(self, ioc_value: str, payload: Dict[str, Any]):
        """Store an indicator in Redis with a TTL."""
        await self.redis_client.setex(
            f"ioc:{ioc_value}",
            self.ttl,
            json.dumps(payload)
        )

    async def invalidate_indicator(self, ioc_value: str):
        """Remove an indicator from the cache (used when score updates)."""
        await self.redis_client.delete(f"ioc:{ioc_value}")

    async def health_check(self) -> Dict[str, str]:
        """Ping Redis for health monitoring."""
        try:
            await self.redis_client.ping()
            return {"status": "healthy", "message": "Redis connection successful"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}

cache_service = CacheService()