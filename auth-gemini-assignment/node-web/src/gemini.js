const { GoogleGenAI } = require('@google/genai');
const config = require('./config');

class GeminiError extends Error {
  constructor(code, message, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

const SYSTEM_INSTRUCTION =
  'Kamu asisten singkat untuk praktikum. Jawab dalam Bahasa Indonesia, ringkas (maksimal sekitar 150 kata).';

let client;
function getClient() {
  if (!client) client = new GoogleGenAI({ apiKey: config.gemini.apiKey });
  return client;
}

// Memetakan error SDK ke kode aman. Pesan asli tidak diteruskan ke klien
// karena dapat memuat potongan konfigurasi atau detail internal.
function mapError(err) {
  if (err instanceof GeminiError) return err;
  const status = err?.status ?? err?.code;
  const text = String(err?.message || '').toLowerCase();
  if (err?.name === 'AbortError' || text.includes('timeout') || text.includes('aborted')) {
    return new GeminiError('GEMINI_TIMEOUT', 'Gemini tidak merespons tepat waktu. Coba lagi.', 504);
  }
  if (status === 429 || text.includes('quota') || text.includes('resource_exhausted')) {
    return new GeminiError('GEMINI_QUOTA', 'Kuota Gemini API habis atau terlalu banyak permintaan. Coba lagi nanti.', 429);
  }
  if (status === 400 && text.includes('api key')) {
    return new GeminiError('GEMINI_BAD_KEY', 'API key Gemini di server tidak valid. Hubungi administrator.', 503);
  }
  if (status === 401 || status === 403) {
    return new GeminiError('GEMINI_BAD_KEY', 'API key Gemini di server ditolak. Hubungi administrator.', 503);
  }
  if (status === 404) {
    return new GeminiError('GEMINI_BAD_MODEL', 'Model Gemini yang dikonfigurasi tidak ditemukan.', 503);
  }
  return new GeminiError('GEMINI_FAILED', 'Gemini gagal memproses permintaan. Coba lagi nanti.', 502);
}

async function askGemini(prompt) {
  if (config.gemini.mock) {
    // MOCK: hanya untuk pengujian lokal. Jawaban diberi label agar tidak dikira jawaban nyata.
    return { text: `[MOCK — bukan jawaban Gemini asli] Anda bertanya: "${prompt.slice(0, 120)}"`, model: 'mock', mock: true };
  }
  if (!config.gemini.apiKey) {
    throw new GeminiError('GEMINI_NO_KEY', 'GEMINI_API_KEY belum dikonfigurasi di server.', 503);
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), config.gemini.timeoutMs);
  try {
    const res = await getClient().models.generateContent({
      model: config.gemini.model,
      contents: prompt,
      config: { systemInstruction: SYSTEM_INSTRUCTION, abortSignal: controller.signal },
    });
    const text = res.text;
    if (!text) throw new GeminiError('GEMINI_EMPTY', 'Gemini tidak memberikan jawaban (mungkin diblokir filter keamanan).', 502);
    return { text, model: config.gemini.model, mock: false };
  } catch (err) {
    throw mapError(err);
  } finally {
    clearTimeout(timer);
  }
}

module.exports = { askGemini, GeminiError, mapError };
