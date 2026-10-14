// Hanya untuk pengujian (tidak dikirim ke pengguna): login dengan kredensial Google TIRUAN milik Auth Emulator.
import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator, signInWithCredential, GoogleAuthProvider, signOut } from 'firebase/auth';
(async () => {
const cfg = window.__APP_CONFIG__;
const auth = getAuth(initializeApp(cfg.firebase, 'fake-google'));
connectAuthEmulator(auth, cfg.emulatorUrl, { disableWarnings: true });
const fake = JSON.stringify({ sub: 'google-sub-' + Date.now(), email: `uji.google.${Date.now()}@example.com`, email_verified: true, name: 'Penguji Google', display_name: 'Penguji Google' });
const cred = await signInWithCredential(auth, GoogleAuthProvider.credential(fake));
const idToken = await cred.user.getIdToken(true);
const csrf = document.querySelector('meta[name="csrf-token"]').content;
const r = await fetch('/api/sessionLogin', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body: JSON.stringify({ idToken }) });
await signOut(auth);
if (r.ok) location.assign('/dashboard');
})();
