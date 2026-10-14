import { auth } from './firebase.js';
import { createUserWithEmailAndPassword, updateProfile, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { $, showAlert, setFieldError, setBusy, friendlyError, isCancelled, wirePasswordToggles, EMAIL_RE } from './ui.js';
import { establishSession } from './session.js';

wirePasswordToggles();
const form = $('register-form');
const submit = $('submit-btn');
const google = $('google-btn');
submit.dataset.main = '1';
let busy = false;

const messageFor = (e) => (e?.custom ? e.message : friendlyError(e));

function validate() {
  const name = $('name').value.trim();
  const email = $('email').value.trim();
  const pw = $('password').value;
  const confirm = $('confirm').value;
  setFieldError('name', name.length < 2 ? 'Nama minimal 2 karakter.' : name.length > 60 ? 'Nama maksimal 60 karakter.' : '');
  setFieldError('email', !email ? 'Email wajib diisi.' : !EMAIL_RE.test(email) ? 'Format email tidak valid.' : '');
  setFieldError(
    'password',
    pw.length < 8 ? 'Password minimal 8 karakter.' : !/[A-Za-z]/.test(pw) || !/\d/.test(pw) ? 'Password harus mengandung huruf dan angka.' : '',
  );
  setFieldError('confirm', !confirm ? 'Konfirmasi password wajib diisi.' : confirm !== pw ? 'Konfirmasi password tidak cocok.' : '');
  const firstInvalid = document.querySelector('[aria-invalid="true"]');
  if (firstInvalid) firstInvalid.focus();
  return { ok: !firstInvalid, name, email, pw };
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  if (busy) return;
  showAlert('');
  const v = validate();
  if (!v.ok) return;
  busy = true;
  setBusy([submit, google], true, 'Mendaftarkan…');
  try {
    const cred = await createUserWithEmailAndPassword(auth, v.email, v.pw);
    await updateProfile(cred.user, { displayName: v.name });
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
    showAlert(isCancelled(e) ? 'Login Google dibatalkan. Anda bisa mencoba lagi.' : messageFor(e));
    busy = false;
    setBusy([submit, google], false);
  }
});
