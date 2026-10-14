const path = require('node:path');
const express = require('express');
const helmet = require('helmet');
const cookieParser = require('cookie-parser');
const rateLimit = require('express-rate-limit');

const config = require('./config');
const csrf = require('./csrf');
const { SESSION_COOKIE, cookieOptions, clearSession, resolveUser, describeUser, PROVIDER_LABEL } = require('./auth');
const gemini = require('./gemini');

const MAX_AUTH_AGE_S = 5 * 60; // ID token harus baru (<5 menit) untuk ditukar menjadi session cookie.

function createApp({ auth, ask = gemini.askGemini } = {}) {
  if (!auth) auth = require('./firebaseAdmin').getAuth();
  const app = express();
  app.disable('x-powered-by');
  app.set('view engine', 'ejs');
  app.set('views', path.join(__dirname, '..', 'views'));

  const emulator = config.firebase.emulatorUrl;
  app.use(
    helmet({
      contentSecurityPolicy: {
        useDefaults: false,
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", 'https://apis.google.com'],
          styleSrc: ["'self'"],
          imgSrc: ["'self'", 'data:', 'https://*.googleusercontent.com'],
          connectSrc: ["'self'", 'https://*.googleapis.com', ...(emulator ? [emulator] : [])],
          frameSrc: ["'self'", 'https://*.firebaseapp.com', 'https://accounts.google.com', ...(emulator ? [emulator] : [])],
          objectSrc: ["'none'"],
          baseUri: ["'self'"],
          formAction: ["'self'"],
          frameAncestors: ["'none'"],
        },
      },
      // Diperlukan agar popup Google Sign-In dapat berkomunikasi dengan jendela induk.
      crossOriginOpenerPolicy: { policy: 'same-origin-allow-popups' },
    }),
  );
  app.use(cookieParser());
  app.use((req, res, next) => {
    res.locals.csrfToken = '';
    next();
  });
  app.use(express.json({ limit: '10kb' }));
  app.use('/static', express.static(path.join(__dirname, '..', 'public'), { maxAge: 0 }));

  // ---- CORS: hanya origin yang terdaftar (mis. Flutter Web) yang boleh memanggil /api ----
  app.use('/api', (req, res, next) => {
    const origin = req.get('origin');
    if (origin && config.allowedOrigins.includes(origin)) {
      res.set('Access-Control-Allow-Origin', origin);
      res.set('Vary', 'Origin');
      res.set('Access-Control-Allow-Headers', 'Authorization, Content-Type');
      res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.set('Access-Control-Max-Age', '600');
    }
    if (req.method === 'OPTIONS') return res.sendStatus(204);
    next();
  });

  // Konfigurasi web Firebase (publik) dikirim sebagai skrip; tidak ada rahasia di sini.
  app.get('/config.js', (req, res) => {
    res.type('application/javascript').set('Cache-Control', 'no-store');
    res.send(`window.__APP_CONFIG__ = ${JSON.stringify({ firebase: config.firebase.web, emulatorUrl: emulator })};`);
  });

  const noStore = (req, res, next) => {
    res.set('Cache-Control', 'no-store');
    next();
  };

  // ---- Halaman ----
  async function currentSession(req) {
    try {
      return await resolveUser(auth, { get: () => '', cookies: req.cookies });
    } catch (e) {
      return { error: e.code };
    }
  }

  app.get('/', async (req, res) => {
    const s = await currentSession(req);
    res.redirect(s.user ? '/dashboard' : '/login');
  });

  for (const page of ['login', 'register']) {
    app.get(`/${page}`, noStore, csrf.issue, async (req, res) => {
      const s = await currentSession(req);
      if (s.user) return res.redirect('/dashboard');
      if (s.error) clearSession(res);
      res.render(page, { title: page === 'login' ? 'Masuk' : 'Daftar', expired: req.query.expired === '1' });
    });
  }

  app.get('/dashboard', noStore, csrf.issue, async (req, res) => {
    const s = await currentSession(req);
    if (!s.user) {
      clearSession(res);
      return res.redirect(s.error === 'SESSION_EXPIRED' ? '/login?expired=1' : '/login');
    }
    const user = describeUser(s.user);
    res.render('dashboard', {
      title: 'Dashboard',
      user,
      providerLabel: PROVIDER_LABEL[user.provider] || user.provider,
      maxChars: config.gemini.maxInputChars,
    });
  });

  // ---- API ----
  app.post('/api/sessionLogin', noStore, csrf.verify, async (req, res) => {
    const idToken = typeof req.body?.idToken === 'string' ? req.body.idToken : '';
    if (!idToken) return res.status(400).json({ code: 'NO_TOKEN', error: 'ID token tidak ada.' });
    let decoded;
    try {
      decoded = await auth.verifyIdToken(idToken);
    } catch {
      return res.status(401).json({ code: 'TOKEN_INVALID', error: 'ID token tidak valid atau kedaluwarsa.' });
    }
    if (Math.floor(Date.now() / 1000) - decoded.auth_time > MAX_AUTH_AGE_S) {
      return res.status(401).json({ code: 'RECENT_LOGIN_REQUIRED', error: 'Silakan masuk ulang.' });
    }
    const cookie = await auth.createSessionCookie(idToken, { expiresIn: config.sessionMaxMs });
    res.cookie(SESSION_COOKIE, cookie, cookieOptions(config.sessionMaxMs));
    res.json({ ok: true });
  });

  app.post('/api/sessionLogout', noStore, csrf.verify, (req, res) => {
    clearSession(res);
    res.json({ ok: true });
  });

  // Autentikasi untuk endpoint API (cookie ATAU bearer).
  async function requireAuth(req, res, next) {
    try {
      req.auth = await resolveUser(auth, req);
    } catch (e) {
      if (req.cookies?.[SESSION_COOKIE]) clearSession(res);
      const expired = e.code === 'SESSION_EXPIRED';
      return res.status(401).json({
        code: e.code,
        error: expired ? 'Sesi Anda sudah berakhir. Silakan masuk lagi.' : 'Anda belum masuk atau token tidak valid.',
      });
    }
    // Permintaan berbasis cookie wajib lolos CSRF; bearer token tidak otomatis dikirim browser.
    if (req.auth.via === 'cookie' && req.method !== 'GET') return csrf.verify(req, res, next);
    next();
  }

  app.get('/api/me', noStore, requireAuth, (req, res) => {
    res.json({ user: describeUser(req.auth.user), via: req.auth.via });
  });

  const geminiLimiter = rateLimit({
    windowMs: 60 * 1000,
    limit: 10,
    keyGenerator: (req) => req.auth.user.uid,
    standardHeaders: true,
    legacyHeaders: false,
    message: { code: 'RATE_LIMITED', error: 'Terlalu banyak pertanyaan. Tunggu sebentar.' },
  });

  app.post('/api/gemini', noStore, requireAuth, geminiLimiter, async (req, res) => {
    const prompt = typeof req.body?.prompt === 'string' ? req.body.prompt.trim() : '';
    if (!prompt) return res.status(400).json({ code: 'EMPTY_PROMPT', error: 'Pertanyaan tidak boleh kosong.' });
    if (prompt.length > config.gemini.maxInputChars) {
      return res.status(400).json({ code: 'PROMPT_TOO_LONG', error: `Pertanyaan maksimal ${config.gemini.maxInputChars} karakter.` });
    }
    try {
      const result = await ask(prompt);
      res.json({ answer: result.text, model: result.model, mock: !!result.mock });
    } catch (e) {
      const err = gemini.mapError(e);
      console.error(`[gemini] ${err.code} uid=${req.auth.user.uid}`); // tanpa prompt/secret di log
      res.status(err.status || 502).json({ code: err.code, error: err.message });
    }
  });

  app.use('/api', (req, res) => res.status(404).json({ code: 'NOT_FOUND', error: 'Endpoint tidak ditemukan.' }));
  app.use((req, res) => res.status(404).render('notfound', { title: 'Tidak ditemukan' }));
  // eslint-disable-next-line no-unused-vars
  app.use((err, req, res, next) => {
    if (err.type === 'entity.parse.failed' || err.type === 'entity.too.large') {
      return res.status(400).json({ code: 'BAD_BODY', error: 'Body permintaan tidak valid.' });
    }
    console.error('[server]', err.code || err.name);
    res.status(500).json({ code: 'SERVER_ERROR', error: 'Terjadi kesalahan di server.' });
  });

  return app;
}

module.exports = { createApp };
