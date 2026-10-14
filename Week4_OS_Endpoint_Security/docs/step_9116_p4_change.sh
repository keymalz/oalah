#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo "Change alice's password to a strong, random (non-dictionary) password:"
set -x
usermod -p $(openssl passwd -6 -salt alicestrong 'XsR1Jjw!Ksa45L#9') alice
set +x
echo "New password set (recorded only in this lab package, not a real account)."
echo
echo "[DONE]"
