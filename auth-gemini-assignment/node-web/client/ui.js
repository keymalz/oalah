const ERRORS = {
  'auth/invalid-email': 'Format email tidak valid.',
  'auth/missing-email': 'Email wajib diisi.',
  'auth/user-not-found': 'Email atau password salah.',
  'auth/wrong-password': 'Email atau password salah.',
  'auth/invalid-credential': 'Email atau password salah.',
  'auth/email-already-in-use': 'Email ini sudah terdaftar. Silakan masuk.',
  'auth/weak-password': 'Password terlalu lemah. Gunakan minimal 8 karakter.',
  'auth/too-many-requests': 'Terlalu banyak percobaan. Tunggu beberapa saat lalu coba lagi.',
  'auth/network-request-failed': 'Koneksi bermasalah. Periksa internet Anda.',
  'auth/user-disabled': 'Akun ini dinonaktifkan.',
  'auth/popup-closed-by-user': 'Login Google dibatalkan karena jendela ditutup.',
  'auth/cancelled-popup-request': 'Login Google dibatalkan.',
  'auth/popup-blocked': 'Popup diblokir browser. Izinkan popup lalu coba lagi.',
  'auth/account-exists-with-different-credential': 'Email ini sudah terdaftar dengan metode login lain.',
  'auth/operation-not-allowed': 'Metode login ini belum diaktifkan di Firebase Console.',
  'auth/unauthorized-domain': 'Domain ini belum ada di Authorized domains Firebase.',
};

export const isCancelled = (e) =>
  e?.code === 'auth/popup-closed-by-user' || e?.code === 'auth/cancelled-popup-request';

export function friendlyError(e) {
  return ERRORS[e?.code] || 'Terjadi kesalahan. Silakan coba lagi.';
}

export const $ = (id) => document.getElementById(id);

export function showAlert(msg, kind = 'error') {
  const el = $('alert');
  if (!el) return;
  el.textContent = msg;
  el.className = `alert ${kind === 'ok' ? 'alert-ok' : 'alert-error'}`;
  el.hidden = !msg;
}

export function setFieldError(name, msg) {
  const input = $(name);
  const err = $(`${name}-error`);
  if (!input || !err) return;
  err.textContent = msg || '';
  err.hidden = !msg;
  if (msg) {
    input.setAttribute('aria-invalid', 'true');
    input.setAttribute('aria-describedby', `${name}-error`);
  } else {
    input.removeAttribute('aria-invalid');
    input.removeAttribute('aria-describedby');
  }
}

export function setBusy(buttons, busy, busyText) {
  for (const b of buttons) {
    if (!b) continue;
    if (busy) {
      b.dataset.label = b.dataset.label || b.textContent;
      b.disabled = true;
      if (busyText && b.dataset.main === '1') b.textContent = busyText;
    } else {
      b.disabled = false;
      if (b.dataset.label) b.textContent = b.dataset.label;
    }
  }
}

export function csrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content || '';
}

export async function postJson(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken() },
    body: JSON.stringify(body || {}),
  });
  let data = {};
  try {
    data = await res.json();
  } catch {
    /* body kosong */
  }
  return { ok: res.ok, status: res.status, data };
}

export function wirePasswordToggles() {
  document.querySelectorAll('.pw-toggle').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = $(btn.dataset.target);
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.textContent = show ? 'Sembunyikan' : 'Tampilkan';
      btn.setAttribute('aria-pressed', String(show));
    });
  });
}

export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
