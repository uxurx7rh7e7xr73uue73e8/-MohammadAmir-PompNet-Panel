from fastapi import WebSocket

from main import app

from pompnet_runtime import (
    startup,
    shutdown,
    proxy_websocket,
)


@app.on_event("startup")
async def pompnet_xray_startup():
    await startup()


@app.on_event("shutdown")
async def pompnet_xray_shutdown():
    await shutdown()


@app.websocket("/ws/{uid}")
async def pompnet_vless_websocket(
    websocket: WebSocket,
    uid: str,
):
    await proxy_websocket(
        websocket,
        uid,
    )


@app.get("/api/pompnet/xray")
async def pompnet_xray_status():
    from pompnet_xray import get_xray_status

    return get_xray_status()
