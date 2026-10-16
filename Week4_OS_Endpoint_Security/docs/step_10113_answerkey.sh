#!/bin/bash
export PS1="$ "
echo "Sumber: File_and_Data_Integrity_Checks.html (export resmi aktivitas Packet Tracer"
echo "        dari Cisco, berisi kotak 'Show Answer' bawaan)"
echo
cd /home/user/oalah/Week4_OS_Endpoint_Security/10.1.13_IntegrityChecks
sed -n '/Are the two hash values/,/Which file has been tampered/p' official_instructions_and_answers.txt | head -8
echo "..."
sed -n '/What is the computed HMAC/,/Show All Answers/p' official_instructions_and_answers.txt
