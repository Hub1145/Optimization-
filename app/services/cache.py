import redis
import json
from typing import Any, Optional
from app.config import settings

class CacheService:
    """Redis cache service"""

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: Any, expire: int = 3600):
        self.redis.set(key, json.dumps(value), ex=expire)

    def delete(self, key: str):
        self.redis.delete(key)
