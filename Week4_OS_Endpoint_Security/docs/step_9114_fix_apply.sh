#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo "SOLUTION: install + start rsyslog (provides syslog + kernel log daemon)"
set -x
apt-get install -y -qq rsyslog
service rsyslog start
sleep 1
service rsyslog status
set +x
echo
echo "[DONE]"
