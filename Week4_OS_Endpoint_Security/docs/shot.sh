#!/bin/bash
# Reusable helper: copy a script into CSE-LABVM docker container, run it in a
# real xterm on a virtual display, wait, and take a genuine screenshot.
# Usage: shot.sh <output.png> <wait_seconds> <local_script_path>
set -e
OUT="$1"
WAIT="$2"
SCRIPT="$3"
export DISPLAY=:99

pkill -f "cse-labvm-shot" 2>/dev/null || true
sleep 0.5

docker cp "$SCRIPT" cse-labvm:/root/_step.sh >/dev/null

xterm -hold -geometry 158x48+0+0 -fa Monospace -fs 13 -bg black -fg "#00FF00" \
  -T "cse-labvm-shot" -e docker exec -it cse-labvm bash /root/_step.sh \
  > /tmp/xterm_last.log 2>&1 &
XPID=$!

sleep "$WAIT"
import -display :99 -window root "$OUT"
echo "Saved: $OUT"

sleep 1
kill $XPID 2>/dev/null || true
pkill -f "cse-labvm-shot" 2>/dev/null || true
