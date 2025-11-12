"""Simple caching layer."""
import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# In-memory cache
_memory_cache: dict[str, tuple[Any, datetime]] = {}

# File cache directory
CACHE_DIR = Path("./data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def memory_cache(ttl_minutes: int = 15):
    """In-memory cache decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check if cached and not expired
            if cache_key in _memory_cache:
                value, expiry = _memory_cache[cache_key]
                if datetime.now() < expiry:
                    logger.debug(f"Cache HIT (memory): {cache_key[:50]}...")
                    return value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            expiry = datetime.now() + timedelta(minutes=ttl_minutes)
            _memory_cache[cache_key] = (result, expiry)
            logger.debug(f"Cache MISS (memory): {cache_key[:50]}...")

            return result
        return wrapper
    return decorator


def file_cache(ttl_hours: int = 3):
    """File-based cache decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            cache_file = CACHE_DIR / f"{cache_key}.json"

            # Check if cached file exists and not expired
            if cache_file.exists():
                file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_age < timedelta(hours=ttl_hours):
                    try:
                        with open(cache_file, "r") as f:
                            logger.debug(f"Cache HIT (file): {cache_key}")
                            return json.load(f)
                    except Exception as e:
                        logger.warning(f"Error reading cache file: {e}")

            # Execute function
            result = await func(*args, **kwargs)

            # Store in file
            try:
                with open(cache_file, "w") as f:
                    json.dump(result, f)
                logger.debug(f"Cache MISS (file): {cache_key}")
            except Exception as e:
                logger.warning(f"Error writing cache file: {e}")

            return result
        return wrapper
    return decorator


def clear_cache():
    """Clear all caches."""
    _memory_cache.clear()
    for cache_file in CACHE_DIR.glob("*.json"):
        try:
            cache_file.unlink()
        except Exception as e:
            logger.warning(f"Error deleting cache file {cache_file}: {e}")
    logger.info("Cache cleared")
