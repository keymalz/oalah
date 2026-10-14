import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator, setPersistence, inMemoryPersistence } from 'firebase/auth';

const cfg = window.__APP_CONFIG__ || {};
const app = initializeApp(cfg.firebase);
export const auth = getAuth(app);
// Sesi sebenarnya dipegang server lewat cookie HttpOnly; SDK klien tidak perlu menyimpan apa pun.
setPersistence(auth, inMemoryPersistence);
if (cfg.emulatorUrl) connectAuthEmulator(auth, cfg.emulatorUrl, { disableWarnings: true });
