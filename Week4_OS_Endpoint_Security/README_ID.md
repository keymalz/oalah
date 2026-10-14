# README - Week 4: OS & Endpoint Security Practices

Paket ini berisi hasil pengerjaan tugas kelompok "OS & Endpoint Security Practices"
untuk kelas Cybersecurity Essentials, Kelompok **PINK HAT**. Dibuat pada 14 Oktober 2026.

## Ringkasan Status

| Praktik | Status | Keterangan |
|---|---|---|
| 9.1.14 Harden a Linux System | **Selesai & terverifikasi** | Dijalankan nyata di VM-lab Docker terisolasi |
| 9.1.16 Recover Password | **Selesai & terverifikasi** | Dijalankan nyata di VM-lab Docker terisolasi, akun uji |
| 10.1.13 File and Data Integrity Checks | **Terhambat** | File .pka asli tidak tersedia |
| 10.1.15 File and Data Encryption | **Terhambat** | File .pka ada, Packet Tracer tidak dapat dijalankan |

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

### 10.1.13 dan 10.1.15 — Packet Tracer (TERHAMBAT)

**10.1.13**: file `.pka` resmi tidak dilampirkan pengguna dan tidak dapat
ditemukan dari sumber yang sah dan dapat diakses sesi ini (portal kelas/NetAcad
tidak terhubung ke sesi ini). Sesuai instruksi, kami **tidak membuat topologi
tiruan** sebagai pengganti.

**10.1.15**: file `.pka` **ada** (dilampirkan pengguna, disalin ke `source/`),
namun **Cisco Packet Tracer tidak dapat dijalankan** di lingkungan kerja ini:
- Tidak tersedia di repository paket Linux mana pun (dicek via `apt-cache search`).
- Pengunduhan resmi memerlukan login akun Cisco NetAcad (kredensial tidak diminta
  melalui chat, sesuai instruksi Anda).
- Merupakan aplikasi desktop GUI berat yang memerlukan interaksi klik manual pada
  banyak "PC simulasi" dan Simulation Mode — tidak dapat diotomasi secara andal
  tanpa tool kendali GUI yang terhubung ke aplikasi tersebut.

**Yang Anda perlu lakukan** untuk menyelesaikan kedua praktik ini:
1. Untuk 10.1.13: unggah file `.pka` resmi dari portal kelas Anda.
2. Untuk 10.1.15: jalankan file `source/10.1.15_Original.pka` ini sendiri di
   Cisco Packet Tracer pada komputer Anda yang sudah memilikinya terpasang
   (sesuai jejak file di `C:\Users\LOQ\Downloads\...` yang Anda sebutkan), ikuti
   Part 1–5 sesuai instruksi di PDF template, lalu kirimkan screenshot dan
   jawaban aktualnya kembali — akan langsung kami masukkan ke dokumen ini.
3. Alternatif: jika Anda menghubungkan komputer Anda ke sesi kerja ini (fitur
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
   dibuat berdasarkan praktik yang benar-benar dijalankan (9.1.14 & 9.1.16), tapi
   WAJIB dibaca & divalidasi/diubah oleh kelompok sebelum dikumpulkan, karena ini
   bukan hasil diskusi kelompok yang sudah benar-benar terjadi.
2. **Praktik 10.1.13 dan 10.1.15** — lihat bagian hambatan di atas.

## Keamanan Data

Semua akun, password, dan hash yang muncul di laporan ini adalah **data uji lab**
yang dibuat khusus untuk latihan ini di dalam kontainer terisolasi — bukan akun
nyata, bukan akun pribadi, dan kontainer tersebut akan dihapus setelah sesi kerja
berakhir. Tidak ada kredensial akun pribadi pengguna yang digunakan atau
tersimpan di paket ini.
