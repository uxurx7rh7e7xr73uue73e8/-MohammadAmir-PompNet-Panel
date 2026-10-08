import hmac
import os

from fastapi import (
    Header,
    HTTPException,
    WebSocket,
)

from main import app

from pompnet_security import (
    install_security,
)

from pompnet_runtime import (
    startup,
    shutdown,
    proxy_websocket,
)


# امنیت روی اپ اصلی اعمال می‌شود
install_security(
    app
)


@app.on_event(
    "startup"
)
async def pompnet_xray_startup():

    await startup()


@app.on_event(
    "shutdown"
)
async def pompnet_xray_shutdown():

    await shutdown()


# VLESS WebSocket واقعی
@app.websocket(
    "/ws/{uid}"
)
async def pompnet_vless_websocket(
    websocket: WebSocket,
    uid: str,
):

    await proxy_websocket(
        websocket,
        uid,
    )


def status_token_ok(
    token: str | None,
):

    expected = os.getenv(
        "POMPNET_STATUS_TOKEN",
        "",
    ).strip()

    if (
        not expected
        or not token
    ):
        return False

    return hmac.compare_digest(
        token,
        expected,
    )


@app.get(
    "/api/pompnet/xray"
)
async def pompnet_xray_status(
    x_pompnet_token: str | None = Header(
        default=None
    ),
):

    if not status_token_ok(
        x_pompnet_token
    ):

        raise HTTPException(
            status_code=404,
            detail="not found",
        )

    from pompnet_xray import (
        get_xray_status,
    )

    return get_xray_status()


@app.get(
    "/api/pompnet/security"
)
async def pompnet_security_status():

    return {
        "security": "enabled",
        "websocket_proxy": "enabled",
        "xray_public_port": False,
        "status_endpoint_protected": True,
    }
