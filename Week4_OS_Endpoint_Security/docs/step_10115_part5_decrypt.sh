#!/bin/bash
export PS1="$ "
echo "=== Decrypt clientinfo.enc -> clientinfo.txt (10.1.15 Part 5) ==="
echo "Key from Mary's email (Packet Tracer, verified by user): cisco123"
cd /tmp
set -x
openssl aes-256-cbc -pbkdf2 -a -d -in clientinfo.enc -out clientinfo.txt -pass pass:cisco123
cat clientinfo.txt
set +x
echo
echo "[DONE]"
