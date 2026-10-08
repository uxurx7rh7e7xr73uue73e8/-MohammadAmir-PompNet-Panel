import hmac
import os

from fastapi import Header, HTTPException
from main import app

from pompnet_security import install_security


# ============================================================
# POMP NET SECURITY
# ============================================================

# امنیت روی همان اپ اصلی AHB اعمال می‌شود.
install_security(app)


# ============================================================
# RAILWAY HEALTH CHECK
# ============================================================

@app.get("/health")
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
# POMP NET STATUS TOKEN
# ============================================================

def status_token_ok(token: str | None):
    expected = os.getenv(
        "POMPNET_STATUS_TOKEN",
        "",
    ).strip()

    if not expected or not token:
        return False

    return hmac.compare_digest(
        token,
        expected,
    )


# ============================================================
# POMP NET XRAY STATUS
# ============================================================

@app.get("/api/pompnet/xray")
async def pompnet_xray_status(
    x_pompnet_token: str | None = Header(
        default=None
    ),
):
    """
    فقط وضعیت Xray را نشان می‌دهد.

    توجه:
    WebSocket اصلی را AHB مدیریت می‌کند.
    اینجا WebSocket جدید تعریف نمی‌کنیم تا
    با /ws/{uuid} اصلی AHB تداخل ایجاد نشود.
    """

    if not status_token_ok(
        x_pompnet_token
    ):
        raise HTTPException(
            status_code=404,
            detail="not found",
        )

    from pompnet_xray import get_xray_status

    return get_xray_status()


# ============================================================
# POMP NET SECURITY STATUS
# ============================================================

@app.get("/api/pompnet/security")
async def pompnet_security_status():

    return {
        "security": "enabled",

        # VLESS WebSocket توسط Core اصلی AHB
        "websocket_proxy": "ahb-core",

        # پورت عمومی جداگانه برای Xray باز نمی‌کنیم
        "xray_public_port": False,

        # Endpoint وضعیت محافظت شده است
        "status_endpoint_protected": True,
    }
