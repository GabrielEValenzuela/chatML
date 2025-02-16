"""
    This module contains the Redis client for caching results.
    The Redis client is used to cache similarity results for faster retrieval.
    
    The module provides two functions:
    - get_cached_results: Retrieves cached results from Redis.
    - set_cached_results: Sets cached results in Redis.
    
    
    Also, the module is used to verify the user's rate limit
"""

import json
import os
import redis
from typing import List, Tuple

from functools import lru_cache


@lru_cache(maxsize=1)
def get_redis_client():
    """
    Returns a Redis client instance. Uses environment variables:
      REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
    """

    return redis.Redis.from_url(
        os.getenv("REDIS_URI", "redis://localhost:6379"),
        decode_responses=True,
        max_connections=10
    )


def get_cached_results(key) -> List[Tuple[str, float]]:
    """
    Retrieves cached results from Redis and ensures numbers remain floats.

    :param key: The key to retrieve from Redis.

    Returns a list of [URI, score] pairs.
    """
    cached_data = get_redis_client().get(key)
    if cached_data:
        # Ensure correct structure
        return {"cache": True, "result": json.loads(cached_data)}
    return None  # No cache available


def set_cached_results(key, results: List[Tuple[str, float]]) -> bool:
    """
    Sets cached results in Redis.

    :param key: The key to set in Redis.
    :param results: The results to cache.
    """
    # Convert to JSON string
    json_results = json.dumps(results)
    get_redis_client().set(key, json_results)
    return True
