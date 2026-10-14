#!/bin/bash
export PS1="root@CSE-LABVM:~# "
set -x
lynis show version
dpkg -l lynis | tail -2
set +x
echo
echo "[DONE]"
