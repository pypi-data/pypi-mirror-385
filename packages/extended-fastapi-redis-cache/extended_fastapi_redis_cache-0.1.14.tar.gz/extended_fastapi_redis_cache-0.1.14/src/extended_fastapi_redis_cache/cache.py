"""cache.py"""
import asyncio
from datetime import timedelta
from functools import partial, update_wrapper, wraps
from http import HTTPStatus
from typing import Any, Optional, Union

from extended_fastapi_redis_cache.client import FastApiRedisCache
from extended_fastapi_redis_cache.enums import RedisEvent
from extended_fastapi_redis_cache.util import (
    ONE_DAY_IN_SECONDS,
    ONE_HOUR_IN_SECONDS,
    ONE_MONTH_IN_SECONDS,
    ONE_WEEK_IN_SECONDS,
    ONE_YEAR_IN_SECONDS,
    deserialize_json,
    serialize_json,
)
from fastapi import Response


def cache(
    *, 
    response_model: Any = None,
    expire: Union[int, timedelta] = ONE_YEAR_IN_SECONDS,
    extend_expire_on_hit: bool = False,
    set_cache_header_values_on_hit: Optional[bool] = None
):
    """Enable caching behavior for the decorated function.

    Args:
        response_model (Any, optional): The response model to use for serialization. Defaults to None.

        expire (Union[int, timedelta], optional): The number of seconds
            from now when the cached response should expire. Defaults to 31,536,000
            seconds (i.e., the number of seconds in one year).
        
        extend_expire_on_hit (bool): If True, the cached response will be extended
            by the number of seconds specified in the `expire` parameter on each cache hit. 
            Defaults to False.

        set_cache_header_values_on_hit (bool): If True, we properly set the `expires`, `cache-control` and `etag` header values.
            Defaults to True.
    """

    def outer_wrapper(func):
        @wraps(func)
        async def inner_wrapper(*args, **kwargs):
            """Return cached value if one exists, otherwise evaluate the wrapped function and cache the result."""

            if set_cache_header_values_on_hit is not None:
                print("set_cache_header_values_on_hit is deprecated and will be removed in a future release. For now, ignoring the value provided.")

            func_kwargs = kwargs.copy()
            request = func_kwargs.pop("request", None)
            response = func_kwargs.pop("response", None)
            create_response_directly = not response
            
            if create_response_directly:
                
                response = Response()

                # remove default 0 content-length header
                # in lower portion of the code the content-length header will be set correctly based on actual content
                if response.headers.get("content-length"):
                    del response.headers["content-length"]
            
            redis_cache = FastApiRedisCache()

            if redis_cache.not_connected or redis_cache.request_is_not_cacheable(request):
                # if the redis client is not connected or request is not cacheable, no caching behavior is performed.
                return await get_api_response_async(func, *args, **kwargs)

            key = redis_cache.get_cache_key(func, *args, **kwargs)
            in_cache = await redis_cache.check_cache_async(key)
            
            if in_cache:
            
                # if the extend_expire_on_hit flag is set to True, we set the cache ttl to the expire time.
                # effectively we reset the expiration time on each subsequent request.
                # This is used when we manually expire the cache through code. 
                if extend_expire_on_hit:
                    await redis_cache.extend_cache_async(key, expire)
                    ttl = expire

                redis_cache.set_response_headers(
                    response=response, 
                    cache_hit=True, 
                )
                
                if create_response_directly:
                    return Response(
                        content=in_cache, 
                        media_type="application/json", 
                        headers=response.headers
                    )
                
                return deserialize_json(in_cache)

            response_data = await get_api_response_async(func, *args, **kwargs)
            ttl = calculate_ttl(expire)

            if response_model is not None:
                if hasattr(response_model, "from_orm"):
                    response_data = response_model.from_orm(response_data)
                if not hasattr(response_model, "from_orm"):
                    if response_model._name == "List":
                        list_type = response_model.__args__[0]
                        formatted_response_data = [list_type.from_orm(item) for item in response_data]
                        response_data = formatted_response_data
                    else:
                        print("response_model must be a List - unhandled type provided")
            
                        redis_cache.log(
                            RedisEvent.FAILED_TO_CACHE_KEY, 
                            msg="response_model must be a List - unhandled type provided", 
                            key=key
                        )
                        return response_data

            cached = await redis_cache.add_to_cache_async(key, response_data, ttl)

            if cached:
                redis_cache.set_response_headers(
                    response, 
                    cache_hit=False, 
                )
                response = Response(
                    content=serialize_json(response_data), media_type="application/json", headers=response.headers
                )
                
                if create_response_directly:
                    return response

                return response_data

            print("Failed to cache response - inspect the logs for more information")
            
            redis_cache.log(
                RedisEvent.FAILED_TO_CACHE_KEY, 
                msg="Failed to cache response - inspect Response Model if it needs to be set!", 
                key=key
            )
            
            return response_data

        return inner_wrapper

    return outer_wrapper


async def get_api_response_async(func, *args, **kwargs):
    """Helper function that allows decorator to work with both async and non-async functions."""
    return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)


def calculate_ttl(expire: Union[int, timedelta]) -> int:
    """"Converts expire time to total seconds and ensures that ttl is capped at one year."""
    if isinstance(expire, timedelta):
        expire = int(expire.total_seconds())
    return min(expire, ONE_YEAR_IN_SECONDS)


cache_one_minute = partial(cache, expire=60)
cache_one_hour = partial(cache, expire=ONE_HOUR_IN_SECONDS)
cache_one_day = partial(cache, expire=ONE_DAY_IN_SECONDS)
cache_one_week = partial(cache, expire=ONE_WEEK_IN_SECONDS)
cache_one_month = partial(cache, expire=ONE_MONTH_IN_SECONDS)
cache_one_year = partial(cache, expire=ONE_YEAR_IN_SECONDS)

update_wrapper(cache_one_minute, cache)
update_wrapper(cache_one_hour, cache)
update_wrapper(cache_one_day, cache)
update_wrapper(cache_one_week, cache)
update_wrapper(cache_one_month, cache)
update_wrapper(cache_one_year, cache)
