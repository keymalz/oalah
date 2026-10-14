#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo "BEFORE FIX: checking for any running log daemon"
set -x
ps aux | grep -Ei "klogd|syslog|rsyslog|journald" | grep -v grep
lynis show details LOGG-2138
set +x
echo
echo "[DONE]"
