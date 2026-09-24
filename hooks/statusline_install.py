#!/usr/bin/env python3
"""SessionStart hook: wire the Catalyst status line into Claude Code.

- ``~/.catalyst-claude/statusline-current`` → this plugin version's
  ``statusline/statusline.py`` (a symlink re-pointed every session, so the
  setting survives plugin updates without copying code).
- ``~/.claude/settings.json`` ``statusLine`` → that symlink, once. A status line
  that was already there (another plugin's, the user's own) is kept: its command
  is recorded in ``chain.json`` and the Catalyst renderer prints it after ours,
  so nothing the user had disappears. A user who later removes the entry is not
  fought — the ``installed`` sentinel means "install once".
- The session's state record is created, so the line reads "ready" before the
  first tool call; records older than 7 days are pruned.

Prints nothing (a SessionStart hook's stdout would land in the model's context).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

HOME = os.path.expanduser("~")
CAT_DIR = os.path.join(HOME, ".catalyst-claude")
ROOT = os.path.join(CAT_DIR, "statusline")
STATE_DIR = os.path.join(ROOT, "state")
LINK = os.path.join(CAT_DIR, "statusline-current")
CHAIN_FILE = os.path.join(ROOT, "chain.json")
INSTALLED = os.path.join(ROOT, "installed")
SETTINGS = os.path.join(HOME, ".claude", "settings.json")
ENTRY = {"type": "command", "command": "python3 ~/.catalyst-claude/statusline-current", "refreshInterval": 1}
SCHEMA = 1


def renderer_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "statusline", "statusline.py"))


def refresh_link() -> str:
    """Point the stable symlink at this plugin version's renderer and return the
    command the setting should run. Where a symlink cannot be made (some Windows
    setups), fall back to the renderer's absolute path — re-pointed every session
    start, so a plugin update still lands."""
    target = renderer_path()
    os.makedirs(CAT_DIR, exist_ok=True)
    try:
        if not (os.path.islink(LINK) and os.readlink(LINK) == target):
            if os.path.lexists(LINK):
                os.unlink(LINK)
            os.symlink(target, LINK)
        if os.path.islink(LINK):
            return ENTRY["command"]
    except Exception:
        pass
    return f'python3 "{target}"'


def install_setting(command: str) -> str:
    """Write the statusLine entry once. Returns what happened: 'installed' (first
    time — the user should hear about it), 'updated' (ours, but the command moved —
    the no-symlink fallback after a plugin update), 'present' or 'kept' (installed
    before and removed by the user — never fought)."""
    try:
        settings = {}
        if os.path.exists(SETTINGS):
            with open(SETTINGS, encoding="utf-8") as f:
                settings = json.load(f)
        current = settings.get("statusLine")
        cur_cmd = str(current.get("command", "")) if isinstance(current, dict) else ""
        ours = "catalyst-claude" in cur_cmd or "statusline.py" in cur_cmd and "catalyst" in cur_cmd
        if ours and cur_cmd == command:
            return "present"
        if not ours and os.path.exists(INSTALLED):
            return "kept"                           # installed once before; the user removed it — respect that
        if not ours and cur_cmd.strip():
            os.makedirs(ROOT, exist_ok=True)
            with open(CHAIN_FILE, "w", encoding="utf-8") as f:
                json.dump({"command": cur_cmd, "recorded_at": int(time.time())}, f)
        settings["statusLine"] = dict(ENTRY, command=command)
        tmp = SETTINGS + ".catalyst-tmp"
        os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
            f.write("\n")
        os.replace(tmp, SETTINGS)
        os.makedirs(ROOT, exist_ok=True)
        with open(INSTALLED, "w") as f:
            f.write(time.strftime("%Y-%m-%dT%H:%M:%S"))
        return "updated" if ours else "installed"
    except Exception:
        return "error"


def touch_state(session_id: str) -> None:
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        p = os.path.join(STATE_DIR, hashlib.sha256(session_id.encode()).hexdigest() + ".json")
        if not os.path.exists(p):
            now = int(time.time() * 1000)
            st = {"version": SCHEMA, "session_id_sha": hashlib.sha256(session_id.encode()).hexdigest()[:12],
                  "startedAt": now, "updatedAt": now, "user": "", "recovered": 0, "expertise": 0, "memories": 0,
                  "inreach": 0, "wingmen": {}, "owners": {}, "inflight": None, "last_from": None, "last_learn": None}
            with open(p + ".tmp", "w", encoding="utf-8") as f:
                json.dump(st, f)
            os.replace(p + ".tmp", p)
        cutoff = time.time() - 7 * 86400
        for name in os.listdir(STATE_DIR):
            fp = os.path.join(STATE_DIR, name)
            try:
                if os.path.getmtime(fp) < cutoff:
                    os.remove(fp)
            except Exception:
                pass
    except Exception:
        pass


def main() -> int:
    try:
        raw = sys.stdin.read()
        ev = json.loads(raw) if raw.strip() else {}
    except Exception:
        ev = {}
    outcome = install_setting(refresh_link())
    sid = str(ev.get("session_id") or "").strip()
    if sid:
        touch_state(sid)
    # Claude Code re-runs a changed statusLine command right away (docs: "A change to
    # the command itself skips the debounce"), so the line usually appears at once;
    # say so once, to the person (systemMessage is shown to the user and adds nothing
    # to the model's context). json.dumps keeps this stdout ASCII whatever the locale.
    if outcome == "installed":
        sys.stdout.write(json.dumps({"systemMessage": "⚡ Catalyst status line installed — look at the bottom of Claude Code (if it is not there yet, it will be on your next session)."}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
