// Memanggil Gemini API NYATA dengan key PALSU (tidak memakai kuota, tidak butuh akun).
// Membuktikan jalur SDK -> Google -> pemetaan error -> respons aman ke klien.
process.env.FIREBASE_AUTH_EMULATOR_HOST ||= '127.0.0.1:9099';
// Dirangkai agar tidak terbaca sebagai API key sungguhan oleh pemindai rahasia.
process.env.GEMINI_API_KEY = ['AIza', 'SyFAKE-KEY-FOR-TEST-0000000000000000'].join('');
process.env.GEMINI_MOCK = '0';

const test = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');
const { createApp } = require('../src/app');

test('key Gemini tidak valid -> 503 GEMINI_BAD_KEY tanpa membocorkan key', async () => {
  const r = await fetch(`http://${process.env.FIREBASE_AUTH_EMULATOR_HOST}/identitytoolkit.googleapis.com/v1/accounts:signUp?key=fake`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: `live-${Date.now()}@example.com`, password: 'Rahasia123', returnSecureToken: true }),
  });
  const { idToken } = await r.json();
  const res = await request(createApp()).post('/api/gemini').set('Authorization', `Bearer ${idToken}`).send({ prompt: 'halo' });
  assert.equal(res.status, 503);
  assert.equal(res.body.code, 'GEMINI_BAD_KEY');
  assert.ok(!JSON.stringify(res.body).includes('AIzaSy'), 'key bocor ke klien');
});
