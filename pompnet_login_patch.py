from pathlib import Path

MAIN = Path("/app/main.py")

if not MAIN.exists():
    raise SystemExit("ERROR: /app/main.py not found")

text = MAIN.read_text(encoding="utf-8")


# ============================================================
# REAL POMP NET OWNER LOGIN CONFIG
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
        "ERROR: AHB AUTH block not found; stopped safely"
    )


# ============================================================
# REAL OWNER / ADMIN LOGIN
# ============================================================

old_login = '''    meta = {"role": "owner", "admin_id": None, "username": "owner"}
    ok = False
    if username and username not in ("owner", "admin", "root"):
        aid, admin = find_admin_by_username(username)
        if admin and admin.get("password_hash") == hash_password(password):
            if not admin_is_valid(admin):
                raise HTTPException(status_code=403, detail="حساب مسدود یا منقضی شده است")
            ok = True
            meta = {"role": "admin", "admin_id": aid, "username": username}
    else:
        if hash_password(password) == AUTH["password_hash"]:
            ok = True'''

new_login = '''    owner_username = str(
        AUTH.get(
            "username",
            "admin",
        )
        or "admin"
    ).strip().lower()

    meta = {
        "role": "owner",
        "admin_id": None,
        "username": owner_username,
    }

    ok = False

    # ========================================================
    # REAL OWNER LOGIN
    # ========================================================

    # ورود مالک با username تنظیم‌شده در ADMIN_USERNAME
    # یا حالت قدیمی بدون username
    if (
        not username
        or username == owner_username
    ):
        if hash_password(
            password
        ) == AUTH["password_hash"]:

            ok = True

            meta = {
                "role": "owner",
                "admin_id": None,
                "username": owner_username,
            }

    # ========================================================
    # REAL AHB SUB-ADMIN LOGIN
    # ========================================================

    elif username:
        aid, admin = find_admin_by_username(
            username
        )

        if (
            admin
            and admin.get(
                "password_hash"
            ) == hash_password(password)
        ):

            if not admin_is_valid(
                admin
            ):
                raise HTTPException(
                    status_code=403,
                    detail="حساب مسدود یا منقضی شده است",
                )

            ok = True

            meta = {
                "role": "admin",
                "admin_id": aid,
                "username": username,
            }'''

if old_login in text:
    text = text.replace(
        old_login,
        new_login,
        1,
    )

elif 'owner_username = str(' not in text:
    raise SystemExit(
        "ERROR: real /api/login block not found; stopped safely"
    )


# ============================================================
# SAFETY CHECKS
# ============================================================

required = (
    'AUTH = {',
    '"username": _env_user or "admin"',
    'ADMIN_USERNAME',
    'ADMIN_PASSWORD',
    'owner_username = str(',
    '"/api/login"',
    'find_admin_by_username',
    '"role": "owner"',
    '"role": "admin"',
)

for marker in required:
    if marker not in text:
        raise SystemExit(
            f"ERROR: required login marker missing: {marker}"
        )


# ============================================================
# WRITE ONLY MAIN.PY PATCH
# ============================================================

MAIN.write_text(
    text,
    encoding="utf-8",
)

print("=" * 55)
print("POMP NET REAL LOGIN PATCH: OK")
print("OWNER USERNAME: ADMIN_USERNAME")
print("OWNER PASSWORD: ADMIN_PASSWORD")
print("BLANK USERNAME OWNER LOGIN: PRESERVED")
print("AHB SUB-ADMIN LOGIN: PRESERVED")
print("NO DASHBOARD CHANGES")
print("NO SUBSCRIPTION CHANGES")
print("NO VLESS CHANGES")
print("=" * 55)
