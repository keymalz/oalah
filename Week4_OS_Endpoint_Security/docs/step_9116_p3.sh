#!/bin/bash
export PS1="root@CSE-LABVM:~# "
set -x
john --wordlist=/usr/share/john/password.lst /root/mypasswd_lab
set +x
echo
echo "--- john --show ---"
set -x
john --show /root/mypasswd_lab
set +x
echo
echo "[DONE]"
