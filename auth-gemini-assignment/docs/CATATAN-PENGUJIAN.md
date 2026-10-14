# Catatan Pengujian

Dibangkitkan otomatis dari `docs/test-results/` (jalankan `python3 docs/build_notes.py`).

**Lingkungan uji:** Firebase Auth Emulator (`demo-auth-gemini`) + Gemini **MOCK** (kecuali tes key palsu ke Gemini API nyata). Hasil di emulator **tidak membuktikan** Google Sign-In, Firebase Console, atau jawaban Gemini nyata.

## Backend Node.js (`npm test`)

| # | Skenario | Status |
|---|---|---|
| B-01 | dashboard tanpa login diarahkan ke /login | Lulus |
| B-02 | POST /api/gemini tanpa autentikasi ditolak 401 dan Gemini tidak dipanggil | Lulus |
| B-03 | bearer token palsu ditolak 401 | Lulus |
| B-04 | session cookie palsu ditolak 401 dan cookie dihapus | Lulus |
| B-05 | sessionLogin tanpa CSRF ditolak 403 | Lulus |
| B-06 | sessionLogin dengan ID token palsu ditolak 401 | Lulus |
| B-07 | alur sesi: login -> dashboard -> gemini -> logout | Lulus |
| B-08 | bearer token valid (gaya Flutter) diterima | Lulus |
| B-09 | error Gemini dipetakan dan tidak membocorkan rahasia | Lulus |
| B-10 | CORS hanya untuk origin yang diizinkan | Lulus |
| B-11 | key Gemini tidak valid -> 503 GEMINI_BAD_KEY tanpa membocorkan key | Lulus |

## E2E Node.js (Playwright)

| ID | Skenario | Diharapkan | Aktual | Status | Bukti |
|---|---|---|---|---|---|
| N-01 | Halaman register tampil | Form nama, email, password, konfirmasi, tombol Daftar & Google | Sesuai harapan | Lulus | 01-node-register.png |
| N-02 | Validasi: email tidak valid, password lemah, nama pendek | Pesan error per kolom, tidak ada request ke Firebase | Sesuai harapan | Lulus | 02-node-validasi-register.png |
| N-03 | Password dan konfirmasi tidak cocok | Pesan "Konfirmasi password tidak cocok." | Sesuai harapan | Lulus | 03-node-password-tidak-cocok.png |
| N-04 | Toggle tampil/sembunyikan password | Tipe input berubah text <-> password | Sesuai harapan | Lulus |  |
| N-05 | Register email baru (email/password) | Akun dibuat, diarahkan ke /dashboard dengan nama & email | Sesuai harapan | Lulus | 04-node-dashboard-setelah-register.png |
| N-06 | Refresh dashboard saat sesi valid | Tetap di dashboard | Sesuai harapan | Lulus |  |
| N-07 | Tanya Gemini (MOCK) dari dashboard | Jawaban muncul; berlabel MOCK karena bukan Gemini asli | Jawaban MOCK tampil (BUKAN bukti Gemini nyata) | Lulus | 05-node-gemini-mock.png |
| N-08 | Pertanyaan kosong ditolak di klien | Pesan "Pertanyaan tidak boleh kosong." | Sesuai harapan | Lulus |  |
| N-09 | Logout lalu buka kembali /dashboard | Diarahkan ke /login | Sesuai harapan | Lulus | 06-node-dashboard-ditolak-setelah-logout.png |
| N-10 | Login: email tidak valid | Pesan format email tidak valid | Sesuai harapan | Lulus |  |
| N-11 | Login: password salah | Alert "Email atau password salah." | Sesuai harapan | Lulus | 07-node-login-kredensial-salah.png |
| N-12 | Login email/password benar | Masuk ke dashboard | Sesuai harapan | Lulus | 08-node-dashboard-login-email.png |
| N-13 | Session cookie berflag HttpOnly & SameSite | Cookie __session HttpOnly, SameSite=Lax; tidak terbaca oleh JavaScript | httpOnly=true, sameSite=Lax, secure=false (Secure aktif hanya di NODE_ENV=production/HTTPS) | Lulus |  |
| N-14 | Sesi hilang/kedaluwarsa saat memakai Gemini | API 401 -> diarahkan ke /login?expired=1 dengan pesan sesi berakhir | Sesuai harapan | Lulus | 09-node-sesi-berakhir.png |
| N-15 | Register email yang sudah dipakai | Pesan "Email ini sudah terdaftar. Silakan masuk." | Sesuai harapan | Lulus | 10-node-register-email-terpakai.png |
| N-16 | Akses /dashboard tanpa login (konteks bersih) | 302 ke /login | /dashboard -> 302 /login; POST /api/gemini -> 401 | Lulus |  |
| N-17 | Login Google via kredensial IdP tiruan emulator (BUKAN Google nyata) | Dashboard menampilkan metode login "Google" | Provider "Google" tampil (jalur emulator, bukan OAuth Google asli) | Lulus | 11-node-dashboard-google-emulator.png |
| N-18 | Klik tombol "Masuk dengan Google" (popup) di sandbox | Popup Google asli | BELUM DIUJI: sandbox memblokir apis.google.com, popup tidak dapat dibuka. Perlu uji manual di Firebase nyata. | Belum diuji |  |

## E2E Flutter Web (Playwright)

| ID | Skenario | Diharapkan | Aktual | Status | Bukti |
|---|---|---|---|---|---|
| F-01 | Halaman login Flutter Web tampil | Email, password, Masuk, Masuk dengan Google, tautan Daftar | Sesuai harapan | Lulus | 12-flutter-login.png |
| F-02 | Akses /#/dashboard sebelum login | AuthGate menampilkan halaman login, bukan dashboard | Sesuai harapan | Lulus | 13-flutter-dashboard-ditolak-sebelum-login.png |
| F-03 | Login: kolom kosong & email tidak valid | Pesan validasi per kolom | Sesuai harapan | Lulus | 14-flutter-validasi-login.png |
| F-04 | Pindah ke halaman register | Form Nama, Email, Password, Konfirmasi, Daftar, Google | Sesuai harapan | Lulus | 15-flutter-register.png |
| F-05 | Register: validasi nama/email/password & konfirmasi tidak cocok | Pesan error muncul | Sesuai harapan | Lulus | 16-flutter-validasi-register.png |
| F-06 | Register email baru | Akun dibuat dan dashboard tampil dengan nama & email | Sesuai harapan | Lulus | 17-flutter-dashboard-setelah-register.png |
| F-07 | Tanya Gemini (MOCK) lewat backend Node.js dengan Bearer token | Jawaban MOCK tampil | Jawaban MOCK tampil (BUKAN bukti Gemini nyata) | Lulus | 18-flutter-gemini-mock.png |
| F-08 | Refresh halaman saat sesi valid | Tetap di dashboard | Sesuai harapan | Lulus |  |
| F-09 | Logout | Kembali ke halaman login | Sesuai harapan | Lulus |  |
| F-10 | Login: password salah | Pesan "Email atau password salah." | Sesuai harapan | Lulus | 19-flutter-login-kredensial-salah.png |
| F-11 | Login email/password benar | Dashboard tampil | Sesuai harapan | Lulus | 20-flutter-dashboard-login-email.png |
| F-12 | Logout lalu register email yang sudah dipakai | Pesan "Email ini sudah terdaftar." | Sesuai harapan | Lulus | 21-flutter-register-email-terpakai.png |
| F-13 | Login Google via kredensial IdP tiruan emulator (BUKAN Google nyata) | Dashboard menampilkan metode login "Google" | Provider "Google" tampil (jalur emulator, bukan OAuth Google asli) | Lulus | 22-flutter-dashboard-google-emulator.png |
| F-14 | Google (dari dashboard Google) mengakses Gemini lewat backend | Jawaban MOCK tampil | Sesuai harapan | Lulus |  |
| F-15 | Klik tombol "Masuk dengan Google" (popup) di sandbox | Popup Google asli | BELUM DIUJI: sandbox memblokir apis.google.com, popup tidak dapat dibuka. Perlu uji manual di Firebase nyata. | Belum diuji |  |

## Flutter

```
No issues found! (ran in 8.2s)
00:03 +5: All tests passed!
```

## Belum diuji (butuh akun/konfigurasi nyata)

- Provider Email/Password & Google aktif di Firebase Console; daftar pengguna di Console
- Pembuatan API key AI Studio; jawaban Gemini nyata (Node.js dan Flutter Web)
- Login Google nyata (popup OAuth) dan pembatalan popup nyata di kedua website
- Sesi kedaluwarsa karena waktu; timeout/kuota Gemini nyata; flag Secure pada HTTPS production
