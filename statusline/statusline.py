#!/usr/bin/env python3
"""The Catalyst status line for Claude Code — what your Wingman is doing behind the prompt.

Claude Code runs this on every activity tick (and once a second when idle) with a
JSON object on stdin that carries the ``session_id``. There is no running process:
the plugin's hooks write one small JSON record per session under
``~/.catalyst-claude/statusline/state/`` (``hooks/statusline_capture.py``) and this
script prints one line from it — a pure function of (state, now), so the shimmer
and the pane rotation are choreographed by the clock, not by memory.

    ⚡ catalyst ⠹ reaching Devin's Wingman          ← a tool call in flight
    ⚡ catalyst · 4 recovered · 2 Wingmen · 1 expertise learned · 3 memories recorded
    ⚡ catalyst · from Devin's Wingman 2m ago       ← panes rotate every 4 s
    ⚡ catalyst · learned expertise 5m ago

If another status line was configured before Catalyst installed itself (the
``chain.json`` written by ``hooks/statusline_install.py``), its output is appended
after a divider, so nothing the user had goes away. Fails silent, always.
"""
from __future__ import annotations

import hashlib
import json
import os
import select
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
ROOT = os.path.join(HOME, ".catalyst-claude", "statusline")
STATE_DIR = os.path.join(ROOT, "state")
CHAIN_FILE = os.path.join(ROOT, "chain.json")
SCHEMA = 1

INFLIGHT_TTL_S = 120        # a PreToolUse with no PostToolUse (denied / crashed) stops spinning here
PANE_TICKS = 4              # seconds a pane stays before the next
EMPHASIS_TICKS = 2          # seconds each tally part stays bold
CREST_STRIDE = 3            # letters the shimmer crest jumps per tick (coprime with len("catalyst"))
SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

# The site's violet (#6C4CF1, --primary) lifted to a mid tint so it clears both
# dark and light terminals; the crest of the shimmer runs to near-white.
BASE = "\x1b[38;2;140;116;245m"
MID = "\x1b[38;2;201;191;251m"
HI = "\x1b[38;2;241;238;254m"
WHITE = "\x1b[97m"
GRAY = "\x1b[38;5;245m"
BOLD = "\x1b[1m"
RESET = "\x1b[0m"


def _read_stdin(timeout_s: float = 0.5) -> tuple[dict, bytes]:
    """Claude Code writes the JSON and closes the pipe; never block longer than the tick."""
    if sys.stdin.isatty():
        return {}, b""
    chunks: list[bytes] = []
    deadline = time.monotonic() + timeout_s
    fd = sys.stdin.buffer
    while True:
        left = deadline - time.monotonic()
        if left <= 0:
            break
        r, _, _ = select.select([fd], [], [], left)
        if not r:
            break
        b = os.read(fd.fileno(), 65536)
        if not b:
            break
        chunks.append(b)
    raw = b"".join(chunks)
    try:
        return json.loads(raw.decode("utf-8") or "{}"), raw
    except Exception:
        return {}, raw


def state_path(session_id: str) -> str:
    return os.path.join(STATE_DIR, hashlib.sha256(session_id.strip().encode()).hexdigest() + ".json")


def read_state(session_id: str) -> dict | None:
    try:
        with open(state_path(session_id), encoding="utf-8") as f:
            st = json.load(f)
        return st if st.get("version") == SCHEMA else None
    except Exception:
        return None


def age(ms: float, now_ms: float) -> str:
    s = max(1, int((now_ms - ms) / 1000))
    if s < 60:
        return f"{s}s"
    m = s // 60
    return f"{m}m" if m < 60 else f"{m // 60}h"


def shimmer(word: str, tick: int) -> str:
    crest = (tick * CREST_STRIDE) % len(word)
    out = []
    for i, ch in enumerate(word):
        d = abs(i - crest)
        out.append((HI if d == 0 else MID if d <= 2 else BASE) + ch)
    return "".join(out) + RESET


def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def render(st: dict | None, now_ms: float) -> str:
    if not st:
        return ""
    tick = int(now_ms // 1000)
    brand = f"{BASE}{BOLD}⚡{RESET} {BOLD}{shimmer('catalyst', tick)}{RESET}"

    inflight = st.get("inflight") or None
    if inflight and 0 <= now_ms - float(inflight.get("at", 0)) < INFLIGHT_TTL_S * 1000:
        spin = SPINNER[(tick * 3) % len(SPINNER)]
        return f"{brand} {BASE}{spin}{RESET} {WHITE}{inflight.get('label', 'working')}{RESET}"

    parts: list[str] = []
    if st.get("recovered", 0) > 0:
        parts.append(f"{st['recovered']} recovered")
    wingmen = st.get("wingmen") or {}
    if wingmen:
        parts.append(plural(len(wingmen), "Wingman", "Wingmen"))
    if st.get("expertise", 0) > 0:
        parts.append(f"{st['expertise']} expertise learned")
    if st.get("memories", 0) > 0:
        parts.append(plural(st["memories"], "memory recorded", "memories recorded"))

    if not parts:
        return f"{brand} {WHITE}· ready{RESET}"

    # Rotate real content: the tally, then live relative ages that tick upward.
    panes: list[str | None] = [None]
    last_from = st.get("last_from") or {}
    if last_from.get("at"):
        panes.append(f"{last_from.get('label', 'from a colleague')} {age(last_from['at'], now_ms)} ago")
    last_learn = st.get("last_learn") or {}
    if last_learn.get("at"):
        panes.append(f"{last_learn.get('label', 'learned')} {age(last_learn['at'], now_ms)} ago")
    pane = panes[(tick // PANE_TICKS) % len(panes)]
    if pane:
        return f"{brand} {WHITE}·{RESET} {WHITE}{pane}{RESET}"

    emph = (tick // EMPHASIS_TICKS) % len(parts)
    styled = [f"{WHITE}{BOLD}{p}{RESET}" if i == emph else f"{GRAY}{p}{RESET}" for i, p in enumerate(parts)]
    return f"{brand} {WHITE}·{RESET} " + f"{GRAY} · {RESET}".join(styled)


def chained(raw_stdin: bytes) -> str:
    """The status line that was there before Catalyst — still rendered, after ours."""
    try:
        with open(CHAIN_FILE, encoding="utf-8") as f:
            cmd = (json.load(f).get("command") or "").strip()
        if not cmd or "catalyst-claude" in cmd:
            return ""
        out = subprocess.run(cmd, shell=True, input=raw_stdin, capture_output=True, timeout=0.8)
        return out.stdout.decode("utf-8", "replace").splitlines()[0].strip() if out.stdout else ""
    except Exception:
        return ""


def main() -> None:
    try:
        payload, raw = _read_stdin()
        sid = payload.get("session_id") if isinstance(payload, dict) else None
        ours = render(read_state(sid), time.time() * 1000) if isinstance(sid, str) and sid.strip() else ""
        other = chained(raw)
        line = ours if not other else (f"{ours} {GRAY}│{RESET} {other}" if ours else other)
        if line:
            sys.stdout.write(line)
            sys.stdout.flush()
    except Exception:
        pass    # a status line must never disturb Claude Code


if __name__ == "__main__":
    main()
