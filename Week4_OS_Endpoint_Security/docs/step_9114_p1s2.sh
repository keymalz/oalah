#!/bin/bash
export PS1="root@CSE-LABVM:~# "
echo "[1] Tutorial step: add official CISOfy repo for latest Lynis"
echo "deb https://packages.cisofy.com/community/lynis/deb/ stable main"
echo
echo "[2] apt-get update output (CISOfy lines only):"
apt-get update 2>&1 | grep -i -A2 cisofy
echo
echo "[3] Environment network policy blocks packages.cisofy.com (non-whitelisted host)."
echo "    Fallback used: apt-get install --only-upgrade lynis via Ubuntu universe repo."
set -x
apt-get install -y --only-upgrade lynis
set +x
lynis show version
echo
echo "[DONE]"
