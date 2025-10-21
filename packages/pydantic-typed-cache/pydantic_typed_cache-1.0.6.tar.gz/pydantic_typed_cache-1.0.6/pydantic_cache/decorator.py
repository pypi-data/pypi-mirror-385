import asyncio
import functools
import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from inspect import isawaitable, iscoroutinefunction
from typing import (
    Any,
    ParamSpec,
    TypeVar,
    get_type_hints,
)

from pydantic import BaseModel, TypeAdapter

from pydantic_cache.coder import Coder
from pydantic_cache.sentinel import CACHE_MISS
from pydantic_cache.types import KeyBuilder

logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
P = ParamSpec("P")
R = TypeVar("R")


def cache(
    expire: int | None = None,
    coder: type[Coder] | Coder | None = None,
    key_builder: KeyBuilder | None = None,
    namespace: str = "",
    model: Any = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Cache decorator for async functions
    :param namespace: cache key namespace
    :param expire: cache expiration time in seconds
    :param coder: encoder/decoder for cache values
    :param key_builder: function to build cache keys
    :param model: optional type to force conversion of cached values (can be any type)
    :return: decorated function
    """

    def wrapper(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        # Get return type hint if available, or use model if specified
        if model is not None:
            return_type = model
        else:
            try:
                type_hints = get_type_hints(func)
                return_type = type_hints.get("return", None)
            except Exception:
                return_type = None

        def convert_to_type(value: Any, target_type: Any) -> Any:
            """Convert value to target type using TypeAdapter.

            Args:
                value: The value to convert
                target_type: The target type to convert to

            Returns:
                Converted value, or original value if conversion fails
            """
            if target_type is None or value is None:
                return value

            try:
                adapter = TypeAdapter(target_type)
                # If value is a BaseModel, dump it first for proper conversion
                if isinstance(value, BaseModel):
                    return adapter.validate_python(value.model_dump())
                return adapter.validate_python(value)
            except Exception:
                logger.debug(f"Failed to convert value to {target_type}, keeping original type", exc_info=True)
                return value

        @wraps(func)
        async def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal coder
            nonlocal expire
            nonlocal key_builder

            async def ensure_async_func(*args: P.args, **kwargs: P.kwargs) -> R:
                """Run sync functions in thread pool for compatibility."""
                if iscoroutinefunction(func):
                    # async, return as is
                    return await func(*args, **kwargs)
                else:
                    # sync, wrap in thread and return async
                    loop = asyncio.get_event_loop()
                    partial_func = functools.partial(func, *args, **kwargs)
                    return await loop.run_in_executor(None, partial_func)  # type: ignore

            # Import here to avoid circular import
            from pydantic_cache import PydanticCache

            if not PydanticCache.get_enable():
                return await ensure_async_func(*args, **kwargs)

            prefix = PydanticCache.get_prefix()
            # Handle both class and instance coders
            if coder is None:
                coder = PydanticCache.get_coder()
            elif isinstance(coder, type):
                # If it's a class, instantiate it
                coder = coder()
            # else it's already an instance, use as-is

            expire = expire or PydanticCache.get_expire()
            key_builder = key_builder or PydanticCache.get_key_builder()
            backend = PydanticCache.get_backend()

            cache_key = key_builder(
                func,
                f"{prefix}:{namespace}",
                args=args,
                kwargs=kwargs,
            )
            if isawaitable(cache_key):
                cache_key = await cache_key
            assert isinstance(cache_key, str)

            try:
                _, cached = await backend.get_with_ttl(cache_key)
            except Exception:
                logger.warning(
                    f"Error retrieving cache key '{cache_key}' from backend:",
                    exc_info=True,
                )
                cached = CACHE_MISS

            if cached is CACHE_MISS:  # cache miss
                result = await ensure_async_func(*args, **kwargs)
                # Convert to target type using TypeAdapter
                result = convert_to_type(result, return_type)

                to_cache = coder.encode(result)

                try:
                    await backend.set(cache_key, to_cache, expire)
                except Exception:
                    logger.warning(
                        f"Error setting cache key '{cache_key}' in backend:",
                        exc_info=True,
                    )
            else:  # cache hit
                decoded = coder.decode(cached)
                # Convert to target type using TypeAdapter
                result = convert_to_type(decoded, return_type)

            return result

        return inner

    return wrapper
