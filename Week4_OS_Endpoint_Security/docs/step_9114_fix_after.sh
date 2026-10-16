#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo "AFTER FIX: confirm log daemon is running, then re-run Lynis to re-check LOGG-2138"
set -x
ps aux | grep -Ei "rsyslog" | grep -v grep
lynis audit system --quick --tests LOGG-2138 2>&1 | grep -A4 -i "running log daemon"
set +x
echo
echo "[DONE]"
