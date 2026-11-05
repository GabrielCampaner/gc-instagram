// Prévia: mesmas peças, com a figurinha de link do Instagram simulada na área reservada
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const AB = require('./artboards');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch();
  for (const k of ['seq5', 'story']) {
    const a = AB[k](); const f = path.join(require('os').tmpdir(), `_prev_${k}.html`); fs.writeFileSync(f, a.html);
    const p = await b.newPage({ viewport: { width: a.w, height: a.h } });
    await p.goto('file://' + f); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(600);
    await p.evaluate(() => {
      const base = [...document.querySelectorAll('[data-l]')].find(e => e.dataset.l === 'Base da figurinha de link');
      const r = base.getBoundingClientRect();
      const s = document.createElement('div');
      s.style.cssText = `position:absolute;left:${r.left + 30}px;top:${r.top + 12}px;width:${r.width - 60}px;height:${r.height - 24}px;background:#fff;border-radius:22px;box-shadow:0 4px 18px rgba(0,0,0,.18);display:flex;align-items:center;justify-content:center;gap:16px;font:700 38px/1 -apple-system,Helvetica,Arial,sans-serif;color:#3a7bf0;letter-spacing:.02em;z-index:9`;
      s.innerHTML = `<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#3a7bf0" stroke-width="2.4" stroke-linecap="round"><path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>AGENDAR AVALIAÇÃO`;
      document.body.appendChild(s);
      const t = document.createElement('div');
      t.textContent = 'simulação da figurinha (entra pelo app)';
      t.style.cssText = `position:absolute;left:${r.left}px;top:${r.bottom + 6}px;font:italic 400 22px/1 din-2014,sans-serif;color:#d0021b;z-index:9`;
      document.body.appendChild(t);
    });
    await p.screenshot({ path: path.join(OUT, `_prev_${k}.png`) }); await p.close();
  }
  await b.close();
})();
