"""redis.py"""
import os
from typing import Tuple

import redis.asyncio as redis
import redis as redis_sync

from extended_fastapi_redis_cache.enums import RedisStatus

async def redis_connect_async(host_url: str) -> Tuple[RedisStatus, redis.client.Redis]:
    """Attempt to connect to `host_url` and return a Redis client instance if successful."""
    return await _connect_async(host_url)

def redis_connect(host_url: str) -> Tuple[RedisStatus, redis.client.Redis]:
    """Attempt to connect to `host_url` and return a Redis client instance if successful."""
    return _connect(host_url)

async def _connect_async(host_url: str) -> Tuple[RedisStatus, redis.client.Redis]:  # pragma: no cover
    try:
        client = redis.Redis.from_url(url=host_url)
        if await client.ping():
            return (RedisStatus.CONNECTED, client)
        return (RedisStatus.CONN_ERROR, None)
    except redis.AuthenticationError:
        return (RedisStatus.AUTH_ERROR, None)
    except redis.ConnectionError:
        return (RedisStatus.CONN_ERROR, None)
    except Exception as e:
        print(f"Exception: {e}")

def _connect(host_url: str) -> Tuple[RedisStatus, redis.client.Redis]:  # pragma: no cover
    try:
        client: redis_sync.Redis = redis_sync.Redis.from_url(url=host_url)
        if client.ping():
            return (RedisStatus.CONNECTED, client)
        return (RedisStatus.CONN_ERROR, None)
    except redis.AuthenticationError:
        return (RedisStatus.AUTH_ERROR, None)
    except redis.ConnectionError:
        return (RedisStatus.CONN_ERROR, None)
    except Exception as e:
        print(f"Exception: {e}")


def _connect_fake() -> Tuple[RedisStatus, redis.client.Redis]:
    return
    # from fakeredis import FakeRedis
    # return (RedisStatus.CONNECTED, FakeRedis())
