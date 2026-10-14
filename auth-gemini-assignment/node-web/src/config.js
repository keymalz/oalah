const path = require('node:path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env'), quiet: true });

const list = (v) => (v || '').split(',').map((s) => s.trim()).filter(Boolean);
const int = (v, d) => (Number.isFinite(parseInt(v, 10)) ? parseInt(v, 10) : d);

const env = process.env;
const emulatorHost = env.FIREBASE_AUTH_EMULATOR_HOST || '';

module.exports = {
  port: int(env.PORT, 3000),
  isProd: env.NODE_ENV === 'production',
  appOrigin: env.APP_ORIGIN || `http://localhost:${int(env.PORT, 3000)}`,
  allowedOrigins: list(env.ALLOWED_ORIGINS),
  sessionMaxMs: int(env.SESSION_MAX_DAYS, 5) * 24 * 60 * 60 * 1000,
  firebase: {
    projectId: env.FIREBASE_PROJECT_ID || 'demo-auth-gemini',
    // Konfigurasi web Firebase bersifat publik (bukan rahasia), aman dikirim ke browser.
    web: {
      apiKey: env.FIREBASE_API_KEY || 'demo-api-key',
      authDomain: env.FIREBASE_AUTH_DOMAIN || '',
      projectId: env.FIREBASE_PROJECT_ID || 'demo-auth-gemini',
      appId: env.FIREBASE_APP_ID || '',
    },
    emulatorHost,
    // URL emulator yang dilihat BROWSER (bukan server).
    emulatorUrl: env.FIREBASE_AUTH_EMULATOR_URL || (emulatorHost ? `http://${emulatorHost}` : ''),
  },
  gemini: {
    apiKey: env.GEMINI_API_KEY || '',
    model: env.GEMINI_MODEL || 'gemini-3.5-flash',
    timeoutMs: int(env.GEMINI_TIMEOUT_MS, 20000),
    maxInputChars: int(env.GEMINI_MAX_INPUT_CHARS, 2000),
    mock: env.GEMINI_MOCK === '1',
  },
};
