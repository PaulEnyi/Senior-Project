import time
import asyncio
import functools
import logging

logger = logging.getLogger("app.timing")

def async_timed(name: str = None):
    """Decorator to measure duration of sync/async function execution and log milliseconds.
    Usage:
        @async_timed("my_operation")
        async def op(...): ...
    """
    def decorator(func):
        is_async = asyncio.iscoroutinefunction(func)

        if not is_async:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    duration_ms = (time.perf_counter() - start) * 1000.0
                    logger.info(f"[TIMING] {name or func.__name__} duration_ms={duration_ms:.2f}")
            return sync_wrapper

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                duration_ms = (time.perf_counter() - start) * 1000.0
                logger.info(f"[TIMING] {name or func.__name__} duration_ms={duration_ms:.2f}")
        return async_wrapper
    return decorator

__all__ = ["async_timed"]
