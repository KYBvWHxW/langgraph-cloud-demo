from redis import Redis
from typing import Optional, Any, Dict, Union
import json
import os
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "")
        self.enabled = bool(self.redis_url)
        self._redis: Optional[Redis] = None
        
        if self.enabled:
            try:
                self._redis = Redis.from_url(self.redis_url)
                logger.info("Redis cache enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Redis: {e}")
                self.enabled = False
        else:
            logger.info("Redis cache disabled - REDIS_URL not set")

    async def get(self, key: str) -> Optional[Any]:
        if not self.enabled or not self._redis:
            return None
        try:
            value = self._redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        if not self.enabled or not self._redis:
            return False
        try:
            self._redis.setex(key, expire, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.enabled or not self._redis:
            return False
        try:
            return bool(self._redis.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

def cache_response(expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_instance = getattr(wrapper, "_cache", None)
            if not cache_instance:
                cache_instance = Cache()
                setattr(wrapper, "_cache", cache_instance)

            if not cache_instance.enabled:
                return await func(*args, **kwargs)

            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_result = await cache_instance.get(cache_key)
            
            if cached_result is not None:
                return cached_result

            result = await func(*args, **kwargs)
            await cache_instance.set(cache_key, result, expire)
            return result
        return wrapper
    return decorator
