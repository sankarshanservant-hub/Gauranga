// node render.js _book.html out.pdf  — печать в PDF через Chromium (Playwright) + отчёт по страницам
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [html, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('console', m => { if (m.type() === 'error') console.log('console:', m.text()); });
  page.on('pageerror', e => console.log('pageerror:', e.message));
  await page.goto('file://' + path.resolve(html));
  await page.waitForFunction('window.__done === true', null, { timeout: 240000 });
  const rep = await page.evaluate('window.__report');
  fs.writeFileSync(path.join(path.dirname(path.resolve(html)), '_report.json'), JSON.stringify(rep, null, 1));
  console.log('проходов:', rep.passes); rep.anchors.forEach(a => console.log('  якорь', a));
  for (const p of rep.pages) console.log(String(p.n).padStart(2), p.side.padEnd(5), (p.tag.join(',') || 'text').padEnd(30), p.cols.map(c => (c.join(',') || '—').padEnd(16)).join(' | '), 'низ:', p.fill.join(' / '), 'мм');
  rep.log.forEach(l => console.log('!!', l));
  await page.pdf({ path: out, width: '210mm', height: '297mm', printBackground: true, preferCSSPageSize: true, timeout: 240000 });
  await browser.close();
  console.log('PDF:', out, (fs.statSync(out).size / 1e6).toFixed(1) + ' МБ');
})();
