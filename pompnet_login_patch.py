import os
from pathlib import Path

MAIN = Path("/app/main.py")

if not MAIN.exists():
    raise SystemExit("ERROR: /app/main.py not found")

text = MAIN.read_text(encoding="utf-8")

# ============================================================
# REAL POMP NET LOGIN
# ============================================================

old_auth = '''_env_pw = os.environ.get("ADMIN_PASSWORD", "").strip()
AUTH = {
    "password_hash": hash_password(_env_pw) if _env_pw else "",
    "password_configured": bool(_env_pw),
}'''

new_auth = '''_env_user = os.environ.get(
    "ADMIN_USERNAME",
    "admin",
).strip().lower()

_env_pw = os.environ.get(
    "ADMIN_PASSWORD",
    "admin",
).strip()

AUTH = {
    "username": _env_user or "admin",
    "password_hash": hash_password(_env_pw) if _env_pw else "",
    "password_configured": bool(_env_pw),
}'''

if old_auth not in text:
    raise SystemExit(
        "ERROR: real AUTH block not found; stopped safely"
    )

text = text.replace(
    old_auth,
    new_auth,
    1,
)

# ============================================================
# JSON LOGIN
# ============================================================

old_json = '''            password = str(
                body.get(
                    "password",
                    "",
                )
            ).strip()'''

new_json = '''            username = str(
                body.get(
                    "username",
                    "",
                )
            ).strip().lower()

            password = str(
                body.get(
                    "password",
                    "",
                )
            ).strip()'''

if old_json not in text:
    raise SystemExit(
        "ERROR: real JSON login block not found"
    )

text = text.replace(
    old_json,
    new_json,
    1,
)

# ============================================================
# FORM LOGIN
# ============================================================

old_form = '''            password = (
                parsed.get(
                    "password",
                    [""],
                )[0]
                .strip()
            )'''

new_form = '''            username = (
                parsed.get(
                    "username",
                    [""],
                )[0]
                .strip()
                .lower()
            )

            password = (
                parsed.get(
                    "password",
                    [""],
                )[0]
                .strip()
            )'''

if old_form not in text:
    raise SystemExit(
        "ERROR: real form login block not found"
    )

text = text.replace(
    old_form,
    new_form,
    1,
)

# ============================================================
# REAL USERNAME VALIDATION
# ============================================================

old_check = '''    if not password:
        register_login_failure(ip)
        return HTMLResponse(
            login_error_html(
                "رمز عبور را وارد کنید."
            ),
            status_code=400,
        )

    if (
        hash_password(password)
        != AUTH["password_hash"]
    ):'''

new_check = '''    if not username:
        username = AUTH.get(
            "username",
            "admin",
        )

    if username != AUTH.get(
        "username",
        "admin",
    ):
        register_login_failure(ip)

        return HTMLResponse(
            login_error_html(
                "نام کاربری یا رمز عبور اشتباه است."
            ),
            status_code=401,
        )

    if not password:
        register_login_failure(ip)

        return HTMLResponse(
            login_error_html(
                "رمز عبور را وارد کنید."
            ),
            status_code=400,
        )

    if (
        hash_password(password)
        != AUTH["password_hash"]
    ):'''

if old_check not in text:
    raise SystemExit(
        "ERROR: real password validation block not found"
    )

text = text.replace(
    old_check,
    new_check,
    1,
)

# ============================================================
# FINAL CHECKS
# ============================================================

if "ADMIN_USERNAME" not in text:
    raise SystemExit(
        "ERROR: ADMIN_USERNAME patch failed"
    )

if 'AUTH["username"]' not in text and 'AUTH.get(' not in text:
    raise SystemExit(
        "ERROR: username validation patch failed"
    )

MAIN.write_text(
    text,
    encoding="utf-8",
)

print("POMP NET REAL LOGIN PATCH: OK")
print("USERNAME: admin")
print("PASSWORD: configured")
