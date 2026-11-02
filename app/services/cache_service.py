import redis.asyncio as redis
import json
from typing import Any, Optional
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.redis: Optional[redis.Redis] = None
        self.default_ttl = 900  # 15 minutes

    async def connect(self):
        """Establish Redis connection if not already connected"""
        if self.redis is None:
            self.redis = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def get_indicator(self, ioc_value: str) -> Optional[dict]:
        """Get cached STIX 2.1 payload for an IoC"""
        await self.connect()
        try:
            cached = await self.redis.get(f"ioc:{ioc_value}")
            if cached:
                return json.loads(cached)
            return None
        except redis.RedisError as e:
            print(f"Redis get error: {e}")
            return None

    async def set_indicator(self, ioc_value: str, stix_payload: dict, ttl: int = None) -> bool:
        """Cache STIX 2.1 payload for an IoC"""
        await self.connect()
        try:
            ttl = ttl or self.default_ttl
            await self.redis.setex(
                f"ioc:{ioc_value}",
                ttl,
                json.dumps(stix_payload, default=str)
            )
            return True
        except redis.RedisError as e:
            print(f"Redis set error: {e}")
            return False

    async def invalidate_indicator(self, ioc_value: str) -> bool:
        """Invalidate cached entry for an IoC"""
        await self.connect()
        try:
            await self.redis.delete(f"ioc:{ioc_value}")
            return True
        except redis.RedisError as e:
            print(f"Redis delete error: {e}")
            return False

    async def health_check(self) -> dict:
        """Check Redis connectivity status"""
        try:
            await self.connect()
            await self.redis.ping()
            return {"status": "healthy", "latency": "0ms"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


cache_service = CacheService()