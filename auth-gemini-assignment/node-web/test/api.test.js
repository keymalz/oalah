// Tes integrasi: memakai Firebase Auth Emulator (autentikasi sungguhan di sisi Admin SDK)
// dan Gemini palsu (di-inject). Jalankan: npm run test:emulator
process.env.FIREBASE_AUTH_EMULATOR_HOST ||= '127.0.0.1:9099';
process.env.ALLOWED_ORIGINS = 'http://localhost:8080';
process.env.GEMINI_API_KEY = 'SECRET-KEY-JANGAN-BOCOR';

const test = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');
const { createApp } = require('../src/app');
const { mapError, GeminiError } = require('../src/gemini');

const EMU = `http://${process.env.FIREBASE_AUTH_EMULATOR_HOST}`;
const email = `uji-${Date.now()}@example.com`;
const password = 'Rahasia123';

async function signUp() {
  const r = await fetch(`${EMU}/identitytoolkit.googleapis.com/v1/accounts:signUp?key=fake`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, displayName: 'Penguji', returnSecureToken: true }),
  });
  return (await r.json()).idToken;
}

let calls = 0;
let nextAsk = async (p) => ({ text: `jawaban untuk: ${p}`, model: 'fake', mock: false });
const app = createApp({ ask: (p) => { calls++; return nextAsk(p); } });
let idToken;

async function csrfAgent() {
  const agent = request.agent(app);
  const page = await agent.get('/login').expect(200);
  const token = /name="csrf-token" content="([a-f0-9]{64})"/.exec(page.text)[1];
  return { agent, token };
}

test.before(async () => { idToken = await signUp(); });

test('dashboard tanpa login diarahkan ke /login', async () => {
  const r = await request(app).get('/dashboard');
  assert.equal(r.status, 302);
  assert.equal(r.headers.location, '/login');
});

test('POST /api/gemini tanpa autentikasi ditolak 401 dan Gemini tidak dipanggil', async () => {
  const before = calls;
  const r = await request(app).post('/api/gemini').send({ prompt: 'halo' });
  assert.equal(r.status, 401);
  assert.equal(r.body.code, 'NO_AUTH');
  assert.equal(calls, before);
});

test('bearer token palsu ditolak 401', async () => {
  const r = await request(app).post('/api/gemini').set('Authorization', 'Bearer abc.def.ghi').send({ prompt: 'halo' });
  assert.equal(r.status, 401);
  assert.equal(r.body.code, 'TOKEN_INVALID');
});

test('session cookie palsu ditolak 401 dan cookie dihapus', async () => {
  const r = await request(app).get('/api/me').set('Cookie', '__session=palsu');
  assert.equal(r.status, 401);
  assert.match(r.headers['set-cookie'].join(';'), /__session=;/);
});

test('sessionLogin tanpa CSRF ditolak 403', async () => {
  const r = await request(app).post('/api/sessionLogin').send({ idToken });
  assert.equal(r.status, 403);
  assert.equal(r.body.code, 'CSRF_INVALID');
});

test('sessionLogin dengan ID token palsu ditolak 401', async () => {
  const { agent, token } = await csrfAgent();
  const r = await agent.post('/api/sessionLogin').set('X-CSRF-Token', token).send({ idToken: 'palsu' });
  assert.equal(r.status, 401);
});

test('alur sesi: login -> dashboard -> gemini -> logout', async () => {
  const { agent, token } = await csrfAgent();
  const login = await agent.post('/api/sessionLogin').set('X-CSRF-Token', token).send({ idToken });
  assert.equal(login.status, 200);
  const sc = login.headers['set-cookie'].find((c) => c.startsWith('__session='));
  assert.match(sc, /HttpOnly/i);
  assert.match(sc, /SameSite=Lax/i);

  const dash = await agent.get('/dashboard');
  assert.equal(dash.status, 200);
  assert.match(dash.text, new RegExp(email.replace('.', '\\.')));
  assert.match(dash.text, /Email dan password/);

  // Cookie tanpa CSRF -> ditolak
  assert.equal((await agent.post('/api/gemini').send({ prompt: 'halo' })).status, 403);

  // Input tidak valid
  const h = { 'X-CSRF-Token': token };
  assert.equal((await agent.post('/api/gemini').set(h).send({ prompt: '   ' })).body.code, 'EMPTY_PROMPT');
  assert.equal((await agent.post('/api/gemini').set(h).send({})).body.code, 'EMPTY_PROMPT');
  assert.equal((await agent.post('/api/gemini').set(h).send({ prompt: 'x'.repeat(2001) })).body.code, 'PROMPT_TOO_LONG');

  const ok = await agent.post('/api/gemini').set(h).send({ prompt: 'Apa itu JWT?' });
  assert.equal(ok.status, 200);
  assert.equal(ok.body.answer, 'jawaban untuk: Apa itu JWT?');

  const out = await agent.post('/api/sessionLogout').set(h);
  assert.equal(out.status, 200);
  assert.match(out.headers['set-cookie'].join(';'), /__session=;/);
  const after = await agent.get('/dashboard');
  assert.equal(after.status, 302);
});

test('bearer token valid (gaya Flutter) diterima', async () => {
  const r = await request(app).post('/api/gemini').set('Authorization', `Bearer ${idToken}`).send({ prompt: 'halo' });
  assert.equal(r.status, 200);
  const me = await request(app).get('/api/me').set('Authorization', `Bearer ${idToken}`);
  assert.equal(me.body.user.email, email);
  assert.equal(me.body.user.provider, 'password');
});

test('error Gemini dipetakan dan tidak membocorkan rahasia', async () => {
  const cases = [
    [Object.assign(new Error('API key not valid SECRET-KEY-JANGAN-BOCOR'), { status: 400 }), 503, 'GEMINI_BAD_KEY'],
    [Object.assign(new Error('RESOURCE_EXHAUSTED quota'), { status: 429 }), 429, 'GEMINI_QUOTA'],
    [Object.assign(new Error('The operation was aborted'), { name: 'AbortError' }), 504, 'GEMINI_TIMEOUT'],
    [new Error('boom SECRET-KEY-JANGAN-BOCOR'), 502, 'GEMINI_FAILED'],
  ];
  for (const [err, status, code] of cases) {
    nextAsk = async () => { throw err; };
    const r = await request(app).post('/api/gemini').set('Authorization', `Bearer ${idToken}`).send({ prompt: 'halo' });
    assert.equal(r.status, status, code);
    assert.equal(r.body.code, code);
    assert.ok(!JSON.stringify(r.body).includes('SECRET-KEY'), 'rahasia bocor!');
  }
  assert.equal(mapError(new GeminiError('X', 'm', 500)).code, 'X');
});

test('CORS hanya untuk origin yang diizinkan', async () => {
  const ok = await request(app).options('/api/gemini').set('Origin', 'http://localhost:8080').set('Access-Control-Request-Method', 'POST');
  assert.equal(ok.status, 204);
  assert.equal(ok.headers['access-control-allow-origin'], 'http://localhost:8080');
  const bad = await request(app).options('/api/gemini').set('Origin', 'https://jahat.example');
  assert.equal(bad.headers['access-control-allow-origin'], undefined);
});
