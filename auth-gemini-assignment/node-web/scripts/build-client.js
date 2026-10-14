const path = require('node:path');
const esbuild = require('esbuild');

const root = path.join(__dirname, '..');
esbuild
  .build({
    entryPoints: ['login', 'register', 'dashboard'].map((n) => path.join(root, 'client', `${n}.js`)),
    outdir: path.join(root, 'public', 'js'),
    entryNames: '[name].bundle',
    bundle: true,
    minify: true,
    format: 'iife',
    target: 'es2020',
    logLevel: 'info',
  })
  .catch(() => process.exit(1));
