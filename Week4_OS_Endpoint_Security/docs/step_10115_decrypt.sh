#!/bin/bash
export PS1="$ "
echo "=== Decrypt Mary's FTP account info (10.1.15 Part 1) ==="
echo "Ciphertext from maryftplogin.txt, password from activity: maryftp123"
set -x
echo 'U2FsdGVkX1+sKwL7uceALGKqAQ78WWown3ok73zicO8GLYu2SpMvLEwCB7HsyRC3MeimUjiXRCLwOSSahAraUrnEtkClGK4tytP9hludc6k=' | openssl aes-256-cbc -pbkdf2 -a -d -pass pass:maryftp123
set +x
echo
echo "=== Decrypt Bob's FTP account info (10.1.15 Part 3) ==="
echo "Ciphertext from bobftplogin.txt, password from activity: bobftp123"
set -x
echo 'U2FsdGVkX1/+3jGTemCqs3e4dK8+b0xfXJiq4eoU0lQgRV9aZQPqJCBsYJWc9lDQwiB2svhiWSUVhCRS5qBrjgmDZF3q/dXqaCrZRR5prjE=' | openssl aes-256-cbc -pbkdf2 -a -d -pass pass:bobftp123
set +x
echo
echo "[DONE]"
