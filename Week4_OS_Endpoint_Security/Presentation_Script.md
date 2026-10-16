# Presentation Script — Week 4: OS & Endpoint Security Practices
**Group: PINK HAT**
**Members: Mohammed Aatef Saleh (24523270), M Kemal Sabda Majid (24523123)**

---

## Opening

Good morning/afternoon everyone. Our group name is **PINK HAT**. Today we will present our work for the "OS and Endpoint Security Practices" assignment from the Cybersecurity Essentials class.

We completed four practices:
1. 9.1.14 — Harden a Linux System
2. 9.1.16 — Recover Password
3. 10.1.13 — File and Data Integrity Checks
4. 10.1.15 — File and Data Encryption

For each practice, we will explain **what we did** and **what result we got**.

---

## Section 1: 9.1.14 — Harden a Linux System

**What we did:**
We used a tool called Lynis to check the security of a Linux system. First, we checked which version of Lynis was already installed. Then we tried to update it to the newest version. After that, we ran a full security audit using the command `lynis audit system`. This audit checks the whole system — more than 200 different security tests.

**What result we got:**
The audit ran 229 tests in total. It found **2 Warnings** and **39 Suggestions**. A warning means something needs attention. A suggestion is a smaller improvement.

We picked one warning to fix: the system had no log daemon running, which means important log messages could be lost. We installed and started a service called `rsyslog` to fix this. After fixing it, we ran the audit again to check. The result: the warning count dropped from 2 down to 1. This proves our fix really worked.

---

## Section 2: 9.1.16 — Recover Password

**What we did:**
This practice is about password cracking — testing how strong or weak passwords are. We created four test accounts with different passwords. Then we combined the username and password-hash information into one file. After that, we used a tool called **John the Ripper** to try to crack the passwords.

**What result we got:**
In the first attempt, using a simple dictionary list, we recovered **2 out of 4 passwords** in just 4 seconds. These were weak passwords like "password" and "summer". The other 2 passwords were a bit stronger — they had numbers added — so we used a smarter attack mode with extra rules. This time, we recovered the last 2 passwords in 10 more seconds. In total, **4 out of 4 passwords were cracked**.

Then we changed one password to a much stronger one — a random 14-character password. We tried to crack it again using the same method, but this time, within 60 seconds, we **could not crack it**. This shows that strong, random passwords are much harder to break than simple dictionary passwords.

---

## Section 3: 10.1.13 — File and Data Integrity Checks

**What we did:**
This practice uses a simulated company network in Cisco Packet Tracer. The story: a file server got attacked and some client files may have been changed without permission. Our job was to find out which file was changed. We connected to the server, downloaded 6 client files, and copied the original hash values (like a digital fingerprint) that were recorded before the attack. Then we calculated the hash of each downloaded file and compared it to the original hash.

**What result we got:**
We found that **one file, called SEclients.txt, had a different hash value** than the original. This means that file was changed — it was tampered with. The other 5 files matched perfectly, so they were safe.

After finding this, we reported the problem by sending an email to our supervisor, Sally. Then we downloaded the suspicious file to Sally's computer so she could investigate it further.

We also used a stronger method called **HMAC**, which is like a hash but combined with a secret key. We calculated the HMAC for an important file called income.txt and confirmed it matched the original value — meaning that file was safe. We learned that HMAC is more secure than a normal hash, because to create a correct HMAC, you need both the file content **and** a secret key. A normal hash check only proves the file didn't change — HMAC also proves it came from someone who has the secret key.

---

## Section 4: 10.1.15 — File and Data Encryption

**What we did:**
This practice shows how encryption protects data during file transfer. In the story, two employees — Mary and Bob — need to send a confidential file (customer data) using FTP. Their FTP login details were saved in encrypted text files. We had to decrypt their usernames and passwords using OpenSSL, a well-known encryption tool. Then we simulated the file transfer: Mary uploaded the encrypted file to the server, and Bob downloaded it from another location.

**What result we got:**
We successfully decrypted both accounts:
- Mary's FTP account: username "mary", password "cisco321"
- Bob's FTP account: username "bob", password "ninja123"

We learned something important here: FTP itself is **not secure** — if someone captures the network traffic, they can see the login username and password in plain text. **But** because the actual file content was already encrypted before it was sent, the file's content stays protected even if the transfer is captured. This shows why encrypting data **before** sending it is so important.

Finally, we got a decryption key from an email message inside the simulation, and used it to decrypt the confidential file. Inside, we found a customer list, and the first name listed was **"Drew"** (Drew N. Stark).

---

## Closing

To summarize: we completed all four practices successfully.
- In **9.1.14**, we hardened a Linux system and reduced security warnings from 2 to 1.
- In **9.1.16**, we proved that weak passwords can be cracked in seconds, while strong passwords resist cracking.
- In **10.1.13**, we found and reported a tampered file using hashing and HMAC.
- In **10.1.15**, we decrypted hidden credentials and confidential files, and learned why encryption matters even when the transfer method itself is not secure.

Thank you for listening. We are ready for any questions.

**— End of Script —**
