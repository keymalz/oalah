#!/usr/bin/env python3
"""Membangkitkan docs/CATATAN-PENGUJIAN.md dari docs/test-results/*."""
import json, os, re
R = os.path.join(os.path.dirname(__file__), 'test-results')
out = ['# Catatan Pengujian', '',
       'Dibangkitkan otomatis dari `docs/test-results/` (jalankan `python3 docs/build_notes.py`).',
       '',
       '**Lingkungan uji:** Firebase Auth Emulator (`demo-auth-gemini`) + Gemini **MOCK** (kecuali tes key palsu ke Gemini API nyata). '
       'Hasil di emulator **tidak membuktikan** Google Sign-In, Firebase Console, atau jawaban Gemini nyata.', '']
bt = open(os.path.join(R, 'node-backend-test.txt'), encoding='utf-8').read()
out += ['## Backend Node.js (`npm test`)', '', '| # | Skenario | Status |', '|---|---|---|']
for i, (s, n) in enumerate(re.findall(r'^(ok|not ok) \d+ - (.*)$', bt, re.M), 1):
    out.append(f'| B-{i:02d} | {n} | {"Lulus" if s == "ok" else "Gagal"} |')
for title, f in (('E2E Node.js (Playwright)', 'node-e2e.json'), ('E2E Flutter Web (Playwright)', 'flutter-e2e.json')):
    out += ['', f'## {title}', '', '| ID | Skenario | Diharapkan | Aktual | Status | Bukti |', '|---|---|---|---|---|---|']
    for r in json.load(open(os.path.join(R, f), encoding='utf-8')):
        out.append('| {id} | {scenario} | {expected} | {actual} | {status} | {evidence} |'.format(**{k: str(v).replace('|', '/') for k, v in r.items()}))
ft = open(os.path.join(R, 'flutter-test.txt'), encoding='utf-8').read()
out += ['', '## Flutter', '', '```', open(os.path.join(R, 'flutter-analyze.txt'), encoding='utf-8').read().strip().split('\n')[-1],
        ft.strip().split('\n')[-1], '```', '',
        '## Belum diuji (butuh akun/konfigurasi nyata)', '',
        '- Provider Email/Password & Google aktif di Firebase Console; daftar pengguna di Console',
        '- Pembuatan API key AI Studio; jawaban Gemini nyata (Node.js dan Flutter Web)',
        '- Login Google nyata (popup OAuth) dan pembatalan popup nyata di kedua website',
        '- Sesi kedaluwarsa karena waktu; timeout/kuota Gemini nyata; flag Secure pada HTTPS production', '']
open(os.path.join(os.path.dirname(__file__), 'CATATAN-PENGUJIAN.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
