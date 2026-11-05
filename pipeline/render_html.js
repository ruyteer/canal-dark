// Renderiza um HTML local em PNG/JPG (screenshot) ou PDF. Uso:
//   node pipeline/render_html.js pagina.html saida.jpg 1280 720
//   node pipeline/render_html.js livro.html livro.pdf
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(path.join(__dirname, 'edit', 'node_modules', 'playwright'))); }
(async () => {
  const [src, out, w = '1280', h = '720', full] = process.argv.slice(2);
  if (!src || !out) { console.error('uso: render_html.js entrada.html saida.(png|jpg|pdf) [largura altura]'); process.exit(1); }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h } });
  await page.goto('file://' + path.resolve(src), { waitUntil: 'networkidle' });
  await page.evaluate(async () => { await document.fonts.ready; if (window.__draw) window.__draw(); });
  if (out.endsWith('.pdf')) {
    await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  } else {
    await page.screenshot({ path: out, type: out.endsWith('.png') ? 'png' : 'jpeg', quality: out.endsWith('.png') ? undefined : 90, fullPage: full === 'full', omitBackground: out.endsWith('.png') });
  }
  await browser.close();
  console.log(out);
})();
