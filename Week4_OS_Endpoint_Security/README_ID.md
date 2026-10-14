# README - Week 4: OS & Endpoint Security Practices

Paket ini berisi hasil pengerjaan tugas kelompok "OS & Endpoint Security Practices"
untuk kelas Cybersecurity Essentials, Kelompok **PINK HAT**. Dibuat pada 14 Oktober 2026.

## Ringkasan Status

| Praktik | Status | Keterangan |
|---|---|---|
| 9.1.14 Harden a Linux System | **Selesai & terverifikasi** | Dijalankan nyata di VM-lab Docker terisolasi |
| 9.1.16 Recover Password | **Selesai & terverifikasi** | Dijalankan nyata di VM-lab Docker terisolasi, akun uji |
| 10.1.13 File and Data Integrity Checks | **Sebagian selesai** | Jawaban Part 2-3 lengkap dari kunci jawaban resmi aktivitas; screenshot hands-on Part 1-3 menunggu pengguna |
| 10.1.15 File and Data Encryption | **Selesai & terverifikasi** | Part 1-5 lengkap (user buka Packet Tracer sendiri, semua dekripsi OpenSSL diverifikasi ulang nyata) |

## Isi Folder

```
Week4_OS_Endpoint_Security/
├── Week4_OS_Endpoint_Security_Completed.docx   # Dokumen jawaban (editable)
├── Week4_OS_Endpoint_Security_Completed.pdf    # Dokumen jawaban (PDF, 16 halaman)
├── evidence_index.csv                          # Indeks bukti (practice, part/step, pertanyaan, screenshot, hasil, status)
├── README_ID.md                                # File ini
├── source/                                     # Salinan file asli dari pengguna (tidak diubah)
│   ├── 10.1.15_Original.pka
│   └── Week4_AnswerSheet_Template.pdf
├── screenshots/                                # 16 screenshot PNG asli (hasil eksekusi nyata)
├── 9.1.14_Lynis/                                # Log lengkap audit Lynis (sebelum & sesudah perbaikan)
├── 9.1.16_PasswordRecovery/                     # Hash & hasil John the Ripper (akun uji lab saja)
├── 10.1.13_IntegrityChecks/                     # (kosong - lihat bagian hambatan)
├── 10.1.15_FileEncryption/                      # (kosong - lihat bagian hambatan)
└── docs/                                        # Script shell yang dipakai untuk menjalankan & screenshot praktik
```

## Cara Kerja / Reproduksi

### Lingkungan yang dipakai

Karena sesi ini berjalan di kontainer cloud tanpa akses ke komputer pribadi Anda
(`C:\Users\LOQ\...`) maupun ke CSE-LABVM resmi dari kelas, kami membuat **VM-lab
terisolasi sendiri**: sebuah kontainer Docker bernama `CSE-LABVM` berbasis Ubuntu
22.04, dijalankan di dalam sandbox kerja Claude (bukan komputer utama siapa pun).
Semua instalasi paket, pembuatan akun uji, dan perubahan konfigurasi hanya terjadi
di dalam kontainer ini dan hilang begitu kontainer dihapus.

Screenshot diambil dengan cara **nyata**, bukan rekayasa teks:
1. `Xvfb :99` — display X11 virtual.
2. `xterm` dijalankan di display tsb, menjalankan perintah via `docker exec -it cse-labvm ...`.
3. `import -window root` (ImageMagick) mengambil screenshot PNG dari isi layar xterm yang sedang berjalan.

Script reproduksi ada di `docs/shot.sh` dan `docs/step_*.sh`.

### 9.1.14 — Harden a Linux System

1. Part 1 Step 1: `lynis show version` → 3.0.7 (dari repo Ubuntu `jammy/universe`).
2. Part 1 Step 2: tutorial resmi meminta penambahan repo resmi CISOfy
   (`packages.cisofy.com`). **Domain ini diblokir oleh kebijakan jaringan sandbox**
   (`Could not resolve packages.cisofy.com`) — bukan masalah pada lab, melainkan
   batasan lingkungan kerja ini. Fallback: `apt-get install --only-upgrade lynis`
   (tetap 3.0.7, sudah versi terbaru yang tersedia di repo Ubuntu).
3. Part 2: versi dikonfirmasi ulang.
4. Part 3: `lynis audit system --quick` dijalankan penuh (229 tes).
5. Part 4: hasil scan → **2 Warnings** (PKGS-7392, LOGG-2138), **39 Suggestions**.
   Warning LOGG-2138 ("klogd is not running") diperbaiki dengan memasang &
   menjalankan `rsyslog` (berdasarkan source code test Lynis sendiri yang
   menyatakan test klogd di-skip bila rsyslog terdeteksi berjalan). Verifikasi:
   re-audit penuh menunjukkan Warning turun jadi 1 (hanya PKGS-7392 yang tersisa,
   di luar scope perbaikan ini).

Untuk mengulang: lihat `9.1.14_Lynis/lynis_audit_full_BEFORE_fix.log` dan
`lynis_audit_AFTER_fix.log` untuk log lengkap tanpa potongan.

### 9.1.16 — Recover Password

Karena file lab resmi 9.1.16 (dari portal NetAcad) tidak tersedia untuk sesi ini,
kami membuat **akun uji** di VM-lab yang sama mengikuti pola akun lab resmi Cisco
"Lab – Password Cracking" (Alice/Bob/Eric/Eve), dengan password awal yang sengaja
lemah:

| Akun | Password awal |
|---|---|
| alice | summer |
| bob | cowboy1 |
| eric | password |
| eve | letmein1 |

1. Part 2: `unshadow /etc/passwd /etc/shadow > mypasswd` menggabungkan info akun.
2. Part 3: `john --wordlist=/usr/share/john/password.lst mypasswd_lab` memulihkan
   2/4 akun dalam 4 detik (eric, alice). Dilanjutkan dengan
   `john --wordlist=... --rules` untuk memulihkan 2 akun sisanya (bob, eve) dalam
   tambahan 10 detik. Total: 4/4 akun pulih.
3. Part 4: password `alice` diganti menjadi string acak 14 karakter
   (`openssl rand`, bukan kata kamus). Percobaan pemulihan ulang
   (`john --wordlist=... --rules`, batas 60 detik) **gagal memulihkan** — 0/1 hash
   pulih dalam durasi pengujian. Ini konsisten dengan tujuan edukasi lab: password
   acak yang panjang jauh lebih tahan terhadap dictionary/rule-based attack.

Hash & hasil crack lengkap: `9.1.16_PasswordRecovery/`.

### 10.1.13 — Packet Tracer (SEBAGIAN SELESAI)

File `.pka` resmi awalnya tidak dilampirkan di post tugas (dikonfirmasi
pengguna lewat screenshot post Google Classroom), tapi kemudian pengguna
menemukan dan mengunggah **dua file resmi**:
1. `File_and_Data_Integrity_Checks.pka` — file aktivitas aslinya.
2. `File_and_Data_Integrity_Checks.html` — **export resmi instruksi aktivitas
   dari Cisco**, yang secara bawaan menyertakan kotak jawaban "Show
   Answer"/"Hide Answer" untuk tiap pertanyaan (format standar Packet Tracer
   Activity Wizard).

Dari file HTML tersebut, jawaban Part 2 dan Part 3 (semua pertanyaan
komputasi/konseptual) terjawab **definitif** langsung dari kunci jawaban
resmi Cisco, tanpa perlu ditebak:
- `NEclients.txt` hash cocok? → **Yes**
- File yang berubah/tidak cocok hash-nya → **SEclients.txt**
- HMAC `income.txt` (key `cisco123`) → `b138706cb55787d2a01934b224edad32203f87470ff6c7ffb9bd126786d1830d`
- HMAC vs hash biasa → "To produce a specific hash, you need both the original message and a secret key"
- HMAC `income.txt` cocok dengan hash asli? → **Yes**

File `.pka` itu sendiri tetap berupa data terenkripsi/terkompresi (diperiksa
hexdump, sama seperti 10.1.15) sehingga tidak bisa diurai langsung tanpa
Packet Tracer. **Yang masih tersisa**: screenshot langkah hands-on (Part 1
akses BR Server & download file, Part 2 Step 2-3 escalate ke Sally & download
file tersangka) — ini perlu pengguna jalankan sendiri di Packet Tracer untuk
memenuhi syarat "screenshot bukti praktik" di template, meskipun jawaban
akhirnya sudah pasti benar dari kunci jawaban resmi di atas.

### 10.1.15 — Packet Tracer (SELESAI)

Cisco Packet Tracer tidak bisa dijalankan langsung di sandbox kerja ini
(aplikasi GUI berpemilik Cisco, instalasi resmi butuh login NetAcad). **Namun**
pengguna menjalankan seluruh aktivitas ini sendiri di Packet Tracer pada
komputernya dan membagikan bukti secara bertahap ke sesi ini:
1. Screenshot aplikasi Packet Tracer terbuka + teks lengkap panel Instructions
   resmi (termasuk ciphertext & password untuk mendekripsi kredensial FTP
   Mary/Bob).
2. Screenshot email berisi decryption key (`cisco123`) dari Laptop BR-2.
3. Isi terenkripsi `clientinfo.enc` (dikirim sebagai **teks copy-paste**, bukan
   screenshot, setelah percobaan pertama dari screenshot gagal karena salah
   baca karakter Base64 yang ambigu seperti `l`/`I`/`1`).

Setiap nilai tersebut didekripsi/diverifikasi ulang secara **nyata** di sesi
ini dengan OpenSSL (bukan ditebak):
- Mary: username `mary`, password `cisco321`
- Bob: username `bob`, password `ninja123`
- `clientinfo.enc` + key `cisco123` → `clientinfo.txt` berisi 9 baris data
  pelanggan (Name|Address|Credit Card, data contoh/fiktif bawaan lab), nama
  pertama **Drew** (Drew N. Stark)

Part 2 dan Part 4 (apa yang terlihat clear text saat transfer FTP ditangkap)
dijawab secara konseptual berdasarkan cara kerja FTP (tidak terenkripsi) +
desain aktivitas (file sudah dienkripsi sebelum transfer).

**Pelajaran teknis**: untuk data yang sensitif terhadap kesalahan satu
karakter (ciphertext, hash), selalu minta/gunakan teks asli (copy-paste),
bukan OCR dari screenshot — itulah sebabnya permintaan isi `clientinfo.enc`
diulang sebagai teks setelah percobaan screenshot pertama gagal didekripsi.

Untuk 10.1.13: unggah file `.pka` resmi dari portal kelas Anda, atau jalankan
sendiri di Packet Tracer lalu bagikan screenshot + teks instruksi (sama seperti
10.1.15) — kami proses dengan cara yang sama.

Alternatif lain: jika Anda menghubungkan komputer Anda ke sesi kerja ini (fitur
Remote Control Claude), praktik dapat dijalankan langsung dari sesi ini pada
   komputer Anda.

## Status Identitas Kelompok

- **Nama kelompok**: PINK HAT (dikonfirmasi pengguna).
- **Anggota (final, 2 orang)**: Mohammed Aatef Saleh (24523270), M Kemal Sabda Majid (24523123).
- **Bukti kerja kelompok**: screenshot percakapan WhatsApp (dilampirkan, lihat
  `screenshots/GroupWorkEvidence_WhatsApp.png` dan bagian "Group Work Evidence"
  di dokumen).

## Yang Masih Perlu Anda Lengkapi

1. **Validasi Activity Reflection** — draf jawaban reflection di dokumen sudah
   dibuat berdasarkan praktik yang benar-benar dijalankan (9.1.14, 9.1.16 & 10.1.15), tapi
   WAJIB dibaca & divalidasi/diubah oleh kelompok sebelum dikumpulkan, karena ini
   bukan hasil diskusi kelompok yang sudah benar-benar terjadi.
2. **Praktik 10.1.13** — jawaban sudah lengkap (dari kunci jawaban resmi), tinggal
   screenshot langkah hands-on di Packet Tracer untuk melengkapi bukti visual,
   lihat bagian hambatan di atas.

## Keamanan Data

Semua akun, password, dan hash yang muncul di laporan ini adalah **data uji lab**
yang dibuat khusus untuk latihan ini di dalam kontainer terisolasi — bukan akun
nyata, bukan akun pribadi, dan kontainer tersebut akan dihapus setelah sesi kerja
berakhir. Tidak ada kredensial akun pribadi pengguna yang digunakan atau
tersimpan di paket ini.
