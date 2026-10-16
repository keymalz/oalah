#!/bin/bash
export PS1="root@CSE-LABVM:~# "
set -x
lynis audit system --quick 2>&1 | tee /root/lynis_audit_full.log
set +x
echo
echo "[AUDIT COMPLETE - full log saved to /root/lynis_audit_full.log]"
