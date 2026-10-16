#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo "Lab test accounts (created for this practice only, isolated container):"
grep -E '^(alice|bob|eric|eve):' /etc/passwd
echo
set -x
unshadow /etc/passwd /etc/shadow > /root/mypasswd
set +x
echo
echo "--- /root/mypasswd (lab accounts only) ---"
grep -E '^(alice|bob|eric|eve):' /root/mypasswd
echo
echo "[DONE]"
