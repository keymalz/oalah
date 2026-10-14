#!/usr/bin/env python3
"""Build Week4_OS_Endpoint_Security_Completed.docx from the original template
structure, filled with genuine practice results. Run with system python3
(not the uploads dir) - I -I to avoid picking up planted modules."""
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import os

BASE = "/home/user/oalah/Week4_OS_Endpoint_Security"
SS = f"{BASE}/screenshots"
OUT = f"{BASE}/Week4_OS_Endpoint_Security_Completed.docx"

doc = Document()

# Base style
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

YELLOW = RGBColor(0x7A, 0x5C, 0x00)

def h1(text):
    p = doc.add_heading(text, level=1)
    return p

def h2(text):
    p = doc.add_heading(text, level=2)
    return p

def h3(text):
    p = doc.add_heading(text, level=3)
    return p

def body(text, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    return p

def answer(text):
    """Filled answer text - highlighted as the 'yellow' filled section."""
    p = doc.add_paragraph()
    r = p.add_run("Jawaban: ")
    r.bold = True
    r2 = p.add_run(text)
    return p

def note(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True
    r.font.color.rgb = RGBColor(0x80, 0x00, 0x00)
    return p

def shot(filename, caption):
    path = os.path.join(SS, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(6.2))
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(caption)
        r.italic = True
        r.font.size = Pt(9)
    else:
        note(f"[Screenshot tidak ditemukan: {filename}]")

# ---------------- COVER ----------------
t = doc.add_heading("OS & Endpoint Security Practices", level=0)
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph("Week 4 - OS and Endpoint Security Practice Answer Sheet (Completed)").alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()
p = doc.add_paragraph()
r = p.add_run("Group name: ")
r.bold = True
r2 = p.add_run("[BELUM DIISI - menunggu konfirmasi kelompok]")
r2.font.color.rgb = YELLOW
r2.bold = True

p = doc.add_paragraph("Names & Student IDs of members present and participating in the work:")
p.runs[0].bold = True
MEMBERS = [
    "Mohammed Aatef Saleh (24523270)",
    "M Kemal Sabda Majid (24523123)",
]
for m in MEMBERS:
    doc.add_paragraph(m, style='List Number')

note("Catatan: Daftar anggota di atas FINAL - dikonfirmasi langsung oleh pengguna (2 orang, per pesan WhatsApp - "
     "lihat bukti kerja kelompok di akhir dokumen). Nama kelompok (Group name) masih belum diberikan - "
     "mohon dilengkapi sebelum pengumpulan.")

doc.add_paragraph()
body("There are four activities:")
for a in ["9.1.14 (Harden a Linux System)", "9.1.16 (Recover Password)",
          "10.1.13 (File and Data Integrity Checks)", "10.1.15 (File and Data Encryption)"]:
    doc.add_paragraph(a, style='List Bullet')

doc.add_page_break()

# ====================================================================
# 9.1.14
# ====================================================================
h1("9.1.14 (Harden a Linux System)")
note("Lingkungan praktik: VM-lab terisolasi (kontainer Docker 'CSE-LABVM', Ubuntu 22.04) yang dibuat "
     "khusus untuk tugas ini di dalam sandbox kerja - bukan akun/komputer utama pengguna. "
     "Semua perintah dan output di bawah adalah hasil eksekusi nyata, diambil via screenshot X11 asli (Xvfb+xterm+import), bukan rekayasa teks.")

h2("Part 1: Install and Update Lynis")
h3("Step 1: Determine the installed Lynis version.")
shot("9.1.14_Part1_Step1_installed_version.png", "Gambar 1. lynis show version -> 3.0.7 (terpasang dari repo Ubuntu universe)")

h3("Step 2: Install Lynis")
body("Tutorial resmi mengarahkan penambahan repository resmi CISOfy (packages.cisofy.com) untuk mendapatkan versi Lynis terbaru.")
shot("9.1.14_Part1_Step2_cisofy_blocked.png",
     "Gambar 2. Percobaan menambah repo CISOfy GAGAL - 'Could not resolve packages.cisofy.com' "
     "(domain ini diblokir oleh kebijakan jaringan lingkungan sandbox, bukan masalah pada lab). "
     "Fallback yang digunakan: apt-get install --only-upgrade lynis via repo Ubuntu.")
shot("9.1.14_Part1_Step2_update_lynis.png", "Gambar 3. Hasil fallback upgrade - Lynis tetap 3.0.7 (sudah versi terbaru di repo Ubuntu universe jammy).")
note("Catatan hambatan: repo resmi CISOfy tidak dapat diakses dari sandbox ini (kebijakan egress jaringan organisasi). "
     "Versi Lynis yang dipakai (3.0.7) adalah versi resmi dari repository Ubuntu, bukan versi arbitrer.")

h2("Part 2: Examine the current version of Lynis")
shot("9.1.14_Part2_examine_version.png", "Gambar 4. lynis show version & dpkg -l lynis mengonfirmasi versi 3.0.7 terpasang.")

h2("Part 3: Run the Lynis tool")
body("Perintah dijalankan: lynis audit system --quick (mode --quick dipakai agar audit berjalan otomatis tanpa perlu menekan Enter berulang kali di setiap tes; seluruh tes standar tetap dijalankan).")
shot("9.1.14_Part3_running_audit.png", "Gambar 5. Audit Lynis sedang berjalan nyata (229 tes dijalankan total; screenshot diambil saat fase Debian Tests/Plugins).")

h2("Part 4: Review the results of your scan and address any warnings")
body("a. Scroll to the Results section in the output for your scan.")

p = doc.add_paragraph()
r = p.add_run("How many Warnings did you receive?")
r.bold = True
answer("2 Warnings.")
shot("9.1.14_Part4_warnings_section.png", "Gambar 6. Bagian Results - Warnings (2): PKGS-7392 dan LOGG-2138.")

p = doc.add_paragraph()
r = p.add_run("How many Suggestions did you receive?")
r.bold = True
answer("39 Suggestions.")
shot("9.1.14_Part4_warning_suggestion_counts.png", "Gambar 7. Jumlah warning (2) dan suggestion (39) dihitung langsung dari /var/log/lynis-report.dat.")

body("b. You should address the warnings.", bold=True)
p = doc.add_paragraph()
r = p.add_run("Which warning are you addressing?")
r.bold = True
answer("LOGG-2138 - \"klogd is not running, which could lead to missing kernel messages in log files\". "
       "(Warning kedua, PKGS-7392 'vulnerable packages found', berada di luar scope perbaikan kelompok kami karena "
       "memerlukan penggantian banyak paket sistem dan tidak terkait langsung dengan konfigurasi hardening tunggal.)")

p = doc.add_paragraph()
r = p.add_run("What is your solution?")
r.bold = True
answer("Memasang dan menjalankan daemon syslog (rsyslog), karena menurut source code pengecekan Lynis sendiri "
       "(/usr/share/lynis/include/tests_logging, test LOGG-2138), pengecekan klogd akan DILEWATI (skip, tidak warning) "
       "apabila daemon rsyslog/systemd-journal/metalog sudah terdeteksi berjalan - klogd terpisah tidak lagi diperlukan "
       "pada sistem modern. Referensi: catatan resmi pada source test tersebut ('When using metalog, rsyslog or systemd "
       "(systemd-journal), this process is not needed').")

body("Kondisi sebelum perbaikan:")
shot("9.1.14_Fix_1_before.png", "Gambar 8. Sebelum: tidak ada proses klogd/rsyslog berjalan - lynis show details LOGG-2138 mengonfirmasi 'No klogd found'.")

body("Tindakan perbaikan:")
shot("9.1.14_Fix_2_apply.png", "Gambar 9. apt-get install rsyslog dijalankan (paket berhasil terpasang; auto-start via 'service' gagal karena policy-rc.d membatasi start service di dalam container Docker).")
shot("9.1.14_Fix_3_after_verify.png", "Gambar 10. rsyslogd dijalankan langsung sebagai proses daemon (ps aux mengonfirmasi rsyslogd aktif dengan user 'syslog').")

body("Verifikasi hasil (re-audit penuh setelah perbaikan):")
shot("9.1.14_Fix_4_verified_1warning.png",
     "Gambar 11. Lynis audit ulang menunjukkan Warnings turun dari 2 menjadi 1 - LOGG-2138 sudah tidak muncul lagi. "
     "Warning PKGS-7392 tetap ada (di luar scope perbaikan ini), dan jumlah Suggestions naik 1 (40) karena Lynis "
     "sekarang menyarankan update rsyslog itu sendiri - konsisten dan dapat diverifikasi.")

doc.add_page_break()

# ====================================================================
# 9.1.16
# ====================================================================
h1("9.1.16 (Recover Password)")
note("Lingkungan & akun: dilakukan di VM-lab terisolasi yang sama (kontainer Docker CSE-LABVM). "
     "Empat akun UJI dibuat khusus untuk latihan ini (alice, bob, eric, eve - mengikuti pola akun lab resmi Cisco "
     "'Lab - Password Cracking' yang menggunakan nama Alice/Bob/Eric/Eve), BUKAN akun pribadi/nyata milik siapa pun. "
     "File lab resmi 9.1.16 dari Cisco NetAcad tidak dapat diakses sesi ini (memerlukan login akun NetAcad yang tidak tersedia); "
     "struktur latihan (unshadow -> John the Ripper -> ganti password lebih kuat -> ulangi) mengikuti prosedur resmi yang "
     "dipakai pada lab Cisco setara (konfirmasi publik: 'Lab - Password Cracking', © Cisco, menggunakan akun Alice/Bob/Eve/Eric "
     "dan John the Ripper pada file 'mypasswd' hasil unshadow).")

h2("Part 2: Combine passwords and usernames into one text file")
body("Akun lab yang diuji: alice, bob, eric, eve (dibuat di CSE-LABVM dengan password awal yang sengaja lemah).")
body("Perintah: unshadow /etc/passwd /etc/shadow > mypasswd")
shot("9.1.16_Part2_unshadow.png", "Gambar 12. unshadow menggabungkan /etc/passwd dan /etc/shadow menjadi satu file; hash SHA-512 crypt ($6$) terlihat untuk tiap akun.")

h2("Part 3: Run John the Ripper to recover the passwords")
body("Mode pengujian 1: dictionary/wordlist attack (john --wordlist=/usr/share/john/password.lst mypasswd_lab).")
shot("9.1.16_Part3_john_wordlist.png",
     "Gambar 13. Hasil: 2 dari 4 akun pulih dalam 4 detik - eric:password, alice:summer. "
     "Akun bob dan eve belum pulih karena passwordnya mengandung akhiran angka yang tidak ada persis di wordlist polos.")
body("Mode pengujian 2: wordlist + mangling rules (john --wordlist=... --rules), untuk menjangkau variasi seperti 'kata+angka'.")
shot("9.1.16_Part3b_john_rules_remaining.png",
     "Gambar 14. Hasil: 2 akun sisanya berhasil dipulihkan dalam tambahan 10 detik - bob:cowboy1, eve:letmein1. "
     "Total akhir: 4 dari 4 akun pulih (durasi gabungan sekitar 12-16 detik pada 4 thread OpenMP).")

h2("Part 4: Change a user password to a stronger version and try to recover it")
body("Password akun 'alice' diganti menjadi string acak 14 karakter (kombinasi huruf besar/kecil, angka, simbol - "
     "dibuat dengan openssl rand, BUKAN kata kamus atau pola yang bisa ditebak wordlist/rules).")
shot("9.1.16_Part4_change_password.png", "Gambar 15. Password baru alice diset via usermod -p dengan hash SHA-512 crypt baru.")
body("Percobaan pemulihan ulang: john --wordlist=password.lst --rules, dibatasi 60 detik.")
shot("9.1.16_Part4_crack_attempt.png",
     "Gambar 16. Hasil: 0 dari 1 hash berhasil dipulihkan dalam 60 detik (wordlist + rules, 4 thread). "
     "Password alice yang baru belum berhasil dipulihkan dalam durasi pengujian 60 detik. "
     "Ini BUKAN bukti password mustahil dipulihkan secara absolut - hanya menunjukkan bahwa password acak panjang "
     "jauh lebih tahan terhadap dictionary/rule-based attack dibanding password kamus sederhana seperti pada Part 3.")

doc.add_page_break()

# ====================================================================
# 10.1.13
# ====================================================================
h1("10.1.13 (File and Data Integrity Checks)")
note("STATUS: TERHAMBAT - belum dapat dijalankan.")
body("Penjelasan hambatan: Aktivitas ini memerlukan file Cisco Packet Tracer (.pka) resmi '10.1.13 Packet Tracer - "
     "File and Data Integrity Checks'. File tersebut TIDAK disertakan dalam lampiran tugas (hanya file 10.1.15 yang "
     "dilampirkan), dan sesi kerja ini tidak memiliki akses ke portal kelas/NetAcad tempat file aslinya biasanya "
     "tersedia untuk mengunduhnya secara sah. Sesuai instruksi pengguna, kami TIDAK membuat topologi/file tiruan "
     "sebagai pengganti dan TIDAK mengarang jawaban atau screenshot untuk aktivitas ini.")
body("Catatan tambahan: bahkan jika file .pka asli tersedia, Cisco Packet Tracer (aplikasi GUI berpemilik Cisco) "
     "tidak terpasang di lingkungan sandbox ini dan tidak dapat dipasang (tidak tersedia di repository publik mana pun; "
     "pengunduhan resmi memerlukan login akun Cisco NetAcad yang tidak diminta melalui chat sesuai instruksi pengguna).")
body("Tindakan yang dibutuhkan dari pengguna:", bold=True)
for item in [
    "Unggah file asli '10.1.13 Packet Tracer - File and Data Integrity Checks.pka' dari portal kelas, ATAU",
    "Jalankan aktivitas ini sendiri di Packet Tracer pada komputer yang memiliki aplikasi tersebut terpasang, lalu "
    "bagikan screenshot dan jawaban aktualnya untuk dimasukkan ke dokumen ini."
]:
    doc.add_paragraph(item, style='List Bullet')

body("Bagian pertanyaan asli (belum terisi, menunggu file/aplikasi):", italic=True)
for q in [
    "Part 1 Step 1: Access the BR Server from Mike's PC. [Show your practice screenshots here]",
    "Part 1 Step 2: Copy the hash values from the last time the files were archived. [Show your practice screenshots here]",
    "Part 1 Step 3: Download the backup files to Mike's PC. [Show your practice screenshots here]",
    "Part 2 Step 1g: Are the two hash values for NEclients.txt the same? [Belum dapat dijawab]",
    "Part 2 Step 1h: Which file has been tampered with and has an incorrect hash? [Belum dapat dijawab]",
    "Part 2 Step 2: Escalate the cyber attack to Mike's supervisor, Sally. [Show your practice screenshots here]",
    "Part 2 Step 3: Download the suspected file to Sally's PC. [Show your practice screenshots here]",
    "Part 3: What is the computed HMAC for the contents of the file? [Belum dapat dijawab]",
    "Part 3: How is using HMAC more secure than general hashing? [Dapat dijawab konseptual - lihat catatan di bawah]",
    "Part 3: Does the HMAC hash for income.txt match the original hash copied to CSE-LABVM? [Belum dapat dijawab]",
]:
    doc.add_paragraph(q, style='List Bullet')

note("Catatan konseptual (bukan pengganti praktik nyata): HMAC (Hash-based Message Authentication Code) berbeda dari "
     "hashing biasa karena HMAC menggabungkan isi pesan dengan sebuah shared secret key sebelum di-hash. Ini memberi "
     "DUA jaminan sekaligus: (1) integritas data - perubahan isi file akan mengubah nilai HMAC, sama seperti hash "
     "biasa, dan (2) autentikasi sumber - hanya pihak yang memiliki secret key yang sama yang bisa menghasilkan HMAC "
     "yang valid, sehingga penyerang yang mengubah file TANPA mengetahui key tidak bisa memalsukan HMAC yang cocok. "
     "Hash biasa (tanpa key) hanya menjamin integritas, bukan sumber/keaslian pengirim. Catatan: HMAC TIDAK mengenkripsi "
     "isi file - ini adalah fungsi autentikasi/integritas, bukan kerahasiaan.")

doc.add_page_break()

# ====================================================================
# 10.1.15
# ====================================================================
h1("10.1.15 (File and Data Encryption)")
note("STATUS: TERHAMBAT - file .pka tersedia, namun aplikasi Cisco Packet Tracer tidak dapat dijalankan di lingkungan sandbox ini.")
body(f"File sumber yang dilampirkan pengguna telah disalin ke paket tugas ini di: "
     f"source/10.1.15_Original.pka (ukuran asli ~24.8 MB, disalin utuh tanpa diubah).")
body("Penjelasan hambatan: Cisco Packet Tracer adalah aplikasi desktop GUI berpemilik Cisco yang: (1) tidak tersedia "
     "di repository paket Linux/Ubuntu mana pun (dicek via apt-cache search - tidak ditemukan), (2) pengunduhan "
     "resmi memerlukan login akun Cisco NetAcad (kredensial tidak diminta melalui chat sesuai instruksi pengguna), "
     "dan (3) bahkan bila terpasang, aplikasi ini memerlukan interaksi GUI penuh (klik perangkat simulasi, membuka "
     "aplikasi teks/FTP client di dalam PC simulasi, Simulation Mode untuk menangkap paket) yang tidak dapat "
     "diotomasi secara andal tanpa tool kendali GUI khusus yang tidak tersedia di sesi cloud ini.")
body("File biner .pka itu sendiri diperiksa (file & hexdump): terbukti berupa data terkompresi/terenkripsi milik "
     "Cisco yang tidak dapat diuraikan tanpa aplikasi resminya - sehingga tidak ada cara sah untuk mengekstrak jawaban "
     "aktivitas tanpa menjalankan simulasinya.")

body("Tindakan yang dibutuhkan dari pengguna:", bold=True)
for item in [
    "Jalankan file 10.1.15_Original.pka ini sendiri di Cisco Packet Tracer (di komputer yang memiliki aplikasi "
    "tersebut terpasang), ikuti Part 1-5 sesuai instruksi aktivitas, lalu bagikan screenshot dan jawaban aktualnya, ATAU",
    "Jika tersedia, hubungkan sesi ini ke komputer pengguna sendiri (fitur Remote Control/Cowork) yang sudah memiliki "
    "Packet Tracer terpasang, agar praktik dapat dijalankan langsung dari sesi ini."
]:
    doc.add_paragraph(item, style='List Bullet')

body("Bagian pertanyaan asli (belum terisi, menunggu aplikasi Packet Tracer):", italic=True)
for q in [
    "Part 1 Step 1-2: Access text document on Mary's Laptop; decrypt Mary's FTP info. "
    "What is the username and password for Mary's FTP account? [Belum dapat dijawab]",
    "Part 2 Step 1: View confidential document on Laptop BR-1. What form is the data in? [Belum dapat dijawab]",
    "Part 2 Step 2-3: Connect to BR Server; upload file via FTP. What would be in clear text if captured? [Belum dapat dijawab]",
    "Part 3 Step 1-2: Access text document on Bob's Laptop; decrypt Bob's FTP info. "
    "What is the username and password for Bob's FTP account? [Belum dapat dijawab]",
    "Part 4 Step 1-2: Connect to BR Server; download file to Bob's PC. What would be in clear text crossing the internet? [Belum dapat dijawab]",
    "Part 5 Step 1: Get the decryption key. What is the decryption key for clientinfo.enc? [Belum dapat dijawab]",
    "Part 5 Step 2: Decrypt clientinfo.enc to clientinfo.txt. What is the first name listed? [Belum dapat dijawab]",
]:
    doc.add_paragraph(q, style='List Bullet')

doc.add_page_break()

# ====================================================================
# Reflection
# ====================================================================
h1("Activity Reflection")
p = doc.add_paragraph()
r = p.add_run("What did you learn from this activity?")
r.bold = True
note("[DRAF - berdasarkan praktik yang benar-benar dijalankan (9.1.14 & 9.1.16). WAJIB divalidasi/diubah oleh "
     "kelompok sebelum dikumpulkan - draf ini BUKAN hasil diskusi kelompok yang sudah terjadi.]")
answer("(Draf) Kelompok mempelajari bahwa hardening sistem Linux dengan Lynis memberikan audit terukur (229 tes, "
       "index hardening 57) yang bisa ditindaklanjuti satu per satu, dan bahwa satu warning dapat diselesaikan dengan "
       "memahami akar penyebab tes tersebut (membaca source code tes Lynis sendiri), bukan hanya menjalankan perintah "
       "secara acak. Pada praktik password recovery, kelompok melihat langsung bagaimana password kamus (seperti "
       "\"password\" atau \"summer\") dapat dipulihkan dalam hitungan detik, sedangkan password acak sepanjang 14 "
       "karakter bertahan terhadap serangan wordlist+rules selama durasi pengujian - menegaskan pentingnya kebijakan "
       "password yang kuat.")

p = doc.add_paragraph()
r = p.add_run("What are you still confused about? / What do you still need clarification on?")
r.bold = True
note("[DRAF - WAJIB divalidasi/diubah oleh kelompok.]")
answer("(Draf) Kelompok masih perlu klarifikasi mengenai bagaimana mengakses materi lab resmi 9.1.14/9.1.16 dan file "
       ".pka 10.1.13 dari portal kelas, serta ketersediaan aplikasi Cisco Packet Tracer untuk menyelesaikan 10.1.13 "
       "dan 10.1.15 secara penuh dengan data resmi dari Cisco (bukan lingkungan substitusi).")

doc.add_page_break()
h1("Group Work Evidence")
body("If you worked together in person, please attach a photo. If you worked together online, please attach a screenshot.")
note("Bukti kerja kelompok (koordinasi daring via WhatsApp) - diberikan langsung oleh pengguna, bukan rekayasa.")
shot("GroupWorkEvidence_WhatsApp.png",
     "Gambar 17. Screenshot percakapan WhatsApp kelompok - konfirmasi nama dan NIM anggota yang berpartisipasi: "
     "Mohammed Aatef Saleh (24523270) dan M Kemal Sabda Majid (24523123).")

doc.save(OUT)
print("Saved:", OUT)
print("Pages approx (paragraphs):", len(doc.paragraphs))
