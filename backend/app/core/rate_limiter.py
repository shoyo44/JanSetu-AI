"""
Tenant Sliding-Window Rate Limiter.

Protects DocsAI from denial-of-service, API credit exhaustion, and tenant resource starvation
using an in-memory sliding-window log. Works out of the box with zero external dependencies
(no Redis required).
"""
from __future__ import annotations

import logging
import os
import threading
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException

logger = logging.getLogger("docqa.security.rate_limiter")

# Default action limits (requests per window)
DEFAULT_LIMITS: Dict[str, int] = {
    "upload": 20,       # 20 document uploads per hour per tenant
    "query": 150,       # 150 RAG queries per hour per tenant
    "detect": 30,       # 30 classification requests per hour per tenant
    "export": 50,       # 50 audit exports per hour per tenant
}

WINDOW_SECONDS = 3600   # 1 hour window


class TenantRateLimiter:
    """
    Thread-safe sliding-window rate limiter per tenant and action.
    """

    def __init__(self, window_seconds: int = WINDOW_SECONDS):
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        # Key format: f"{action}:{tenant_id}" -> list of timestamps
        self._history: Dict[str, List[float]] = defaultdict(list)

    def _get_limit(self, action: str) -> int:
        env_key = f"RATE_LIMIT_{action.upper()}_PER_HOUR"
        if env_key in os.environ:
            try:
                return int(os.environ[env_key])
            except ValueError:
                pass
        return DEFAULT_LIMITS.get(action, 100)

    def check(
        self,
        tenant_id: str,
        action: str = "query",
        ip_address: Optional[str] = None,
    ) -> Tuple[bool, int, int]:
        """
        Records an attempt and checks if within rate limits.

        Returns:
            (allowed: bool, remaining: int, retry_after: int)
        """
        # If rate limiting is globally disabled via env
        if os.getenv("DISABLE_RATE_LIMITING", "false").lower() in ("true", "1", "yes"):
            return True, 999, 0

        now = time.time()
        window_start = now - self.window_seconds
        limit = self._get_limit(action)
        key = f"{action}:{tenant_id or 'anonymous'}"

        with self._lock:
            # Purge timestamps outside the current window
            timestamps = self._history[key]
            valid_timestamps = [t for t in timestamps if t > window_start]
            self._history[key] = valid_timestamps

            if len(valid_timestamps) >= limit:
                # Rate limit exceeded.
                oldest_in_window = valid_timestamps[0]
                retry_after = max(1, int(oldest_in_window + self.window_seconds - now))
                logger.warning(
                    "⚠️ Rate limit exceeded for tenant '%s' on action '%s' (count=%d, limit=%d). Retry after %ds.",
                    tenant_id, action, len(valid_timestamps), limit, retry_after,
                )
                return False, 0, retry_after

            # Allow and append current timestamp
            valid_timestamps.append(now)
            remaining = max(0, limit - len(valid_timestamps))
            return True, remaining, 0

    def enforce(
        self,
        tenant_id: str,
        action: str = "query",
        ip_address: Optional[str] = None,
    ) -> None:
        """
        Enforces rate limits. Raises FastAPI HTTPException(429) if exceeded.
        """
        allowed, remaining, retry_after = self.check(tenant_id, action=action, ip_address=ip_address)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "action": action,
                    "tenant_id": tenant_id,
                    "limit_per_hour": self._get_limit(action),
                    "retry_after_seconds": retry_after,
                    "message": f"Tenant '{tenant_id}' has exceeded the {action} quota. Please retry in {retry_after} seconds.",
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self._get_limit(action)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                },
            )

    def get_status(self, tenant_id: str) -> Dict[str, Any]:
        """Returns quota usage across all actions for a tenant."""
        now = time.time()
        window_start = now - self.window_seconds
        usage = {}

        with self._lock:
            for action, default_cap in DEFAULT_LIMITS.items():
                limit = self._get_limit(action)
                key = f"{action}:{tenant_id}"
                timestamps = [t for t in self._history.get(key, []) if t > window_start]
                usage[action] = {
                    "limit": limit,
                    "used": len(timestamps),
                    "remaining": max(0, limit - len(timestamps)),
                    "window_seconds": self.window_seconds,
                }
        return usage


# Singleton instance
tenant_limiter = TenantRateLimiter()
