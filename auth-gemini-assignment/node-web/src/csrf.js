const crypto = require('node:crypto');
const config = require('./config');

const COOKIE = '__csrf';

// Pola "synchronizer token" sederhana: token acak disimpan di cookie HttpOnly dan
// disisipkan ke halaman HTML (meta tag). Klien mengirim ulang token lewat header
// X-CSRF-Token; situs lain tidak bisa membaca halaman kita sehingga tidak bisa memalsukannya.
function issue(req, res, next) {
  let token = req.cookies?.[COOKIE];
  if (!token || !/^[a-f0-9]{64}$/.test(token)) {
    token = crypto.randomBytes(32).toString('hex');
    res.cookie(COOKIE, token, {
      httpOnly: true,
      sameSite: 'strict',
      secure: config.isProd,
      path: '/',
    });
  }
  res.locals.csrfToken = token;
  next();
}

function safeEqual(a, b) {
  const ba = Buffer.from(String(a));
  const bb = Buffer.from(String(b));
  return ba.length === bb.length && crypto.timingSafeEqual(ba, bb);
}

function originHost(origin) {
  try {
    return new URL(origin).host;
  } catch {
    return '';
  }
}

function verify(req, res, next) {
  const cookieToken = req.cookies?.[COOKIE];
  const headerToken = req.get('x-csrf-token');
  if (!cookieToken || !headerToken || !safeEqual(cookieToken, headerToken)) {
    return res.status(403).json({ code: 'CSRF_INVALID', error: 'Token keamanan tidak valid. Muat ulang halaman lalu coba lagi.' });
  }
  // Lapisan kedua: bila browser mengirim Origin, harus sama dengan origin aplikasi.
  const origin = req.get('origin');
  if (origin && origin !== config.appOrigin && originHost(origin) !== req.get('host')) {
    return res.status(403).json({ code: 'ORIGIN_INVALID', error: 'Origin permintaan tidak diizinkan.' });
  }
  next();
}

module.exports = { issue, verify, COOKIE };
