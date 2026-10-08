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


# ============================================================
# POMP NET SECURITY
# ============================================================

# امنیت روی اپ اصلی اعمال می‌شود
install_security(
    app
)


# ============================================================
# RAILWAY HEALTH CHECK
# ============================================================

@app.get(
    "/health"
)
async def health_check():
    """
    Railway health check.
    این مسیر عمومی است و برای بررسی زنده بودن پنل
    نیازی به Login یا Xray ندارد.
    """

    return {
        "ok": True,
        "service": "POMP NET",
        "status": "healthy",
    }


# ============================================================
# POMP NET XRAY STARTUP
# ============================================================

@app.on_event(
    "startup"
)
async def pompnet_xray_startup():

    await startup()


# ============================================================
# POMP NET XRAY SHUTDOWN
# ============================================================

@app.on_event(
    "shutdown"
)
async def pompnet_xray_shutdown():

    await shutdown()


# ============================================================
# REAL VLESS WEBSOCKET
# ============================================================

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


# ============================================================
# POMP NET XRAY STATUS
# ============================================================

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


# ============================================================
# POMP NET SECURITY STATUS
# ============================================================

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
