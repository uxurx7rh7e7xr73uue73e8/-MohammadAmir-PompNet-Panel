"""
POMP NET Xray Manager Compatibility Layer.

The real implementation lives in pompnet_xray.py.
This file is kept so existing imports never break.
"""

from pompnet_xray import (
    build_config,
    ensure_xray,
    extract_uuids,
    get_xray_status,
    restart_xray,
    start_xray,
    stop_xray,
    validate_config,
    write_config,
    xray_running,
)

__all__ = [
    "build_config",
    "ensure_xray",
    "extract_uuids",
    "get_xray_status",
    "restart_xray",
    "start_xray",
    "stop_xray",
    "validate_config",
    "write_config",
    "xray_running",
]
