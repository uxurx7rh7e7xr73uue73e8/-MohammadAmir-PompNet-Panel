import hashlib
import json
import logging
import os
import subprocess
import threading
from pathlib import Path
from typing import Iterable

logger = logging.getLogger("pompnet-xray")

XRAY_BIN = os.getenv(
    "XRAY_BIN",
    "/usr/local/bin/xray",
)

DATA_DIR = Path(
    os.getenv(
        "RAILWAY_VOLUME_MOUNT_PATH",
        os.getenv(
            "DATA_DIR",
            "/app/data",
        ),
    )
)

XRAY_CONFIG = DATA_DIR / "pompnet-xray.json"

XRAY_HOST = "127.0.0.1"
XRAY_PORT = 10000

_process = None
_lock = threading.RLock()

_last_hash = ""


def _uuid(value):
    value = str(value or "").strip()

    parts = value.split("-")

    if len(parts) != 5:
        return None

    if [
        8,
        4,
        4,
        4,
        12,
    ] != [
        len(x)
        for x in parts
    ]:
        return None

    try:
        int(value.replace("-", ""), 16)
    except ValueError:
        return None

    return value.lower()


def extract_uuids(links) -> list[str]:
    if not isinstance(links, dict):
        return []

    result = []

    for uid, link in links.items():

        if not isinstance(link, dict):
            continue

        if link.get("active", True) is False:
            continue

        clean = _uuid(uid)

        if clean and clean not in result:
            result.append(clean)

    return result


def build_config(links) -> dict:
    uuids = extract_uuids(links)

    clients = [
        {
            "id": uid,
            "email": f"pompnet-{index}",
            "level": 0,
        }
        for index, uid in enumerate(
            uuids,
            start=1,
        )
    ]

    return {
        "log": {
            "loglevel": "warning",
        },

        "inbounds": [
            {
                "tag": "pompnet-vless",
                "listen": XRAY_HOST,
                "port": XRAY_PORT,
                "protocol": "vless",

                "settings": {
                    "clients": clients,
                    "decryption": "none",
                },

                "streamSettings": {
                    "network": "tcp",
                },

                "sniffing": {
                    "enabled": True,
                    "destOverride": [
                        "http",
                        "tls",
                    ],
                },
            }
        ],

        "outbounds": [
            {
                "tag": "direct",
                "protocol": "freedom",
            },

            {
                "tag": "block",
                "protocol": "blackhole",
            },
        ],

        "routing": {
            "domainStrategy": "AsIs",
            "rules": [],
        },
    }


def _config_hash(config: dict) -> str:
    raw = json.dumps(
        config,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()

    return hashlib.sha256(raw).hexdigest()


def write_config(links) -> bool:
    global _last_hash

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    config = build_config(
        links
    )

    current_hash = _config_hash(
        config
    )

    if (
        XRAY_CONFIG.exists()
        and current_hash == _last_hash
    ):
        return False

    temporary = XRAY_CONFIG.with_suffix(
        ".tmp"
    )

    temporary.write_text(
        json.dumps(
            config,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary.replace(
        XRAY_CONFIG
    )

    _last_hash = current_hash

    return True


def validate_config() -> bool:
    if not Path(
        XRAY_BIN
    ).exists():
        logger.error(
            "Xray binary not found: %s",
            XRAY_BIN,
        )
        return False

    if not XRAY_CONFIG.exists():
        logger.error(
            "Xray config not found: %s",
            XRAY_CONFIG,
        )
        return False

    try:
        result = subprocess.run(
            [
                XRAY_BIN,
                "run",
                "-test",
                "-config",
                str(XRAY_CONFIG),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
        )

        if result.returncode != 0:
            logger.error(
                "Xray config test failed: %s",
                result.stderr[-4000:],
            )
            return False

        return True

    except Exception:
        logger.exception(
            "Xray config validation failed"
        )
        return False


def stop_xray():
    global _process

    with _lock:

        if _process is None:
            return

        try:

            if _process.poll() is None:
                _process.terminate()

                try:
                    _process.wait(
                        timeout=10
                    )
                except subprocess.TimeoutExpired:
                    _process.kill()
                    _process.wait(
                        timeout=5
                    )

        except Exception:
            logger.exception(
                "Could not stop Xray"
            )

        finally:
            _process = None


def start_xray() -> bool:
    global _process

    with _lock:

        if (
            _process is not None
            and _process.poll() is None
        ):
            return True

        if not validate_config():
            return False

        try:

            _process = subprocess.Popen(
                [
                    XRAY_BIN,
                    "run",
                    "-config",
                    str(XRAY_CONFIG),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

        except Exception:
            logger.exception(
                "Could not start Xray"
            )
            _process = None
            return False

        return True


def ensure_xray(links) -> bool:
    with _lock:

        changed = write_config(
            links
        )

        if changed:

            stop_xray()

        if (
            _process is None
            or _process.poll() is not None
        ):
            return start_xray()

        return True


def restart_xray(links) -> bool:
    with _lock:

        write_config(
            links
        )

        stop_xray()

        return start_xray()


def xray_running() -> bool:
    with _lock:

        return bool(
            _process is not None
            and _process.poll() is None
        )


def get_xray_status() -> dict:
    return {
        "available": Path(
            XRAY_BIN
        ).exists(),

        "running":
            xray_running(),

        "config":
            str(XRAY_CONFIG),

        "port":
            XRAY_PORT,
    }
