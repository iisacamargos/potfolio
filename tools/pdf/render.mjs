// Renderiza print/portfolio.html em PDF (A4 retrato) com o Chromium do Playwright.
// Uso: node tools/pdf/render.mjs [saida.pdf] [--png pasta]  (--png gera prévias das páginas)
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const args = process.argv.slice(2);
const pngIdx = args.indexOf('--png');
const pngDir = pngIdx >= 0 ? args[pngIdx + 1] : null;
const out = args.find((a, i) => !a.startsWith('--') && (pngIdx < 0 || i !== pngIdx + 1)) || path.join(ROOT, 'print/Isadora-Camargo-Portfolio-2026.pdf');

// playwright local ou global (npm i -g playwright)
let chromium;
try { ({ chromium } = await import('playwright')); }
catch { const { execSync } = await import('node:child_process');
  ({ chromium } = await import(path.join(execSync('npm root -g').toString().trim(), 'playwright/index.mjs'))); }
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 2 });
await page.goto('file://' + path.join(ROOT, 'print/portfolio.html'), { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.pdf({ path: out, width: '210mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
console.log('PDF:', out);

if (pngDir) {
  fs.mkdirSync(pngDir, { recursive: true });
  const n = await page.locator('section.page').count();
  for (let i = 0; i < n; i++) {
    await page.locator('section.page').nth(i).screenshot({ path: path.join(pngDir, `p${String(i + 1).padStart(2, '0')}.png`) });
  }
  console.log(n, 'prévias em', pngDir);
}
await browser.close();
