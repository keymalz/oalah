// SHIM UJI: mengganti gstatic firebase-app.js/firebase-auth.js. Menyambungkan Auth Emulator tepat
// saat instance Auth dibuat (sebelum pemulihan sesi tersimpan), agar uji refresh dapat berjalan.
import * as authMod from 'firebase/auth';
export * from 'firebase/app';
export * from 'firebase/auth';

const EMU = 'http://127.0.0.1:9099';
const hook = (auth) => {
  try { if (!auth.emulatorConfig) authMod.connectAuthEmulator(auth, EMU, { disableWarnings: true }); } catch {}
  return auth;
};
export const getAuth = (...a) => hook(authMod.getAuth(...a));
export const initializeAuth = (...a) => hook(authMod.initializeAuth(...a));
export const connectAuthEmulator = (auth, url, opts) => { if (auth.emulatorConfig) return; return authMod.connectAuthEmulator(auth, url, opts); };
