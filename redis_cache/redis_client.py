import redis
import json
import os
from typing import Optional, Any


class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = redis.from_url(self.redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Set value in Redis with expiration (default 5 minutes)"""
        try:
            serialized_value = json.dumps(value, default=str)
            return self.client.setex(key, expire, serialized_value)
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis DELETE PATTERN error: {e}")
            return 0


redis_client = RedisClient()
