"""
POMP NET Security Layer
Independent security layer.
Does not modify AHB/POMP NET state files.
"""

import os
import time
from collections import defaultdict, deque
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware


def get_allowed_hosts():
    raw = os.getenv(
        "POMPNET_ALLOWED_HOSTS",
        "",
    ).strip()

    if not raw:
        return []

    return [
        item.strip()
        for item in raw.split(",")
        if item.strip()
    ]


class SecurityHeadersMiddleware(
    BaseHTTPMiddleware
):

    async def dispatch(
        self,
        request,
        call_next,
    ):
        response = await call_next(
            request
        )

        response.headers.setdefault(
            "X-Content-Type-Options",
            "nosniff",
        )

        response.headers.setdefault(
            "X-Frame-Options",
            "SAMEORIGIN",
        )

        response.headers.setdefault(
            "Referrer-Policy",
            "strict-origin-when-cross-origin",
        )

        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )

        response.headers.setdefault(
            "Cross-Origin-Resource-Policy",
            "same-site",
        )

        if (
            os.getenv(
                "POMPNET_HSTS",
                "0",
            ).strip()
            == "1"
        ):
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )

        return response


class SlidingRateLimiter:

    def __init__(
        self,
        limit=60,
        window=60,
        max_keys=10000,
    ):
        self.limit = max(
            1,
            int(limit),
        )

        self.window = max(
            1,
            int(window),
        )

        self.max_keys = max(
            100,
            int(max_keys),
        )

        self.items = defaultdict(
            deque
        )

        self.lock = Lock()

    def allow(
        self,
        key,
    ):
        now = time.monotonic()

        with self.lock:

            bucket = self.items[key]

            cutoff = (
                now
                - self.window
            )

            while (
                bucket
                and bucket[0]
                <= cutoff
            ):
                bucket.popleft()

            if (
                len(bucket)
                >= self.limit
            ):
                return False

            bucket.append(
                now
            )

            if (
                len(self.items)
                > self.max_keys
            ):
                stale = [
                    k
                    for k, v
                    in self.items.items()
                    if not v
                    or v[-1]
                    <= cutoff
                ]

                for key_name in stale[
                    :max(
                        1,
                        len(stale) // 2,
                    )
                ]:
                    self.items.pop(
                        key_name,
                        None,
                    )

            return True


def install_security(app):

    allowed_hosts = (
        get_allowed_hosts()
    )

    if allowed_hosts:

        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts,
        )

    app.add_middleware(
        SecurityHeadersMiddleware
    )

    return app
