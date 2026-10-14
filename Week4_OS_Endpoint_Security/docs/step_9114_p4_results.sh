#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo '+ sed -n "544,558p" /root/lynis_audit_full.log   # Warnings section'
sed -n '544,558p' /root/lynis_audit_full.log
echo
echo "[DONE]"
