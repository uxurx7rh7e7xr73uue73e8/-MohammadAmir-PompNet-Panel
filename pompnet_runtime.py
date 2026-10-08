import asyncio
import logging
import os
import re
from contextlib import suppress

from fastapi import (
    WebSocket,
    WebSocketDisconnect,
)

from pompnet_security import (
    SlidingRateLimiter,
)

from pompnet_xray import (
    ensure_xray,
    stop_xray,
    xray_running,
)


logger = logging.getLogger(
    "pompnet-runtime"
)


UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)


XRAY_HOST = "127.0.0.1"

XRAY_PORT = int(
    os.getenv(
        "POMPNET_XRAY_PORT",
        "10000",
    )
)


MAX_WS_CONNECTIONS = max(
    1,
    int(
        os.getenv(
            "POMPNET_MAX_WS_CONNECTIONS",
            "256",
        )
    ),
)


WS_HANDSHAKE_LIMIT = max(
    1,
    int(
        os.getenv(
            "POMPNET_WS_HANDSHAKE_LIMIT",
            "60",
        )
    ),
)


HANDSHAKE_WINDOW = max(
    1,
    int(
        os.getenv(
            "POMPNET_WS_HANDSHAKE_WINDOW",
            "60",
        )
    ),
)


_rate_limiter = (
    SlidingRateLimiter(
        limit=WS_HANDSHAKE_LIMIT,
        window=HANDSHAKE_WINDOW,
    )
)


_connections = 0

_connections_lock = (
    asyncio.Lock()
)


def valid_uuid(
    value: str,
):

    return bool(
        UUID_RE.fullmatch(
            str(
                value or ""
            ).strip()
        )
    )


def get_links():

    try:

        import main

        return main.LINKS

    except Exception:

        return {}


def get_link(
    uid: str,
):

    links = get_links()

    link = links.get(
        uid
    )

    if not isinstance(
        link,
        dict,
    ):
        return None

    return link


def allowed_uuid(
    uid: str,
):

    link = get_link(
        uid
    )

    if not link:
        return False

    try:

        from main import (
            is_link_allowed,
        )

        return bool(
            is_link_allowed(
                link
            )
        )

    except Exception:

        return bool(
            link.get(
                "active",
                True,
            )
        )


def client_ip(
    websocket: WebSocket,
):

    value = websocket.headers.get(
        "x-real-ip"
    )

    if value:
        return value.strip()

    value = websocket.headers.get(
        "x-forwarded-for"
    )

    if value:
        return (
            value
            .split(",")[0]
            .strip()
        )

    if websocket.client:
        return websocket.client.host

    return "unknown"


async def reserve_connection():

    global _connections

    async with _connections_lock:

        if (
            _connections
            >= MAX_WS_CONNECTIONS
        ):
            return False

        _connections += 1

        return True


async def release_connection():

    global _connections

    async with _connections_lock:

        _connections = max(
            0,
            _connections - 1,
        )


async def startup():

    try:

        ok = await asyncio.to_thread(
            ensure_xray,
            get_links(),
        )

        if ok:

            logger.info(
                "POMP NET Xray started"
            )

        else:

            logger.error(
                "POMP NET Xray failed to start"
            )

    except Exception:

        logger.exception(
            "Xray startup failed"
        )


async def shutdown():

    try:

        await asyncio.to_thread(
            stop_xray
        )

    except Exception:

        logger.exception(
            "Xray shutdown failed"
        )


async def proxy_websocket(
    websocket: WebSocket,
    uid: str,
):

    ip = client_ip(
        websocket
    )

    if not valid_uuid(uid):

        await websocket.close(
            code=1008,
            reason="invalid uuid",
        )

        return

    if not _rate_limiter.allow(
        ip
    ):

        await websocket.close(
            code=1008,
            reason="rate limit",
        )

        return

    if not allowed_uuid(
        uid
    ):

        await websocket.close(
            code=1008,
            reason="inactive or expired uuid",
        )

        return

    if not await reserve_connection():

        await websocket.close(
            code=1013,
            reason="server busy",
        )

        return

    try:

        ok = await asyncio.to_thread(
            ensure_xray,
            get_links(),
        )

        if (
            not ok
            or not xray_running()
        ):

            await websocket.close(
                code=1011,
                reason="xray unavailable",
            )

            return

        await websocket.accept()

        reader = None
        writer = None

        try:

            reader, writer = (
                await asyncio.open_connection(
                    XRAY_HOST,
                    XRAY_PORT,
                )
            )

            async def websocket_to_xray():

                while True:

                    message = (
                        await websocket.receive()
                    )

                    if (
                        message.get("type")
                        == "websocket.disconnect"
                    ):
                        return

                    data = message.get(
                        "bytes"
                    )

                    if data:

                        writer.write(
                            data
                        )

                        await writer.drain()

            async def xray_to_websocket():

                while True:

                    data = await reader.read(
                        65536
                    )

                    if not data:
                        return

                    await websocket.send_bytes(
                        data
                    )

            await asyncio.gather(
                websocket_to_xray(),
                xray_to_websocket(),
            )

        except (
            asyncio.CancelledError,
            ConnectionError,
            BrokenPipeError,
            ConnectionResetError,
            WebSocketDisconnect,
        ):
            pass

        except Exception:

            logger.exception(
                "VLESS WebSocket proxy error"
            )

        finally:

            if writer is not None:

                with suppress(Exception):

                    writer.close()

                    await writer.wait_closed()

            with suppress(Exception):

                await websocket.close()

    finally:

        await release_connection()
