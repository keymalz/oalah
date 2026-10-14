// E2E website Node.js terhadap Firebase Auth EMULATOR + Gemini MOCK.
// Prasyarat: emulator di :9099, server Node di :3000 (FIREBASE_AUTH_EMULATOR_HOST & GEMINI_MOCK=1).
const assert = require('node:assert/strict');
const path = require('node:path');
const { launch, recorder, SHOTS } = require('./lib');

const BASE = 'http://localhost:3000';
const stamp = Date.now();
const email = `uji.node.${stamp}@example.com`;
const password = 'Rahasia123';

(async () => {
  const rec = recorder('node-e2e');
  const browser = await launch();
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 760 }, locale: 'id-ID' });
  const page = await ctx.newPage();
  const shot = async (slug) => {
    const f = rec.nextName(slug);
    await page.screenshot({ path: path.join(SHOTS, f) });
    return f;
  };
  const fillRegister = async (v) => {
    for (const [k, val] of Object.entries(v)) await page.fill(`#${k}`, val);
  };

  await rec.step('N-01', 'Halaman register tampil', 'Form nama, email, password, konfirmasi, tombol Daftar & Google', async () => {
    await page.goto(`${BASE}/register`);
    await page.waitForSelector('#register-form');
    for (const s of ['#name', '#email', '#password', '#confirm', '#submit-btn', '#google-btn']) assert.ok(await page.locator(s).isVisible(), s);
    return { evidence: await shot('node-register') };
  });

  await rec.step('N-02', 'Validasi: email tidak valid, password lemah, nama pendek', 'Pesan error per kolom, tidak ada request ke Firebase', async () => {
    await fillRegister({ name: 'B', email: 'bukan-email', password: 'abc', confirm: 'abc' });
    await page.click('#submit-btn');
    assert.equal(await page.textContent('#name-error'), 'Nama minimal 2 karakter.');
    assert.equal(await page.textContent('#email-error'), 'Format email tidak valid.');
    assert.equal(await page.textContent('#password-error'), 'Password minimal 8 karakter.');
    return { evidence: await shot('node-validasi-register') };
  });

  await rec.step('N-03', 'Password dan konfirmasi tidak cocok', 'Pesan "Konfirmasi password tidak cocok."', async () => {
    await fillRegister({ name: 'Penguji Node', email, password, confirm: 'Beda12345' });
    await page.click('#submit-btn');
    assert.equal(await page.textContent('#confirm-error'), 'Konfirmasi password tidak cocok.');
    return { evidence: await shot('node-password-tidak-cocok') };
  });

  await rec.step('N-04', 'Toggle tampil/sembunyikan password', 'Tipe input berubah text <-> password', async () => {
    await page.click('[data-target="password"]');
    assert.equal(await page.getAttribute('#password', 'type'), 'text');
    await page.click('[data-target="password"]');
    assert.equal(await page.getAttribute('#password', 'type'), 'password');
  });

  await rec.step('N-05', 'Register email baru (email/password)', 'Akun dibuat, diarahkan ke /dashboard dengan nama & email', async () => {
    await fillRegister({ confirm: password });
    await Promise.all([page.waitForURL('**/dashboard'), page.click('#submit-btn')]);
    assert.match(await page.textContent('h1'), /Halo, Penguji Node/);
    assert.equal(await page.textContent('#user-email'), email);
    assert.equal(await page.textContent('#user-provider'), 'Email dan password');
    return { evidence: await shot('node-dashboard-setelah-register') };
  });

  await rec.step('N-06', 'Refresh dashboard saat sesi valid', 'Tetap di dashboard', async () => {
    await page.reload();
    assert.match(page.url(), /\/dashboard$/);
    assert.equal(await page.textContent('#user-email'), email);
  });

  await rec.step('N-07', 'Tanya Gemini (MOCK) dari dashboard', 'Jawaban muncul; berlabel MOCK karena bukan Gemini asli', async () => {
    await page.fill('#prompt', 'Jelaskan apa itu Firebase Authentication dalam 3 kalimat.');
    await page.click('#ask-btn');
    await page.waitForFunction(() => document.querySelector('#answer').textContent.startsWith('[MOCK'));
    assert.match(await page.textContent('#answer-meta'), /MOCK/);
    return { actual: 'Jawaban MOCK tampil (BUKAN bukti Gemini nyata)', evidence: await shot('node-gemini-mock') };
  });

  await rec.step('N-08', 'Pertanyaan kosong ditolak di klien', 'Pesan "Pertanyaan tidak boleh kosong."', async () => {
    await page.fill('#prompt', '   ');
    await page.click('#ask-btn');
    assert.equal(await page.textContent('#alert'), 'Pertanyaan tidak boleh kosong.');
  });

  await rec.step('N-09', 'Logout lalu buka kembali /dashboard', 'Diarahkan ke /login', async () => {
    await Promise.all([page.waitForURL('**/login'), page.click('#logout-btn')]);
    await page.goto(`${BASE}/dashboard`);
    assert.match(page.url(), /\/login$/);
    return { evidence: await shot('node-dashboard-ditolak-setelah-logout') };
  });

  await rec.step('N-10', 'Login: email tidak valid', 'Pesan format email tidak valid', async () => {
    await page.fill('#email', 'abc');
    await page.fill('#password', 'x');
    await page.click('#submit-btn');
    assert.equal(await page.textContent('#email-error'), 'Format email tidak valid.');
  });

  await rec.step('N-11', 'Login: password salah', 'Alert "Email atau password salah."', async () => {
    await page.fill('#email', email);
    await page.fill('#password', 'SalahBanget1');
    await page.click('#submit-btn');
    await page.waitForFunction(() => !document.querySelector('#alert').hidden);
    assert.equal(await page.textContent('#alert'), 'Email atau password salah.');
    return { evidence: await shot('node-login-kredensial-salah') };
  });

  await rec.step('N-12', 'Login email/password benar', 'Masuk ke dashboard', async () => {
    await page.fill('#password', password);
    await Promise.all([page.waitForURL('**/dashboard'), page.click('#submit-btn')]);
    assert.equal(await page.textContent('#user-email'), email);
    return { evidence: await shot('node-dashboard-login-email') };
  });

  await rec.step('N-13', 'Session cookie berflag HttpOnly & SameSite', 'Cookie __session HttpOnly, SameSite=Lax; tidak terbaca oleh JavaScript', async () => {
    const c = (await ctx.cookies()).find((x) => x.name === '__session');
    assert.ok(c, 'cookie tidak ada');
    assert.equal(c.httpOnly, true);
    assert.equal(c.sameSite, 'Lax');
    assert.ok(!(await page.evaluate(() => document.cookie)).includes('__session'));
    return { actual: `httpOnly=${c.httpOnly}, sameSite=${c.sameSite}, secure=${c.secure} (Secure aktif hanya di NODE_ENV=production/HTTPS)` };
  });

  await rec.step('N-14', 'Sesi hilang/kedaluwarsa saat memakai Gemini', 'API 401 -> diarahkan ke /login?expired=1 dengan pesan sesi berakhir', async () => {
    await ctx.clearCookies({ name: '__session' });
    await page.fill('#prompt', 'halo');
    await Promise.all([page.waitForURL('**/login?expired=1'), page.click('#ask-btn')]);
    assert.match(await page.textContent('#alert'), /Sesi Anda sudah berakhir/);
    return { evidence: await shot('node-sesi-berakhir') };
  });

  await rec.step('N-15', 'Register email yang sudah dipakai', 'Pesan "Email ini sudah terdaftar. Silakan masuk."', async () => {
    await page.goto(`${BASE}/register`);
    await fillRegister({ name: 'Penguji Node', email, password, confirm: password });
    await page.click('#submit-btn');
    await page.waitForFunction(() => !document.querySelector('#alert').hidden);
    assert.equal(await page.textContent('#alert'), 'Email ini sudah terdaftar. Silakan masuk.');
    return { evidence: await shot('node-register-email-terpakai') };
  });

  await rec.step('N-16', 'Akses /dashboard tanpa login (konteks bersih)', '302 ke /login', async () => {
    const clean = await browser.newContext({ locale: 'id-ID' });
    const r = await clean.request.get(`${BASE}/dashboard`, { maxRedirects: 0 });
    assert.equal(r.status(), 302);
    assert.match(r.headers().location, /\/login/);
    const api = await clean.request.post(`${BASE}/api/gemini`, { data: { prompt: 'halo' } });
    assert.equal(api.status(), 401);
    await clean.close();
    return { actual: '/dashboard -> 302 /login; POST /api/gemini -> 401' };
  });

  // --- Google (EMULATOR): kredensial IdP tiruan, BUKAN popup Google asli ---
  await rec.step('N-17', 'Login Google via kredensial IdP tiruan emulator (BUKAN Google nyata)', 'Dashboard menampilkan metode login "Google"', async () => {
    const g = await browser.newContext({ viewport: { width: 1000, height: 760 }, locale: 'id-ID', bypassCSP: true });
    const gp = await g.newPage();
    await gp.goto(`${BASE}/login`);
    await gp.waitForSelector('#login-form');
    await gp.addScriptTag({ path: path.join(__dirname, '.build', 'google-fake.bundle.js') });
    await gp.waitForURL('**/dashboard', { timeout: 15000 });
    assert.equal(await gp.textContent('#user-provider'), 'Google');
    const f = rec.nextName('node-dashboard-google-emulator');
    await gp.screenshot({ path: path.join(SHOTS, f) });
    await g.close();
    return { actual: 'Provider "Google" tampil (jalur emulator, bukan OAuth Google asli)', evidence: f };
  });

  await rec.step('N-18', 'Klik tombol "Masuk dengan Google" (popup) di sandbox', 'Popup Google asli', async () => {
    throw new Error('BELUM DIUJI: sandbox memblokir apis.google.com, popup tidak dapat dibuka. Perlu uji manual di Firebase nyata.');
  });

  rec.save();
  await browser.close();
})();
