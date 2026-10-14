import { auth } from './firebase.js';
import { signOut } from 'firebase/auth';
import { postJson } from './ui.js';

// Menukar user Firebase yang baru login menjadi session cookie HttpOnly di server.
export async function establishSession(user) {
  const idToken = await user.getIdToken(true);
  const r = await postJson('/api/sessionLogin', { idToken });
  await signOut(auth); // cookie server sudah cukup
  if (!r.ok) throw Object.assign(new Error(r.data?.error || 'Gagal membuat sesi.'), { custom: true });
  window.location.assign('/dashboard');
}
