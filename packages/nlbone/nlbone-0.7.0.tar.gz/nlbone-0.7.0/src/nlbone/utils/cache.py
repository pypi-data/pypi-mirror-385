import asyncio
import inspect
import json
from typing import Any, Callable, Iterable, Optional

from makefun import wraps as mf_wraps

from nlbone.utils.cache_registry import get_cache

try:
    from pydantic import BaseModel  # v1/v2
except Exception:  # pragma: no cover

    class BaseModel:  # minimal fallback
        pass


# -------- helpers --------


def _bind(func: Callable, args, kwargs):
    sig = inspect.signature(func)
    bound = sig.bind_partial(*args, **kwargs)
    bound.apply_defaults()
    return bound


def _key_from_template(
    tpl: Optional[str],
    func: Callable,
    args,
    kwargs,
) -> str:
    """Format key template with bound arguments or build a stable default."""
    bound = _bind(func, args, kwargs)
    if tpl:
        return tpl.format(**bound.arguments)

    # Default stable key: module:qualname:sha of args
    payload = json.dumps(bound.arguments, sort_keys=True, default=str)
    return f"{func.__module__}:{func.__qualname__}:{hash(payload)}"


def _format_tags(
    tag_tpls: Optional[Iterable[str]],
    func: Callable,
    args,
    kwargs,
) -> list[str] | None:
    if not tag_tpls:
        return None
    bound = _bind(func, args, kwargs)
    return [t.format(**bound.arguments) for t in tag_tpls]


def default_serialize(val: Any) -> bytes:
    """Serialize BaseModel (v2/v1) or JSON-serializable data to bytes."""
    if isinstance(val, BaseModel):
        if hasattr(val, "model_dump_json"):  # pydantic v2
            return val.model_dump_json().encode("utf-8")
        if hasattr(val, "json"):  # pydantic v1
            return val.json().encode("utf-8")
    return json.dumps(val, default=str).encode("utf-8")


def default_deserialize(b: bytes) -> Any:
    return json.loads(b)


def _is_async_method(obj: Any, name: str) -> bool:
    meth = getattr(obj, name, None)
    return asyncio.iscoroutinefunction(meth)


def _run_maybe_async(func: Callable, *args, **kwargs):
    """Call a function that may be async from sync context."""
    result = func(*args, **kwargs)
    if inspect.isawaitable(result):
        return asyncio.run(result)
    return result


# -------- cache decorators --------


def cached(
    *,
    ttl: int,
    key: str | None = None,
    tags: Iterable[str] | None = None,
    serializer: Callable[[Any], bytes] = default_serialize,
    deserializer: Callable[[bytes], Any] = default_deserialize,
    cache_resolver: Optional[Callable[[], Any]] = None,
):
    """
    Framework-agnostic caching for SYNC or ASYNC callables.
    - Preserves function signature (good for FastAPI/OpenAPI).
    - Works with sync/async cache backends (CachePort / AsyncCachePort).
    - `key` & `tags` are string templates, e.g. "file:{file_id}".
    """

    def deco(func: Callable):
        is_async_func = asyncio.iscoroutinefunction(func)

        if is_async_func:

            @mf_wraps(func)
            async def aw(*args, **kwargs):
                cache = (cache_resolver or get_cache)()
                k = _key_from_template(key, func, args, kwargs)
                tg = _format_tags(tags, func, args, kwargs)

                # GET
                if _is_async_method(cache, "get"):
                    cached_bytes = await cache.get(k)
                else:
                    cached_bytes = cache.get(k)

                if cached_bytes is not None:
                    return deserializer(cached_bytes)

                # MISS -> compute
                result = await func(*args, **kwargs)

                # SET
                data = serializer(result)
                if _is_async_method(cache, "set"):
                    await cache.set(k, data, ttl=ttl, tags=tg)
                else:
                    cache.set(k, data, ttl=ttl, tags=tg)

                return result

            return aw

        # SYNC callable
        @mf_wraps(func)
        def sw(*args, **kwargs):
            cache = (cache_resolver or get_cache)()
            k = _key_from_template(key, func, args, kwargs)
            tg = _format_tags(tags, func, args, kwargs)

            # GET (may be async)
            if _is_async_method(cache, "get"):
                cached_bytes = _run_maybe_async(cache.get, k)
            else:
                cached_bytes = cache.get(k)

            if cached_bytes is not None:
                return deserializer(cached_bytes)

            # MISS -> compute
            result = func(*args, **kwargs)

            # SET (may be async)
            data = serializer(result)
            if _is_async_method(cache, "set"):
                _run_maybe_async(cache.set, k, data, ttl=ttl, tags=tg)
            else:
                cache.set(k, data, ttl=ttl, tags=tg)

            return result

        return sw

    return deco


def invalidate_by_tags(tags_builder: Callable[..., Iterable[str]]):
    """
    Invalidate computed tags after function finishes.
    Works with sync or async functions and cache backends.
    """

    def deco(func: Callable):
        is_async_func = asyncio.iscoroutinefunction(func)

        if is_async_func:

            @mf_wraps(func)
            async def aw(*args, **kwargs):
                out = await func(*args, **kwargs)
                cache = get_cache()
                tags = list(tags_builder(*args, **kwargs))
                if _is_async_method(cache, "invalidate_tags"):
                    await cache.invalidate_tags(tags)
                else:
                    cache.invalidate_tags(tags)
                return out

            return aw

        @mf_wraps(func)
        def sw(*args, **kwargs):
            out = func(*args, **kwargs)
            cache = get_cache()
            tags = list(tags_builder(*args, **kwargs))
            if _is_async_method(cache, "invalidate_tags"):
                _run_maybe_async(cache.invalidate_tags, tags)
            else:
                cache.invalidate_tags(tags)
            return out

        return sw

    return deco
