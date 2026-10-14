// Helper bersama untuk skenario E2E (Playwright). Jalankan dengan NODE_PATH ke modul playwright.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const ROOT = path.join(__dirname, '..', '..');
const SHOTS = path.join(ROOT, 'screenshots');
const RESULTS = path.join(ROOT, 'docs', 'test-results');
fs.mkdirSync(SHOTS, { recursive: true });
fs.mkdirSync(RESULTS, { recursive: true });

async function launch() {
  return chromium.launch({ args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist'] });
}

function recorder(suite) {
  const rows = [];
  let n = Number(process.env.SHOT_START || 1);
  return {
    rows,
    onFail: null,
    nextName: (slug) => `${String(n++).padStart(2, '0')}-${slug}.png`,
    step: async function (id, scenario, expected, fn) {
      const row = { id, scenario, expected, actual: '', status: 'Lulus', evidence: '' };
      try {
        const r = await fn();
        row.actual = r?.actual || 'Sesuai harapan';
        row.evidence = r?.evidence || '';
      } catch (e) {
        row.status = /^BELUM DIUJI/.test(e.message) ? 'Belum diuji' : 'Gagal';
        row.actual = String(e.message || e).split('\n')[0].slice(0, 300);
      }
      if (row.status === 'Gagal' && this.onFail) await this.onFail(id);
      console.log(`[${row.status}] ${id} ${scenario} -> ${row.actual}`);
      rows.push(row);
    },
    save() {
      fs.writeFileSync(path.join(RESULTS, `${suite}.json`), JSON.stringify(rows, null, 2));
    },
  };
}

module.exports = { launch, recorder, SHOTS, RESULTS, ROOT };
