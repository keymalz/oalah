const { initializeApp, getApps, applicationDefault } = require('firebase-admin/app');
const { getAuth: adminGetAuth } = require('firebase-admin/auth');
const config = require('./config');

// Admin SDK memakai Application Default Credentials (GOOGLE_APPLICATION_CREDENTIALS).
// Jika FIREBASE_AUTH_EMULATOR_HOST terisi, SDK otomatis berbicara ke emulator
// dan tidak membutuhkan service account.
function getAuth() {
  if (!getApps().length) {
    const opts = { projectId: config.firebase.projectId };
    if (!config.firebase.emulatorHost) opts.credential = applicationDefault();
    initializeApp(opts);
  }
  return adminGetAuth();
}

module.exports = { getAuth };
