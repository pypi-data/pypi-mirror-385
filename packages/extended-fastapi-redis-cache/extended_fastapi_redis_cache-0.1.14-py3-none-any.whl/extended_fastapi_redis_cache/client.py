import logging
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Tuple, Type, Union

from extended_fastapi_redis_cache.enums import RedisEvent, RedisStatus
from extended_fastapi_redis_cache.key_gen import get_cache_key
from extended_fastapi_redis_cache.redis import redis_connect, redis_connect_async
from extended_fastapi_redis_cache.util import serialize_json
from fastapi import Request, Response
from redis.asyncio import client

DEFAULT_RESPONSE_HEADER = "X-FastAPI-Cache"
# ALLOWED_HTTP_TYPES = ["GET"]
ALLOWED_HTTP_TYPE = "GET"
LOG_TIMESTAMP = "%m/%d/%Y %I:%M:%S %p"
HTTP_TIME = "%a, %d %b %Y %H:%M:%S GMT"

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MetaSingleton(type):
    """Metaclass for creating classes that allow only a single instance to be created."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class FastApiRedisCache(metaclass=MetaSingleton):
    """Communicates with Redis server to cache API response data."""

    host_url: str
    prefix: str = None
    response_header: str = None
    status: RedisStatus = RedisStatus.NONE
    redis: client.Redis = None

    @property
    def connected(self):
        return self.status == RedisStatus.CONNECTED

    @property
    def not_connected(self):
        return not self.connected

    def init(
        self,
        host_url: str,
        prefix: Optional[str] = None,
        response_header: Optional[str] = None,
        ignore_arg_types: Optional[List[Type[object]]] = None,
    ) -> None:
        """Connect to a Redis database using `host_url` and configure cache settings.

        Args:
            host_url (str): URL for a Redis database.
            prefix (str, optional): Prefix to add to every cache key stored in the
                Redis database. Defaults to None.
            response_header (str, optional): Name of the custom header field used to
                identify cache hits/misses. Defaults to None.
            ignore_arg_types (List[Type[object]], optional): Each argument to the
                API endpoint function is used to compose the cache key. If there
                are any arguments that have no effect on the response (such as a
                `Request` or `Response` object), including their type in this list
                will ignore those arguments when the key is created. Defaults to None.
        """
        self.host_url = host_url
        self.prefix = prefix
        self.response_header = response_header or DEFAULT_RESPONSE_HEADER
        self.ignore_arg_types = ignore_arg_types

    async def connect_async(self):    
        await self._connect_async()

    def connect(self):    
        self._connect()

    async def _connect_async(self):
        self.log(RedisEvent.CONNECT_BEGIN, msg="Attempting to connect to Redis server...")
        self.status, self.redis = await redis_connect_async(self.host_url)
        if self.status == RedisStatus.CONNECTED:
            self.log(RedisEvent.CONNECT_SUCCESS, msg="Redis client is connected to server.")
        if self.status == RedisStatus.AUTH_ERROR:  # pragma: no cover
            self.log(RedisEvent.CONNECT_FAIL, msg="Unable to connect to redis server due to authentication error.")
        if self.status == RedisStatus.CONN_ERROR:  # pragma: no cover
            self.log(RedisEvent.CONNECT_FAIL, msg="Redis server did not respond to PING message.")
    
    def _connect(self):
        self.log(RedisEvent.CONNECT_BEGIN, msg="Attempting to connect to Redis server...")
        self.status, self.redis = redis_connect(self.host_url)
        if self.status == RedisStatus.CONNECTED:
            self.log(RedisEvent.CONNECT_SUCCESS, msg="Redis client is connected to server.")
        if self.status == RedisStatus.AUTH_ERROR:  # pragma: no cover
            self.log(RedisEvent.CONNECT_FAIL, msg="Unable to connect to redis server due to authentication error.")
        if self.status == RedisStatus.CONN_ERROR:  # pragma: no cover
            self.log(RedisEvent.CONNECT_FAIL, msg="Redis server did not respond to PING message.")

    def request_is_not_cacheable(self, request: Request) -> bool:
        return request and (
            request.method != ALLOWED_HTTP_TYPE
            or any(directive in request.headers.get("Cache-Control", "") for directive in ["no-store", "no-cache"])
        )

    def get_cache_key(self, func: Callable, *args: List, **kwargs: Dict) -> str:
        return get_cache_key(self.prefix, self.ignore_arg_types, func, *args, **kwargs)

    async def check_cache_async(self, key: str) -> str:
        in_cache = await self.redis.get(key)
        if in_cache:
            self.log(RedisEvent.KEY_FOUND_IN_CACHE, key=key)
        return in_cache

    def check_cache(self, key: str) -> str:
        in_cache = self.redis.get(key)
        if in_cache:
            self.log(RedisEvent.KEY_FOUND_IN_CACHE, key=key)
        return in_cache


    async def add_to_cache_async(self, key: str, value: Dict, expire: int) -> bool:
        response_data = None
        try:
            response_data = serialize_json(value)
        except TypeError:
            message = f"Object of type {type(value)} is not JSON-serializable"
            self.log(RedisEvent.FAILED_TO_CACHE_KEY, msg=message, key=key)
            return False
        cached = await self.redis.set(name=key, value=response_data, ex=expire)
        if cached:
            self.log(RedisEvent.KEY_ADDED_TO_CACHE, key=key)
        else:  # pragma: no cover
            self.log(RedisEvent.FAILED_TO_CACHE_KEY, key=key, value=value)
        return cached
    
    def add_to_cache(self, key: str, value: Dict, expire: int) -> bool:
        response_data = None
        try:
            response_data = serialize_json(value)
        except TypeError:
            message = f"Object of type {type(value)} is not JSON-serializable"
            self.log(RedisEvent.FAILED_TO_CACHE_KEY, msg=message, key=key)
            return False
        cached = self.redis.set(name=key, value=response_data, ex=expire)
        if cached:
            self.log(RedisEvent.KEY_ADDED_TO_CACHE, key=key)
        else:  # pragma: no cover
            self.log(RedisEvent.FAILED_TO_CACHE_KEY, key=key, value=value)
        return cached
    
    async def extend_cache_async(self, key: str, ttl: int) -> bool:
        extended = await self.redis.expire(key, ttl)
        if extended:
            self.log(RedisEvent.KEY_EXTENDED, key=key)
        else:
            self.log(RedisEvent.FAILED_TO_EXTEND_KEY, key=key)

    def extend_cache(self, key: str, ttl: int) -> bool:
        extended = self.redis.expire(key, ttl)
        if extended:
            self.log(RedisEvent.KEY_EXTENDED, key=key)
        else:
            self.log(RedisEvent.FAILED_TO_EXTEND_KEY, key=key)

    async def expire_entire_router_cache_async(
        self, 
        router: str, 
        account_id: int, 
        user_label: str = "current_user",
        exclude_routes: Optional[List[str]] = None,
        log_time_execution: bool = False
    ) -> None:
        exp_msg = ""
        if log_time_execution:
            start = time.time()
        keys = await self.redis.keys(f"{self.prefix}:api*.routes.{router}.*{user_label}=_{account_id}_*")
        
        if keys:
            keys = self._filter_keys_excluding_routes(exclude_routes, keys)
        
        if keys:
            await self.redis.delete(*keys)
            if log_time_execution:
                exp_msg = f" - Expire operation took {(time.time() - start) * 1000} ms."
            self.log(RedisEvent.ENTIRE_ENDPOINT_CACHE_EXPIRED, msg=f"Router: {router}, account_id: {account_id} {exp_msg}")
    
    def expire_entire_router_cache(
        self, 
        router: str, 
        account_id: int, 
        user_label: str = "current_user",
        exclude_routes: Optional[List[str]] = None,
        log_time_execution: bool = False
    ) -> None:
        exp_msg = ""
        if log_time_execution:
            start = time.time()
        keys = self.redis.keys(f"{self.prefix}:api*.routes.{router}.*{user_label}=_{account_id}_*")
       
        if keys:
            keys = self._filter_keys_excluding_routes(exclude_routes, keys)

        if keys:
            self.redis.delete(*keys)
            if log_time_execution:
                exp_msg = f" - Expire operation took {(time.time() - start) * 1000} ms."
            self.log(RedisEvent.ENTIRE_ENDPOINT_CACHE_EXPIRED, msg=f"Router: {router}, account_id: {account_id} {exp_msg}")

    async def expire_endpoint_cache_async(
        self, 
        router: str, 
        endpoint: str, 
        account_id: int, 
        user_label: str = "current_user",
        log_time_execution: bool = False
    ) -> None:
        exp_msg = ""
        if log_time_execution:
            start = time.time()
        keys = await self.redis.keys(f"{self.prefix}:api*.routes.{router}.{endpoint}*{user_label}=_{account_id}_*")
        if keys:
            await self.redis.delete(*keys)
            if log_time_execution:
                exp_msg = f" - Expire operation took {(time.time() - start) * 1000} ms."
            self.log(RedisEvent.EXPIRE_ENDPOINT_CACHE, msg=f"Expired single endpoint cache {router}.{endpoint}, account_id: {account_id} {exp_msg}")
    
    def expire_endpoint_cache(
        self, 
        router: str, 
        endpoint: str, 
        account_id: int, 
        user_label: str = "current_user",
        log_time_execution: bool = False
    ) -> None:
        exp_msg = ""
        if log_time_execution:
            start = time.time()
        keys = self.redis.keys(f"{self.prefix}:api*.routes.{router}.{endpoint}*{user_label}=_{account_id}_*")
        if keys:
            self.redis.delete(*keys)
            if log_time_execution:
                exp_msg = f" - Expire operation took {(time.time() - start) * 1000} ms."
            self.log(RedisEvent.EXPIRE_ENDPOINT_CACHE, msg=f"Expired single endpoint cache {router}.{endpoint}, account_id: {account_id} {exp_msg}")

    def set_response_headers(
        self, 
        response: Response, 
        cache_hit: bool, 
    ) -> None:
        response.headers[self.response_header] = "Hit" if cache_hit else "Miss"

    def _filter_keys_excluding_routes(self, excluding_routes: Optional[List[str]], keys: List[bytes]) -> List[bytes]:
        if not excluding_routes:
            return keys
        
        try:
            # filter the keys to exclude any that contain the excluding_routes
            filtered_keys = []
            for key in keys:
                key_str = key.decode('utf-8')
                # Keep the key only if it doesn't match any of the excluding_routes
                if not any(route in key_str for route in excluding_routes):
                    filtered_keys.append(key)
            return filtered_keys
        except Exception as e:
            self.log(RedisEvent.FAILED_TO_CACHE_KEY, msg=f"Error filtering excluding_routes: {e}")
            return keys  # Return all keys if filtering fails

    def log(self, event: RedisEvent, msg: Optional[str] = None, key: Optional[str] = None, value: Optional[str] = None):
        """Log `RedisEvent` using the configured `Logger` object"""
        message = f" {self.get_log_time()} | {event.name}"
        if msg:
            message += f": {msg}"
        if key:
            message += f": key={key}"
        if value:  # pragma: no cover
            message += f", value={value}"
        logger.info(message)

    @staticmethod
    def get_log_time():
        """Get a timestamp to include with a log message."""
        return datetime.now().strftime(LOG_TIMESTAMP)
