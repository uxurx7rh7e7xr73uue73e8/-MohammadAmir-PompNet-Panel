import os
from pathlib import Path

MAIN = Path("/app/main.py")

if not MAIN.exists():
    raise SystemExit("ERROR: /app/main.py not found")

text = MAIN.read_text(encoding="utf-8")

# ============================================================
# REAL POMP NET LOGIN CONFIG
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

if old_auth in text:
    text = text.replace(old_auth, new_auth, 1)
elif '"username": _env_user or "admin"' not in text:
    raise SystemExit(
        "ERROR: real AUTH block not found; stopped safely"
    )

# ============================================================
# REAL OWNER USERNAME
# ============================================================

old_owner_check = '''    if username and username not in ("owner", "admin", "root"):'''

new_owner_check = '''    if username and username != AUTH.get("username", "admin") and username not in ("owner", "admin", "root"):'''

if old_owner_check in text:
    text = text.replace(old_owner_check, new_owner_check, 1)
elif new_owner_check not in text:
    raise SystemExit(
        "ERROR: real /api/login owner check not found; stopped safely"
    )

# ============================================================
# SAFETY CHECKS
# ============================================================

required = (
    'AUTH = {',
    '"username": _env_user or "admin"',
    'ADMIN_USERNAME',
    'document.getElementById(\'loginUser\').value',
    '"/api/login"',
)

for marker in required:
    if marker not in text:
        raise SystemExit(
            f"ERROR: required login marker missing: {marker}"
        )

MAIN.write_text(
    text,
    encoding="utf-8",
)

print("POMP NET REAL LOGIN PATCH: OK")
print("OWNER USERNAME: ADMIN_USERNAME")
print("DEFAULT USERNAME: admin")
print("DEFAULT PASSWORD: admin")
