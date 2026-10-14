#!/bin/bash
export PS1="root@CSE-LABVM:~# "
unshadow /etc/passwd /etc/shadow > /root/mypasswd
grep -E '^alice:' /root/mypasswd > /root/mypasswd_alice_strong
rm -f /root/.john/john.pot
echo "Attempt to recover alice's NEW strong password (60 second budget):"
set -x
timeout 60 john --wordlist=/usr/share/john/password.lst --rules /root/mypasswd_alice_strong
john --show /root/mypasswd_alice_strong
set +x
echo
echo "[DONE - see result above]"
