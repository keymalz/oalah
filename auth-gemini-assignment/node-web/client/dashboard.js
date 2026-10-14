import { $, showAlert, setBusy, csrfToken, postJson } from './ui.js';

const form = $('ask-form');
const prompt = $('prompt');
const btn = $('ask-btn');
const answer = $('answer');
const meta = $('answer-meta');
btn.dataset.main = '1';
let busy = false;

prompt.addEventListener('input', () => ($('count').textContent = String(prompt.value.length)));

function sessionExpired() {
  window.location.assign('/login?expired=1');
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  if (busy) return;
  showAlert('');
  const text = prompt.value.trim();
  if (!text) {
    showAlert('Pertanyaan tidak boleh kosong.');
    return prompt.focus();
  }
  busy = true;
  setBusy([btn], true, 'Menunggu Gemini…');
  answer.classList.add('loading');
  answer.textContent = 'Gemini sedang menjawab…';
  meta.textContent = '';
  try {
    const r = await postJson('/api/gemini', { prompt: text });
    if (r.status === 401) return sessionExpired();
    if (!r.ok) {
      answer.textContent = 'Tidak ada jawaban.';
      showAlert(r.data?.error || 'Gagal menghubungi Gemini.');
    } else {
      answer.textContent = r.data.answer;
      meta.textContent = r.data.mock ? 'MOCK — bukan jawaban Gemini asli (mode pengujian).' : `Model: ${r.data.model}`;
    }
  } catch {
    answer.textContent = 'Tidak ada jawaban.';
    showAlert('Koneksi ke server bermasalah. Coba lagi.');
  } finally {
    answer.classList.remove('loading');
    busy = false;
    setBusy([btn], false);
  }
});

$('logout-btn').addEventListener('click', async (ev) => {
  ev.currentTarget.disabled = true;
  await fetch('/api/sessionLogout', {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'X-CSRF-Token': csrfToken() },
  });
  window.location.assign('/login');
});
