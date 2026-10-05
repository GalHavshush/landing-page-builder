"""A small in-memory sliding-window rate limiter for the login/registration endpoints.

Limits brute-force password guessing and signup spam. It is per process: with several API
workers each keeps its own counts, so a production deployment should also rate limit at the
reverse proxy. Behind a proxy set BUILDER_TRUST_PROXY=true so the real client IP is used.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.config import get_settings


class RateLimiter:
    def __init__(self, max_attempts: int, window_seconds: int):
        self.max_attempts = max_attempts
        self.window = window_seconds
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.monotonic()
        hits = self.hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.max_attempts:
            retry = int(self.window - (now - hits[0])) + 1
            raise HTTPException(
                429,
                "Too many attempts. Please wait a few minutes.",
                headers={"Retry-After": str(retry)},
            )
        hits.append(now)

    def reset(self) -> None:
        self.hits.clear()


def client_ip(request: Request) -> str:
    if get_settings().trust_proxy:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


login_limiter = RateLimiter(max_attempts=15, window_seconds=300)
register_limiter = RateLimiter(max_attempts=8, window_seconds=3600)
stock_limiter = RateLimiter(max_attempts=60, window_seconds=60)


def limit_login(request: Request) -> None:
    if get_settings().rate_limit_enabled:
        login_limiter.check(client_ip(request))


def limit_register(request: Request) -> None:
    if get_settings().rate_limit_enabled:
        register_limiter.check(client_ip(request))


def limit_stock(user_id: int) -> None:
    if get_settings().rate_limit_enabled:
        stock_limiter.check(f"stock:{user_id}")
