const config = require('./config');

const SESSION_COOKIE = '__session';

function cookieOptions(maxAge) {
  return { maxAge, httpOnly: true, secure: config.isProd, sameSite: 'lax', path: '/' };
}

function clearSession(res) {
  res.clearCookie(SESSION_COOKIE, { httpOnly: true, secure: config.isProd, sameSite: 'lax', path: '/' });
}

// Mengembalikan { user, via } atau melempar error { code } bila tidak sah.
// Prioritas: header Authorization Bearer (Flutter) lalu session cookie (Node web).
async function resolveUser(auth, req) {
  const header = req.get('authorization') || '';
  if (header.toLowerCase().startsWith('bearer ')) {
    const token = header.slice(7).trim();
    try {
      const decoded = await auth.verifyIdToken(token, true);
      return { user: decoded, via: 'bearer' };
    } catch (e) {
      const code = e?.code === 'auth/id-token-expired' ? 'SESSION_EXPIRED' : 'TOKEN_INVALID';
      throw Object.assign(new Error(code), { code });
    }
  }
  const cookie = req.cookies?.[SESSION_COOKIE];
  if (!cookie) throw Object.assign(new Error('NO_AUTH'), { code: 'NO_AUTH' });
  try {
    const decoded = await auth.verifySessionCookie(cookie, true);
    return { user: decoded, via: 'cookie' };
  } catch (e) {
    const expired = e?.code === 'auth/session-cookie-expired';
    throw Object.assign(new Error('SESSION'), { code: expired ? 'SESSION_EXPIRED' : 'TOKEN_INVALID' });
  }
}

function describeUser(decoded) {
  return {
    uid: decoded.uid,
    name: decoded.name || '',
    email: decoded.email || '',
    emailVerified: !!decoded.email_verified,
    provider: decoded.firebase?.sign_in_provider || 'tidak diketahui',
  };
}

const PROVIDER_LABEL = {
  password: 'Email dan password',
  'google.com': 'Google',
  custom: 'Custom token',
};

module.exports = { SESSION_COOKIE, cookieOptions, clearSession, resolveUser, describeUser, PROVIDER_LABEL };
