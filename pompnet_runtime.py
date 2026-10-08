import asyncio
import logging
import re
from contextlib import suppress

from fastapi import WebSocket, WebSocketDisconnect

from pompnet_xray import (
    ensure_xray,
    stop_xray,
    xray_running,
)

logger = logging.getLogger("pompnet-runtime")

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)

XRAY_HOST = "127.0.0.1"
XRAY_PORT = 10000


def valid_uuid(value: str) -> bool:
    return bool(UUID_RE.fullmatch(str(value or "").strip()))


def get_links():
    try:
        import main
        return main.LINKS
    except Exception:
        return {}


def allowed_uuid(uid: str) -> bool:
    links = get_links()
    link = links.get(uid)

    if not isinstance(link, dict):
        return False

    if link.get("active", True) is False:
        return False

    return True


async def startup():
    try:
        ok = await asyncio.to_thread(
            ensure_xray,
            get_links(),
        )

        if ok:
            logger.info(
                "POMP NET Xray Core started successfully"
            )
        else:
            logger.warning(
                "POMP NET Xray Core could not be started"
            )

    except Exception:
        logger.exception(
            "Xray startup failed"
        )


async def shutdown():
    try:
        await asyncio.to_thread(stop_xray)
    except Exception:
        logger.exception(
            "Xray shutdown failed"
        )


async def proxy_websocket(websocket: WebSocket, uid: str):
    if not valid_uuid(uid):
        await websocket.close(
            code=1008,
            reason="invalid uuid"
        )
        return

    if not allowed_uuid(uid):
        await websocket.close(
            code=1008,
            reason="inactive uuid"
        )
        return

    try:
        await asyncio.to_thread(
            ensure_xray,
            get_links(),
        )
    except Exception:
        logger.exception(
            "Xray refresh failed"
        )

    if not xray_running():
        await websocket.close(
            code=1011,
            reason="xray unavailable"
        )
        return

    await websocket.accept()

    reader = None
    writer = None

    try:
        reader, writer = await asyncio.open_connection(
            XRAY_HOST,
            XRAY_PORT,
        )

        async def websocket_to_xray():
            while True:
                message = await websocket.receive()

                if message.get("type") == "websocket.disconnect":
                    return

                data = message.get("bytes")

                if data:
                    writer.write(data)
                    await writer.drain()

        async def xray_to_websocket():
            while True:
                data = await reader.read(65536)

                if not data:
                    return

                await websocket.send_bytes(data)

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
