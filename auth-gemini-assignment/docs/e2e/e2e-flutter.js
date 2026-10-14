// E2E Flutter Web terhadap Firebase Auth EMULATOR + backend Node.js (Gemini MOCK).
// Catatan sandbox: SDK JS Firebase biasanya dimuat dari gstatic.com (diblokir di sandbox),
// jadi disajikan dari paket npm firebase@12.19.0 (versi yang sama) lewat page.route. Kode aplikasi tidak diubah.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { launch, recorder, SHOTS } = require('./lib');

const BASE = 'http://localhost:8080/';
const SDK = 'https://www.gstatic.com/firebasejs/12.19.0';
const stamp = Date.now();
const email = `uji.flutter.${stamp}@example.com`;
const password = 'Rahasia123';

async function newCtx(browser) {
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 780 }, locale: 'id-ID' });
  const all = fs.readFileSync(path.join(__dirname, '.build', 'firebase-all.js'));
  const h = { 'access-control-allow-origin': '*' };
  await ctx.route(`${SDK}/firebase-app.js`, (r) => r.fulfill({ contentType: 'text/javascript', body: all, headers: h }));
  await ctx.route(`${SDK}/firebase-auth.js`, (r) => r.fulfill({ contentType: 'text/javascript', body: `export * from "${SDK}/firebase-app.js";`, headers: h }));
  return ctx;
}

async function emulatorUser(mail) {
  const r = await fetch('http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/projects/demo-auth-gemini/accounts:batchGet?maxResults=200', {
    headers: { Authorization: 'Bearer owner' },
  });
  const u = (await r.json()).users?.find((x) => x.email === mail);
  assert.ok(u, 'pengguna tidak ada di emulator');
  return u;
}

async function open(page, hash = '') {
  await page.goto(BASE + hash);
  if (hash) await page.reload(); // goto dengan hash saja tidak memuat ulang dokumen
  await page.waitForSelector('flt-semantics-placeholder', { state: 'attached', timeout: 30000 });
  await page.evaluate(() => document.querySelector('flt-semantics-placeholder')?.click());
  await page.waitForTimeout(800);
}

(async () => {
  const rec = recorder('flutter-e2e');
  const browser = await launch();
  const ctx = await newCtx(browser);
  const page = await ctx.newPage();
  rec.onFail = async (id) => {
    await page.screenshot({ path: path.join(__dirname, '.build', `gagal-${id}.png`) }).catch(() => {});
    const t = await page.evaluate(() => [...document.querySelectorAll('flt-semantics')].map((e) => (e.getAttribute('role') || '-') + ':' + (e.getAttribute('aria-label') || e.textContent).slice(0, 50)).slice(0, 14)).catch(() => []);
    console.log('   semantik (diagnosis):', JSON.stringify(t));
  };
  const shot = async (slug) => {
    const f = rec.nextName(slug);
    await page.screenshot({ path: path.join(SHOTS, f) });
    return f;
  };
  const tb = (name) => page.getByRole('textbox', { name, exact: false }).first();
  const btn = (name) => page.getByRole('button', { name }).first();
  const text = (t) => page.getByText(t, { exact: false }).first();
  // Field Flutter Web: klik, pilih semua, ketik (fill() kurang andal pada field berisi).
  const put = async (name, value) => {
    for (let attempt = 1; attempt <= 4; attempt++) {
      const el = tb(name);
      await el.click();
      await page.keyboard.press('Control+A');
      await page.keyboard.press('Backspace');
      if (value) await page.keyboard.type(value, { delay: 8 });
      await page.waitForTimeout(150);
      // Verifikasi nilai <input> yang sedang fokus (editing host Flutter).
      const actual = await page.evaluate(() => document.activeElement?.value ?? '');
      if (actual === value) return;
    }
    throw new Error(`Gagal mengisi field "${name}" dengan benar`);
  };
  const labelHas = (t) => [...document.querySelectorAll('flt-semantics')].some((e) => (e.getAttribute('aria-label') || '').includes(t) || (e.textContent || '').includes(t));
  const seen = async (t, ms = 10000) => page.waitForFunction(`(${labelHas.toString()})(${JSON.stringify(t)})`, null, { timeout: ms });
  const count = async (t) => (await page.evaluate(`(${labelHas.toString()})(${JSON.stringify(t)})`)) ? 1 : 0;

  await rec.step('F-01', 'Halaman login Flutter Web tampil', 'Email, password, Masuk, Masuk dengan Google, tautan Daftar', async () => {
    await open(page);
    await seen('Masuk dengan Google');
    await seen('Daftar di sini');
    return { evidence: await shot('flutter-login') };
  });

  await rec.step('F-02', 'Akses /#/dashboard sebelum login', 'AuthGate menampilkan halaman login, bukan dashboard', async () => {
    await open(page, '#/dashboard');
    await seen('Masuk dengan Google');
    assert.equal(await count('Tanya Gemini\nJawaban'), 0);
    return { evidence: await shot('flutter-dashboard-ditolak-sebelum-login') };
  });

  await rec.step('F-03', 'Login: kolom kosong & email tidak valid', 'Pesan validasi per kolom', async () => {
    await btn('Masuk').click();
    await seen('Email wajib diisi.');
    await seen('Password wajib diisi.');
    await put('Email', 'bukan-email');
    await btn('Masuk').click();
    await seen('Format email tidak valid.');
    return { evidence: await shot('flutter-validasi-login') };
  });

  await rec.step('F-04', 'Pindah ke halaman register', 'Form Nama, Email, Password, Konfirmasi, Daftar, Google', async () => {
    await page.getByRole('button', { name: 'Daftar di sini' }).click();
    await seen('Daftar akun');
    await seen('Daftar dengan Google');
    return { evidence: await shot('flutter-register') };
  });

  await rec.step('F-05', 'Register: validasi nama/email/password & konfirmasi tidak cocok', 'Pesan error muncul', async () => {
    await put('Nama', 'B');
    await put('Email', 'abc');
    await put('Password (min', 'abc');
    await put('Konfirmasi password', 'xyz');
    await btn('Daftar').click();
    await seen('Nama minimal 2 karakter.');
    await seen('Format email tidak valid.');
    await seen('Password minimal 8 karakter.');
    await seen('Konfirmasi password tidak cocok.');
    return { evidence: await shot('flutter-validasi-register') };
  });

  await rec.step('F-06', 'Register email baru', 'Akun dibuat dan dashboard tampil dengan nama & email', async () => {
    await put('Nama', 'Penguji Flutter');
    await put('Email', email);
    await put('Password (min', password);
    await put('Konfirmasi password', password);
    await btn('Daftar').click();
    await seen('Halo, Penguji Flutter', 15000);
    const u = await emulatorUser(email);
    assert.equal(u.providerUserInfo[0].providerId, 'password');
    return { evidence: await shot('flutter-dashboard-setelah-register') };
  });

  await rec.step('F-07', 'Tanya Gemini (MOCK) lewat backend Node.js dengan Bearer token', 'Jawaban MOCK tampil', async () => {
    await put('Pertanyaan Anda', 'Jelaskan apa itu Firebase Authentication dalam 3 kalimat.');
    await btn('Kirim ke Gemini').click();
    await seen('MOCK — bukan jawaban Gemini asli', 20000);
    return { actual: 'Jawaban MOCK tampil (BUKAN bukti Gemini nyata)', evidence: await shot('flutter-gemini-mock') };
  });

  await rec.step('F-08', 'Refresh halaman saat sesi valid', 'Tetap di dashboard', async () => {
    await page.reload();
    await page.waitForSelector('flt-semantics-placeholder', { state: 'attached' });
    await page.evaluate(() => document.querySelector('flt-semantics-placeholder')?.click());
    await seen('Halo, Penguji Flutter', 15000);
  });

  await rec.step('F-09', 'Logout', 'Kembali ke halaman login', async () => {
    await btn('Keluar').click();
    await seen('Masuk dengan Google');
    assert.equal(await count('Tanya Gemini\nJawaban'), 0);
  });

  await rec.step('F-10', 'Login: password salah', 'Pesan "Email atau password salah."', async () => {
    await put('Email', email);
    await put('Password', 'SalahBanget1');
    await btn('Masuk').click();
    await seen('Email atau password salah.');
    return { evidence: await shot('flutter-login-kredensial-salah') };
  });

  await rec.step('F-11', 'Login email/password benar', 'Dashboard tampil', async () => {
    await put('Password', password);
    await btn('Masuk').click();
    await seen('Halo, Penguji Flutter', 15000);
    return { evidence: await shot('flutter-dashboard-login-email') };
  });

  await rec.step('F-12', 'Logout lalu register email yang sudah dipakai', 'Pesan "Email ini sudah terdaftar."', async () => {
    await btn('Keluar').click();
    await seen('Masuk dengan Google');
    await page.getByRole('button', { name: 'Daftar di sini' }).click();
    await seen('Daftar akun');
    await put('Nama', 'Penguji Flutter');
    await put('Email', email);
    await put('Password (min', password);
    await put('Konfirmasi password', password);
    await btn('Daftar').click();
    await seen('Email ini sudah terdaftar. Silakan masuk.');
    return { evidence: await shot('flutter-register-email-terpakai') };
  });

  await rec.step('F-13', 'Login Google via kredensial IdP tiruan emulator (BUKAN Google nyata)', 'Dashboard menampilkan metode login "Google"', async () => {
    await page.evaluate(async () => {
      const a = window.firebase_auth;
      const auth = a.getAuth();
      const fake = JSON.stringify({ sub: 'google-sub-' + Date.now(), email: `uji.google.flutter.${Date.now()}@example.com`, email_verified: true, name: 'Penguji Google', display_name: 'Penguji Google' });
      await a.signInWithCredential(auth, a.GoogleAuthProvider.credential(fake));
    });
    await seen('Halo, Penguji Google', 15000);
    await seen('Metode login');
    return { actual: 'Provider "Google" tampil (jalur emulator, bukan OAuth Google asli)', evidence: await shot('flutter-dashboard-google-emulator') };
  });

  await rec.step('F-14', 'Google (dari dashboard Google) mengakses Gemini lewat backend', 'Jawaban MOCK tampil', async () => {
    await put('Pertanyaan Anda', 'Halo Gemini');
    await btn('Kirim ke Gemini').click();
    await seen('MOCK — bukan jawaban Gemini asli', 20000);
  });

  await rec.step('F-15', 'Klik tombol "Masuk dengan Google" (popup) di sandbox', 'Popup Google asli', async () => {
    throw new Error('BELUM DIUJI: sandbox memblokir apis.google.com, popup tidak dapat dibuka. Perlu uji manual di Firebase nyata.');
  });

  rec.save();
  await browser.close();
})();
