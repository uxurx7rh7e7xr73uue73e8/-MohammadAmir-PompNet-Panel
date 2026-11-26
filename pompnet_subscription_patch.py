#!/usr/bin/env python3
"""Surgical subscription-output fix for the pinned panel core.

Only removes the invalid synthetic 0.0.0.0 VLESS entry from /sub/{uuid}
and uses the request's actual public host in the subscription profile title.
All user records, inbounds, protocol generators and panel routes stay intact.
"""
from pathlib import Path
import re
import sys

target = Path("/app/main.py")
if not target.is_file():
    raise SystemExit("Subscription patch: /app/main.py not found")

source = target.read_text(encoding="utf-8")
updated = source

# The core already owns /sub/{uuid}; keep that route and its real config
# generation. Remove only the extra, unusable 0.0.0.0 VLESS line.
pattern = re.compile(
    r'^\s*stats_line = generate_vless_link\(uuid, "0\.0\.0\.0".*\)\n'
    r'^\s*lines = \[stats_line\]$',
    re.MULTILINE,
)
updated, removed = pattern.subn("    lines = []", updated, count=1)

old_title = 'profile_title = f"0.0.0.0 | {stats_remark}"'
new_title = 'profile_title = f"{host} | {stats_remark}"'

if removed == 1:
    if updated.count(old_title) != 1:
        raise SystemExit("Subscription patch: expected profile title not found exactly once")
    updated = updated.replace(old_title, new_title, 1)
elif removed == 0:
    # Safe idempotence: accept only the exact already-patched state.
    if (
        'profile_title = f"{host} | {stats_remark}"' not in updated
        or 'lines = []' not in updated
    ):
        raise SystemExit("Subscription patch: source did not match expected core; refusing to modify it")
else:
    raise SystemExit("Subscription patch: unexpected duplicate subscription block")

if updated != source:
    target.write_text(updated, encoding="utf-8")
    print("Subscription patch applied: /sub/{uuid} now emits only real host-based user configs.")
else:
    print("Subscription patch already applied; no changes needed.")
