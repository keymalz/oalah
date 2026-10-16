#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo '+ grep -c "^suggestion\[\]=" /var/log/lynis-report.dat'
grep -c '^suggestion\[\]=' /var/log/lynis-report.dat
echo '+ grep -c "^warning\[\]=" /var/log/lynis-report.dat'
grep -c '^warning\[\]=' /var/log/lynis-report.dat
echo
echo "[DONE]"
