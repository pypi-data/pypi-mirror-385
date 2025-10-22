"""Response caching for vigil-ai to reduce API costs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from vigil_ai.config import get_config


def get_cache_dir() -> Path:
    """Get cache directory path.

    Returns:
        Path to cache directory

    Examples:
        >>> cache_dir = get_cache_dir()
        >>> print(cache_dir)
        .vigil-ai-cache
    """
    config = get_config()
    cache_dir = Path(config.cache_dir)
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


def cache_key(prompt: str, model: str, **kwargs: Any) -> str:
    """Generate cache key from prompt and parameters.

    Args:
        prompt: The prompt text
        model: Model name
        **kwargs: Additional parameters

    Returns:
        Cache key (hex digest)

    Examples:
        >>> key = cache_key("Test prompt", "claude-3-5-sonnet")
        >>> print(len(key))
        64
    """
    # Create deterministic hash from all parameters
    data = {
        "prompt": prompt,
        "model": model,
        **kwargs,
    }

    # Sort keys for consistency
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def get_cached_response(key: str) -> str | None:
    """Get cached response if it exists.

    Args:
        key: Cache key

    Returns:
        Cached response or None if not found

    Examples:
        >>> response = get_cached_response("abc123...")
        >>> if response:
        ...     print("Cache hit!")
    """
    config = get_config()
    if not config.cache_responses:
        return None

    cache_file = get_cache_dir() / f"{key}.json"

    if not cache_file.exists():
        return None

    try:
        with open(cache_file) as f:
            data = json.load(f)
            return data.get("response")
    except Exception:
        return None


def cache_response(key: str, response: str, metadata: dict[str, Any] | None = None) -> None:
    """Cache a response.

    Args:
        key: Cache key
        response: Response text to cache
        metadata: Optional metadata to store

    Examples:
        >>> cache_response("abc123", "Generated pipeline...")
    """
    config = get_config()
    if not config.cache_responses:
        return

    cache_file = get_cache_dir() / f"{key}.json"

    try:
        data = {
            "response": response,
            "metadata": metadata or {},
        }

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

    except Exception:
        # Silently fail - caching is not critical
        pass


def clear_cache() -> int:
    """Clear all cached responses.

    Returns:
        Number of files deleted

    Examples:
        >>> deleted = clear_cache()
        >>> print(f"Cleared {deleted} cached responses")
    """
    cache_dir = get_cache_dir()
    count = 0

    for cache_file in cache_dir.glob("*.json"):
        try:
            cache_file.unlink()
            count += 1
        except Exception:
            pass

    return count


def cached(func: Callable) -> Callable:
    """Decorator to cache function results.

    Args:
        func: Function to cache

    Returns:
        Wrapped function with caching

    Examples:
        >>> @cached
        ... def generate_pipeline(prompt):
        ...     # Expensive API call
        ...     return result
    """

    def wrapper(prompt: str, *args: Any, **kwargs: Any) -> str:
        # Generate cache key
        model = kwargs.get("model", get_config().model)
        key = cache_key(prompt, model, **kwargs)

        # Check cache
        cached_response = get_cached_response(key)
        if cached_response is not None:
            return cached_response

        # Call function
        response = func(prompt, *args, **kwargs)

        # Cache result
        cache_response(key, response, {
            "model": model,
            "args": args,
            "kwargs": kwargs,
        })

        return response

    return wrapper
