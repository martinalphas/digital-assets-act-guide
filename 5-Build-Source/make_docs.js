// Renders the PDF explainer and the social preview image from the built HTML.
// Usage: node src/make_docs.js <base-url-of-local-server>
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const base = process.argv[2] || 'http://127.0.0.1:8765';
  const root = path.resolve(__dirname, '..');
  const browser = await chromium.launch();

  // PDF
  const page = await browser.newPage();
  await page.emulateMedia({ media: 'print', colorScheme: 'light' });
  await page.goto(`${base}/_print.html`, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: path.join(root, 'deliverables', 'DAF-Act-Tokeniser-Explainer.pdf'),
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate:
      '<div style="width:100%;font-size:7.5px;color:#848B91;padding:0 15mm;display:flex;justify-content:space-between;font-family:Arial,sans-serif;">' +
      '<span>DAF Act explainer · General information only, not legal advice · As at 26 October 2026</span>' +
      '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
  });

  // Social preview image (1200x630)
  const og = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  await og.goto(`${base}/_og.html`, { waitUntil: 'networkidle' });
  await og.evaluate(() => document.fonts.ready);
  await og.screenshot({ path: path.join(root, 'site', 'assets', 'og.png') });

  await browser.close();
  console.log('pdf and og image written');
})();
