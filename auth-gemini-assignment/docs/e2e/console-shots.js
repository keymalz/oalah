// Merender output perintah NYATA (docs/test-results/*.txt) menjadi gambar, dan memotret Auth Emulator UI.
const fs = require('node:fs');
const path = require('node:path');
const { launch, recorder, SHOTS, RESULTS } = require('./lib');

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const read = (f) => fs.readFileSync(path.join(RESULTS, f), 'utf8');

function backend() {
  const keep = read('node-backend-test.txt').split('\n').filter((l) => /^(ok|not ok) |^# (tests|pass|fail)|^> /.test(l));
  return ['$ cd node-web && npm run test:emulator   # (Auth Emulator aktif; Gemini di-inject palsu)', ...keep].join('\n');
}
const tail = (f, n) => read(f).trim().split('\n').slice(-n).join('\n');
const e2eTable = (f) =>
  JSON.parse(read(f)).map((r) => `[${r.status.padEnd(11)}] ${r.id}  ${r.scenario}`).join('\n');

const SHOTS_DEF = [
  ['console-npm-test-backend', backend()],
  ['console-flutter-analyze-test', `$ cd flutter-web && flutter analyze\n${tail('flutter-analyze.txt', 1)}\n\n$ flutter test\n${tail('flutter-test.txt', 7)}\n\n$ flutter build web --release\n${tail('flutter-build.txt', 1)}`],
  ['console-e2e-node', `$ node docs/e2e/e2e-node.js   # Playwright, Auth Emulator + Gemini MOCK\n${e2eTable('node-e2e.json')}`],
  ['console-e2e-flutter', `$ node docs/e2e/e2e-flutter.js   # Playwright, Auth Emulator + Gemini MOCK\n${e2eTable('flutter-e2e.json')}`],
];

(async () => {
  const rec = recorder('console');
  const browser = await launch();
  const ctx = await browser.newContext({ viewport: { width: 1100, height: 600 }, locale: 'id-ID' });
  const page = await ctx.newPage();
  for (const [slug, body] of SHOTS_DEF) {
    await page.setContent(`<body style="margin:0;background:#0f1220"><pre style="margin:0;padding:18px;color:#d6e2ff;font:14px/1.45 ui-monospace,Menlo,Consolas,monospace;white-space:pre-wrap">${esc(body)}</pre></body>`);
    const h = await page.evaluate(() => document.body.scrollHeight);
    await page.setViewportSize({ width: 1100, height: Math.min(h + 4, 1400) });
    await page.screenshot({ path: path.join(SHOTS, rec.nextName(slug)) });
  }
  // Auth Emulator UI (BUKAN Firebase Console)
  await page.setViewportSize({ width: 1200, height: 640 });
  await page.goto('http://127.0.0.1:4000/auth');
  await page.waitForSelector('text=Add user', { timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(SHOTS, rec.nextName('emulator-ui-daftar-pengguna')) });
  await browser.close();
})();
