#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo "Remaining 2 accounts (bob, eve) resisted plain wordlist - retry with mangling rules:"
set -x
john --wordlist=/usr/share/john/password.lst --rules /root/mypasswd_lab
john --show /root/mypasswd_lab
set +x
echo
echo "[DONE]"
