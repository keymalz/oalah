#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo "AFTER FIX: rsyslogd running as a process + re-run Lynis LOGG-2138 check"
set -x
ps aux | grep rsyslogd | grep -v grep
lynis audit system --quick --tests LOGG-2138 2>&1 | tail -20
set +x
echo
echo "[DONE]"
