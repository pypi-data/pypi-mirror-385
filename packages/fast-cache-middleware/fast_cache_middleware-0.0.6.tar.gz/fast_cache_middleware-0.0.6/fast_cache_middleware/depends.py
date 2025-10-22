import re
from typing import Awaitable, Callable, Optional, Union

from fastapi import params
from starlette.requests import Request

SyncOrAsync = Union[Callable[[Request], str], Callable[[Request], Awaitable[str]]]


class BaseCacheConfigDepends(params.Depends):
    """Base class for cache configuration via ASGI scope extensions.

    Uses standardized ASGI extensions mechanism for passing
    configuration from route dependencies to middleware.
    """

    use_cache: bool = True

    def __call__(self, request: Request) -> None:
        pass


class CacheConfig(BaseCacheConfigDepends):
    """Cache configuration for route.

    Args:
        max_age: Cache lifetime in seconds
        key_func: Cache key generation function
    """

    def __init__(
        self,
        max_age: int = 5 * 60,
        key_func: Optional[SyncOrAsync] = None,
    ) -> None:
        self.max_age = max_age
        self.key_func = key_func

        self.dependency = self


class CacheDropConfig(BaseCacheConfigDepends):
    """Cache invalidation configuration for route.

    Args:
        paths: Path for cache invalidation. Can be string or regular expression.
            If string, it will be converted to regular expression
            that matches the beginning of request path.
    """

    def __init__(
        self,
        paths: list[str | re.Pattern] | None = None,
        methods: list[Callable] | None = None,
    ) -> None:
        self.paths: list[re.Pattern] = [
            p if isinstance(p, re.Pattern) else re.compile(f"^{p}") for p in paths or []
        ]
        self.methods: list[Callable] = methods or []

        self.dependency = self
