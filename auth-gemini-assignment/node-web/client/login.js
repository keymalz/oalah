import { auth } from './firebase.js';
import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { $, showAlert, setFieldError, setBusy, friendlyError, isCancelled, wirePasswordToggles, EMAIL_RE } from './ui.js';
import { establishSession } from './session.js';

wirePasswordToggles();
const form = $('login-form');
const submit = $('submit-btn');
const google = $('google-btn');
submit.dataset.main = '1';
let busy = false;

function messageFor(e) {
  return e?.custom ? e.message : friendlyError(e);
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  if (busy) return;
  showAlert('');
  const email = $('email').value.trim();
  const password = $('password').value;
  let ok = true;
  setFieldError('email', !email ? 'Email wajib diisi.' : !EMAIL_RE.test(email) ? 'Format email tidak valid.' : '');
  setFieldError('password', password ? '' : 'Password wajib diisi.');
  ok = !(document.querySelector('[aria-invalid="true"]'));
  if (!ok) return document.querySelector('[aria-invalid="true"]').focus();

  busy = true;
  setBusy([submit, google], true, 'Memproses…');
  try {
    const cred = await signInWithEmailAndPassword(auth, email, password);
    await establishSession(cred.user);
  } catch (e) {
    showAlert(messageFor(e));
    busy = false;
    setBusy([submit, google], false);
  }
});

google.addEventListener('click', async () => {
  if (busy) return;
  showAlert('');
  busy = true;
  setBusy([submit, google], true);
  try {
    const cred = await signInWithPopup(auth, new GoogleAuthProvider());
    await establishSession(cred.user);
  } catch (e) {
    showAlert(isCancelled(e) ? 'Login Google dibatalkan. Anda bisa mencoba lagi.' : messageFor(e), isCancelled(e) ? 'error' : 'error');
    busy = false;
    setBusy([submit, google], false);
  }
});
