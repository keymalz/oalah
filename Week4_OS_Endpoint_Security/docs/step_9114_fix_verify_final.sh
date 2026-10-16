#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo '+ sed -n "550,558p" /root/lynis_audit_recheck.log   # full re-audit after fix'
sed -n '550,558p' /root/lynis_audit_recheck.log
echo
echo "[DONE]"
