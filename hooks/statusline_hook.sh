#!/bin/sh
# Launcher for the status line hooks — `sh statusline_hook.sh install|capture`.
#
# No single runtime is on every Claude Code machine: a Mac set up with the native
# installer has python3 (Command Line Tools) but often no node; a Windows machine
# usually has node but python3 is not a command there. Claude Code runs hook
# commands through a POSIX shell (Git Bash on Windows), so this picks whichever
# runtime exists, node first, and hands the hook's stdin straight through. Neither
# runtime → exit 0 quietly: a status line that cannot run must never become an
# error printed on every tool call. The same choice decides which renderer the
# settings entry runs (each install hook writes a command for its own runtime).
here=${0%/*}                      # the script's own dir — parameter expansion, no external command (PATH may be bare)
case "$here" in "$0") here=. ;; esac
what=$1
case "$what" in install|capture) ;; *) exit 0 ;; esac
if command -v node >/dev/null 2>&1; then
  exec node "$here/statusline_$what.js"
elif command -v python3 >/dev/null 2>&1; then
  exec python3 "$here/statusline_$what.py"
fi
exit 0
