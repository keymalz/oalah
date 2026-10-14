const config = require('./src/config');
const { createApp } = require('./src/app');

createApp().listen(config.port, () => {
  console.log(`Server berjalan di http://localhost:${config.port}`);
  if (config.firebase.emulatorHost) console.log(`[!] Mode EMULATOR Firebase Auth: ${config.firebase.emulatorHost}`);
  if (config.gemini.mock) console.log('[!] GEMINI_MOCK=1 aktif: jawaban Gemini adalah MOCK.');
  if (!config.gemini.apiKey && !config.gemini.mock) console.log('[!] GEMINI_API_KEY belum diisi.');
});
