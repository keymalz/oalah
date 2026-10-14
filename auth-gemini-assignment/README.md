# Praktikum: Login/Register Node.js + Flutter Web dengan Google Sign-In dan Gemini API

Dua website dengan fitur sama: **register**, **login email/password**, **login Google**, **dashboard terproteksi**, **logout**, dan **"Tanya Gemini"**.

```
auth-gemini-assignment/
├── node-web/      Website Node.js (Express + EJS) sekaligus backend (verifikasi Firebase + Gemini)
├── flutter-web/   Website Flutter Web (Firebase Auth) yang memanggil backend Node.js
├── screenshots/   Screenshot hasil pengujian (lihat docs/ untuk keterangan asal tiap gambar)
├── docs/          Laporan, hasil pengujian (test-results/), skrip E2E (e2e/)
├── firebase.json  Konfigurasi Auth Emulator untuk pengujian lokal
└── README.md
```

## Status jujur (baca dulu)

| Bagian | Status |
|---|---|
| Kode kedua website + backend + tes | Selesai, tes lulus (lihat `docs/test-results/`) |
| Pengujian terhadap **Firebase Auth Emulator** + **Gemini MOCK** | Lulus |
| Proyek Firebase **nyata**, provider Email/Password & Google aktif | **Belum dibuat** (perlu akun Google Anda) |
| API key **Google AI Studio** nyata + jawaban Gemini nyata | **Belum dibuat** (perlu akun Google Anda) |
| Login Google **nyata** (popup OAuth) di kedua website | **Belum diuji** |

Alasan: lingkungan pengembangan kode ini tidak punya login Google dan memblokir `aistudio.google.com`,
`console.firebase.google.com`, dan `apis.google.com`. Langkah 1–3 di bawah adalah yang perlu Anda lakukan.

## Arsitektur singkat

* **Firebase Authentication** menyimpan dan mengelola kredensial pengguna (password di-hash oleh Firebase;
  aplikasi ini tidak menyimpan password sendiri).
* **Node.js (Express)** menjalankan website Node.js dan backend API. Backend memakai **Firebase Admin SDK**
  untuk memverifikasi identitas sebelum memanggil Gemini.
* **Website Node.js**: SDK Firebase di browser melakukan register/login → ID token ditukar server menjadi
  **session cookie** (`HttpOnly`, `SameSite=Lax`, `Secure` di production) → halaman `/dashboard` dan `/api/*`
  memverifikasi cookie itu. Permintaan POST berbasis cookie dilindungi **token CSRF**.
* **Flutter Web**: `firebase_auth` melakukan login → Flutter mengirim **Firebase ID token** sebagai
  `Authorization: Bearer ...` ke `POST /api/gemini`; backend memverifikasinya. CORS dibatasi ke `ALLOWED_ORIGINS`.
* **Gemini**: API key hanya ada di `.env` server (`GEMINI_API_KEY`). Tidak ada key di browser maupun di build Flutter.

## Prasyarat

* Node.js ≥ 22 (diuji 22.22.0), npm
* Flutter stable (diuji 3.47.7 / Dart 3.13.5), Chrome
* Untuk pengujian lokal tanpa akun Google: Java 21 dan `firebase-tools` (`npm i -g firebase-tools`)

## 1. Konfigurasi Firebase nyata (dilakukan oleh Anda)

1. Buka <https://console.firebase.google.com> → **Add project** (paket Spark/gratis; jangan aktifkan billing).
2. **Build → Authentication → Get started → Sign-in method**: aktifkan **Email/Password** dan **Google**
   (pilih *support email* untuk Google).
3. **Authentication → Settings → Authorized domains**: pastikan `localhost` ada; tambahkan domain deploy bila ada.
4. **Project settings → General → Your apps → Web (`</>`)**: daftarkan app, salin `apiKey`, `authDomain`,
   `projectId`, `appId`, `messagingSenderId` (nilai ini bersifat publik).
5. **Project settings → Service accounts → Generate new private key**: simpan sebagai
   `node-web/secrets/serviceAccount.json`. **Jangan commit/kirim file ini** (sudah di `.gitignore`).
   Alternatif tanpa file: `gcloud auth application-default login`.

## 2. Membuat API key Gemini di Google AI Studio (dilakukan oleh Anda)

1. Buka <https://aistudio.google.com/apikey> → **Create API key** (pilih/buat proyek Google Cloud; tier gratis cukup).
2. Salin key ke `node-web/.env` sebagai `GEMINI_API_KEY`.
3. Di AI Studio, lihat daftar model yang tersedia untuk akun Anda, lalu isi `GEMINI_MODEL`
   (default `gemini-3.5-flash`; **nama model belum diverifikasi terhadap akun Anda**).

## 3. Menjalankan website Node.js + backend

```bash
cd node-web
npm install
cp .env.example .env        # lalu isi FIREBASE_* , GOOGLE_APPLICATION_CREDENTIALS , GEMINI_API_KEY , GEMINI_MODEL
npm run build:client        # membundel SDK Firebase untuk browser -> public/js/*.bundle.js
npm start                   # http://localhost:3000
```

`ALLOWED_ORIGINS` di `.env` harus memuat origin Flutter Web (default `http://localhost:8080`).

## 4. Menjalankan Flutter Web

```bash
cd flutter-web
cp dart-defines.example.json dart-defines.json   # isi dengan konfigurasi web Firebase (langkah 1.4)
flutter pub get
flutter run -d chrome --web-port 8080 --dart-define-from-file=dart-defines.json
# build produksi:
flutter build web --release --dart-define-from-file=dart-defines.json
```

Alternatif resmi: `dart pub global activate flutterfire_cli && flutterfire configure` akan menghasilkan
`lib/firebase_options.dart` (menimpa file yang ada).

## 5. Urutan demonstrasi

1. Buka `http://localhost:3000/register` → daftar (nama, email, password, konfirmasi) → masuk ke dashboard.
2. Di dashboard, isi pertanyaan pada **Tanya Gemini** → jawaban tampil. Klik **Keluar**.
3. Buka `/dashboard` langsung → dialihkan ke `/login` (terbukti terproteksi).
4. Login email/password → dashboard. Lalu logout dan coba **Masuk dengan Google**.
5. Ulangi di Flutter Web (`http://localhost:8080`): register, login, Google, Tanya Gemini, Keluar.

## Pengujian lokal tanpa akun Google (Auth Emulator + Gemini mock)

```bash
# terminal 1 (dari folder ini)
firebase emulators:start --only auth --project demo-auth-gemini
# terminal 2: backend + tes otomatis (Gemini di-inject palsu)
cd node-web && FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099 npm test
# terminal 3: server Node untuk E2E
FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099 GEMINI_MOCK=1 ALLOWED_ORIGINS=http://localhost:8080 node server.js
# terminal 4: Flutter dibangun untuk emulator dan disajikan di :8080
cd flutter-web && flutter test && flutter analyze
flutter build web --release --no-web-resources-cdn --dart-define=USE_AUTH_EMULATOR=true --dart-define=API_BASE_URL=http://localhost:3000
(cd build/web && python3 -m http.server 8080 --bind 127.0.0.1)
# terminal 5: E2E Playwright (screenshot masuk ke ../../screenshots)
cd docs/e2e && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install && npm run build-shim
node e2e-node.js && SHOT_START=12 node e2e-flutter.js
```

Catatan: mode `GEMINI_MOCK=1` menghasilkan jawaban berlabel `[MOCK — bukan jawaban Gemini asli]`.
Pada E2E, "login Google" memakai **kredensial IdP tiruan milik emulator** (bukan popup Google), dan SDK JS Firebase
untuk Flutter disajikan dari paket npm karena `gstatic.com` diblokir di lingkungan pengembangan. Rinciannya di laporan.

## Endpoint backend

| Metode & path | Autentikasi | Fungsi |
|---|---|---|
| `GET /login`, `/register` | – | Halaman (diarahkan ke dashboard bila sudah login) |
| `GET /dashboard` | session cookie | Dashboard (302 ke `/login` bila tidak sah) |
| `POST /api/sessionLogin` | CSRF + ID token segar | Menukar ID token menjadi session cookie |
| `POST /api/sessionLogout` | CSRF | Menghapus cookie |
| `GET /api/me` | cookie **atau** Bearer | Info pengguna |
| `POST /api/gemini` | cookie (+CSRF) **atau** Bearer | `{prompt}` → `{answer, model}`; batas 2000 karakter, 10 permintaan/menit/pengguna |

## Keamanan

* Rahasia hanya di `node-web/.env` dan `node-web/secrets/` (keduanya di `.gitignore`).
* `.env.example` hanya berisi placeholder. Jangan menaruh service account/API key di screenshot, laporan, atau arsip.
* Pesan error dari Gemini dipetakan ke kode aman; detail asli (yang bisa memuat potongan konfigurasi) tidak dikirim ke klien.
* Logout menghapus cookie di browser; sesi tidak dicabut di server (lihat keterbatasan di laporan).
