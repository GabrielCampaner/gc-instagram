// Renderiza os artboards, exporta as imagens finais e grava os PSDs (pranchetas, grupos, textos editáveis).
// Uso: npm i ag-psd@20 pngjs@7 playwright  →  node render.js <pasta-de-saída>
// Gera <saída>/CPDDEM_osteoporose_v1.psd, CPDDEM_osteoporose_sequencia_v1.psd e as imagens cruas em <saída>/_raw.
// Textos e marcadores ficam em design.js (PH) e artboards.js.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const { PNG } = require('pngjs');
const { writePsdBuffer } = require('ag-psd');
const AB = require('./artboards');

const OUT = process.argv[2] || path.join(require('os').tmpdir(), 'cpddem_render');
const TMP = path.join(require('os').tmpdir(), 'cpddem_html'); fs.mkdirSync(TMP, { recursive: true });
const RAW = path.join(OUT, '_raw'); fs.mkdirSync(RAW, { recursive: true });
const PAD = 700; // margem para capturar o que sai da prancheta (grafismo)
const GROUP_ORDER = ['Fundo', 'Foto', 'Grafismo', 'Painel', 'Logo', 'Textos', 'Passos', 'Benefícios', 'Dúvidas', 'CTA', 'Rodapé', 'Guias']; // de baixo para cima

const PS_FONT = (w, italic) => {
  const map = { 400: 'Regular', 600: 'Demi', 700: 'Bold', 800: 'ExtraBold' };
  const st = map[w] || 'Regular';
  return 'DIN2014-' + st + (italic ? (st === 'Regular' ? 'Italic' : 'Italic') : '');
};
const rgb = (s) => { const m = s.match(/\d+(\.\d+)?/g).map(Number); return { r: m[0], g: m[1], b: m[2], a: m[3] == null ? 1 : m[3] }; };

async function load(browser, html, w, h, file) {
  fs.writeFileSync(file, html);
  const p = await browser.newPage({ viewport: { width: w, height: h } });
  await p.goto('file://' + file);
  await p.evaluate(() => document.fonts.ready);
  const faces = await p.evaluate(async () => {
    const els = [...document.querySelectorAll('[data-k=text]')];
    const res = await Promise.all(els.map(e => { const cs = getComputedStyle(e); return document.fonts.load(`${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} din-2014`, e.textContent); }));
    return els.map((e, i) => { const cs = getComputedStyle(e); return [e.dataset.l, cs.fontWeight, cs.fontStyle, res[i].length, document.fonts.check(`${cs.fontStyle} ${cs.fontWeight} 20px din-2014`)]; });
  });
  const bad = faces.filter(f => !f[4]); if (bad.length) throw new Error('fonte não carregou: ' + JSON.stringify(bad));
  await p.waitForTimeout(400);
  return p;
}

function decode(buf) { return PNG.sync.read(buf); }
function alphaBBox(png) {
  const { width, height, data } = png; let l = width, t = height, r = -1, b = -1;
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    if (data[(y * width + x) * 4 + 3] > 0) { if (x < l) l = x; if (x > r) r = x; if (y < t) t = y; if (y > b) b = y; }
  }
  return r < 0 ? null : { l, t, r: r + 1, b: b + 1 };
}
function crop(png, bb) {
  const w = bb.r - bb.l, h = bb.b - bb.t; const out = new Uint8ClampedArray(w * h * 4);
  for (let y = 0; y < h; y++) {
    const s = ((bb.t + y) * png.width + bb.l) * 4; out.set(png.data.subarray(s, s + w * 4), y * w * 4);
  }
  return { width: w, height: h, data: out };
}

// retângulo arredondado (raio por canto: [sup.esq, sup.dir, inf.dir, inf.esq]) → nós de Bézier
function rrectKnots(l, t, r, b, rad) {
  const R = (Array.isArray(rad) ? rad : [rad, rad, rad, rad]).map(v => Math.max(0, Math.min(v, (r - l) / 2, (b - t) / 2)));
  const K = 0.5522847498; const [tl, tr, br, bl] = R;
  const C4 = [
    { r: tl, a: [l, t + tl], b: [l + tl, t], ha: [l, t + tl - K * tl], hb: [l + tl - K * tl, t] },
    { r: tr, a: [r - tr, t], b: [r, t + tr], ha: [r - tr + K * tr, t], hb: [r, t + tr - K * tr] },
    { r: br, a: [r, b - br], b: [r - br, b], ha: [r, b - br + K * br], hb: [r - br + K * br, b] },
    { r: bl, a: [l + bl, b], b: [l, b - bl], ha: [l + bl - K * bl, b], hb: [l, b - bl + K * bl] },
  ];
  const nodes = [];
  for (const c of C4) {
    if (c.r <= 0.01) { nodes.push({ linked: false, points: [c.a[0], c.a[1], c.a[0], c.a[1], c.a[0], c.a[1]] }); continue; }
    nodes.push({ linked: true, points: [c.a[0], c.a[1], c.a[0], c.a[1], c.ha[0], c.ha[1]] });
    nodes.push({ linked: true, points: [c.hb[0], c.hb[1], c.b[0], c.b[1], c.b[0], c.b[1]] });
  }
  // junta nós repetidos (lado de comprimento zero, ex.: pílula)
  const out = [];
  for (const n of nodes) {
    const p = out[out.length - 1];
    if (p && Math.abs(p.points[2] - n.points[2]) < 0.01 && Math.abs(p.points[3] - n.points[3]) < 0.01) { p.points[4] = n.points[4]; p.points[5] = n.points[5]; }
    else out.push(n);
  }
  const f = out[0], z = out[out.length - 1];
  if (out.length > 1 && Math.abs(f.points[2] - z.points[2]) < 0.01 && Math.abs(f.points[3] - z.points[3]) < 0.01) { f.points[0] = z.points[0]; f.points[1] = z.points[1]; out.pop(); }
  return out;
}

async function processArtboard(browser, def, offsetX) {
  const file = path.join(TMP, `_${def.key}.html`);
  // 1) imagem final
  const p = await load(browser, def.html, def.w, def.h, file);
  const finalPng = path.join(RAW, `${def.key}.png`);
  await p.screenshot({ path: finalPng });
  // 2) dados das camadas
  const layers = await p.evaluate(() => {
    const ctx = document.createElement('canvas').getContext('2d');
    return [...document.querySelectorAll('[data-l]')].map((e, i) => {
      const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
      const o = { i, name: e.dataset.l, group: e.dataset.g, kind: e.dataset.k, rect: { x: r.left, y: r.top, w: r.width, h: r.height } };
      if (o.kind === 'text') {
        const size = parseFloat(cs.fontSize), lh = parseFloat(cs.lineHeight);
        const ls = cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) / size;
        ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${size}px din-2014`;
        const m = ctx.measureText('Hgx');
        const rg = document.createRange(); rg.setStart(e.firstChild, 0); rg.setEnd(e.firstChild, 1);
        const fr = rg.getClientRects()[0];
        o.text = { str: e.textContent, size, lh, ls, weight: +cs.fontWeight, italic: cs.fontStyle === 'italic', color: cs.color,
          asc: m.fontBoundingBoxAscent, desc: m.fontBoundingBoxDescent, baseline: fr.top + m.fontBoundingBoxAscent, x: fr.left };
      }
      if (o.kind === 'shape' || o.kind === 'guide') {
        o.fill = cs.backgroundColor;
        const rv = (v) => v.endsWith('%') ? parseFloat(v) / 100 * Math.min(r.width, r.height) : (parseFloat(v) || 0);
        o.radius = [rv(cs.borderTopLeftRadius), rv(cs.borderTopRightRadius), rv(cs.borderBottomRightRadius), rv(cs.borderBottomLeftRadius)];
      }
      if (o.kind === 'fill') o.fill = cs.backgroundColor;
      return o;
    });
  });
  await p.close();
  // 3) pixels de cada camada (isolada, fundo transparente, com margem)
  const sp = await load(browser, def.html.replace('<body class="export">', '<body class="solo">')
    .replace('</style>', `html,body{background:transparent!important}.ab{overflow:visible!important;margin:${PAD}px}</style>`), def.w + 2 * PAD, def.h + 2 * PAD, file);
  for (const L of layers) {
    await sp.evaluate((i) => { document.querySelectorAll('[data-l]').forEach((e, j) => e.classList.toggle('on', j === i)); }, L.i);
    const full = L.kind === 'image' || L.kind === 'fill' || L.kind === 'raster';
    const m = 80;
    const clip = full ? undefined : {
      x: Math.max(0, Math.floor(PAD + L.rect.x - m)), y: Math.max(0, Math.floor(PAD + L.rect.y - m)),
      width: Math.ceil(L.rect.w + 2 * m), height: Math.ceil(L.rect.h + 2 * m),
    };
    const png = decode(await sp.screenshot({ omitBackground: true, clip }));
    const bb = alphaBBox(png);
    if (!bb) { L.empty = true; continue; }
    const ox = clip ? clip.x : 0, oy = clip ? clip.y : 0;
    L.px = crop(png, bb);
    L.left = offsetX + bb.l + ox - PAD; L.top = bb.t + oy - PAD;
  }
  await sp.close();
  return { layers, finalPng };
}

function toPsdLayer(L, offsetX) {
  const base = { name: L.name, blendMode: 'normal', opacity: 1 };
  if (L.kind === 'fill') {
    const c = rgb(L.fill);
    return { ...base, left: offsetX, top: 0, right: offsetX + L.rect.w, bottom: L.rect.h, imageData: L.px,
      vectorFill: { type: 'color', color: { r: c.r, g: c.g, b: c.b } },
      vectorMask: { paths: [{ open: false, operation: 'combine', fillRule: 'non-zero', knots: rrectKnots(offsetX, 0, offsetX + L.rect.w, L.rect.h, 0) }] } };
  }
  if (L.empty) return null;
  const px = { left: L.left, top: L.top, right: L.left + L.px.width, bottom: L.top + L.px.height, imageData: L.px };
  if (L.kind === 'text') {
    const T = L.text; const c = rgb(T.color);
    return { ...base, ...px, text: {
      text: T.str.replace(/\n/g, '\r'),
      transform: [1, 0, 0, 1, offsetX + T.x, T.baseline],
      antiAlias: 'smooth', shapeType: 'point',
      style: { font: { name: PS_FONT(T.weight, T.italic) }, fontSize: T.size, autoLeading: false, leading: T.lh,
        tracking: Math.round(T.ls * 1000), autoKerning: true, fillColor: { r: c.r, g: c.g, b: c.b } },
      paragraphStyle: { justification: 'left' },
    } };
  }
  if (L.kind === 'shape' || L.kind === 'guide') {
    const c = rgb(L.fill); const x = offsetX + Math.round(L.rect.x), y = Math.round(L.rect.y);
    const lyr = { ...base, ...px, vectorFill: { type: 'color', color: { r: c.r, g: c.g, b: c.b } },
      vectorMask: { paths: [{ open: false, operation: 'combine', fillRule: 'non-zero', knots: rrectKnots(x, y, x + Math.round(L.rect.w), y + Math.round(L.rect.h), L.radius) }] } };
    if (L.kind === 'guide') { lyr.hidden = true; lyr.fillOpacity = Math.round(c.a * 255) / 255; }
    else if (c.a < 1) lyr.opacity = Math.round(c.a * 255) / 255;
    return lyr;
  }
  return { ...base, ...px }; // image / icon
}

function buildTree(layers, offsetX) {
  const root = {};
  for (const L of layers) {
    const lyr = toPsdLayer(L, offsetX); if (!lyr) continue;
    const parts = L.group.split('/');
    let node = root;
    for (const part of parts) { node.sub = node.sub || {}; node.sub[part] = node.sub[part] || { name: part, items: [] }; node = node.sub[part]; }
    node.items.push(lyr);
  }
  const toChildren = (node) => {
    const kids = [...(node.items || [])];
    if (node.sub) Object.values(node.sub).forEach(s => kids.push({ name: s.name, opened: s.name !== 'Guias', hidden: false, children: toChildren(s) }));
    return kids;
  };
  return GROUP_ORDER.filter(g => root.sub && root.sub[g]).map(g => ({ name: g, opened: true, children: toChildren(root.sub[g]) }));
}

async function makePsd(browser, defs, psdName) {
  const GAP = 400;
  let x = 0; const boards = [];
  const W = defs.reduce((s, d) => s + d.w, 0) + GAP * (defs.length - 1); const H = Math.max(...defs.map(d => d.h));
  for (const d of defs) {
    const r = await processArtboard(browser, d, x);
    boards.push({ name: d.name, opened: true, artboard: { rect: { top: 0, left: x, bottom: d.h, right: x + d.w }, presetName: d.preset, color: { r: 255, g: 255, b: 255 }, backgroundType: 1 },
      children: buildTree(r.layers, x), _final: r.finalPng, _x: x, _w: d.w, _h: d.h });
    x += d.w + GAP;
  }
  // composição do documento (pranchetas sobre fundo transparente)
  const comp = new Uint8ClampedArray(W * H * 4);
  for (const b of boards) {
    const png = PNG.sync.read(fs.readFileSync(b._final));
    for (let yy = 0; yy < png.height; yy++) comp.set(png.data.subarray(yy * png.width * 4, (yy + 1) * png.width * 4), (yy * W + b._x) * 4);
  }
  const psd = {
    width: W, height: H, channels: 4,
    imageResources: { resolutionInfo: { horizontalResolution: 72, horizontalResolutionUnit: 'PPI', widthUnit: 'Inches', verticalResolution: 72, verticalResolutionUnit: 'PPI', heightUnit: 'Inches' } },
    artboards: { count: boards.length, autoExpandOffset: { horizontal: 0, vertical: 0 }, origin: { horizontal: 0, vertical: 0 }, autoExpandEnabled: true, autoNestEnabled: true, autoPositionEnabled: true, shrinkwrapOnSaveEnabled: true, docDefaultNewArtboardBackgroundColor: { r: 255, g: 255, b: 255 }, docDefaultNewArtboardBackgroundType: 1 },
    imageData: { width: W, height: H, data: comp },
    children: boards.map(({ _final, _x, _w, _h, ...b }) => b),
  };
  const buf = writePsdBuffer(psd, { logMissingFeatures: true });
  fs.writeFileSync(path.join(OUT, psdName), buf);
  console.log('PSD', psdName, (buf.length / 1e6).toFixed(1) + ' MB', boards.map(b => b.name).join(', '));
}

(async () => {
  const browser = await chromium.launch();
  const mk = (fn, key, preset) => ({ ...AB[fn](), key, preset });
  await makePsd(browser, [mk('story', 'story', 'Instagram Story'), mk('whatsapp', 'whatsapp', 'Instagram 4:5'), mk('whatsappDuvidas', 'whatsappDuvidas', 'Instagram 4:5')], 'CPDDEM_osteoporose_v2.psd');
  await makePsd(browser, ['seq1', 'seq2', 'seq3', 'seq4', 'seq5'].map(k => mk(k, k, 'Instagram Story')), 'CPDDEM_osteoporose_sequencia_v2.psd');
  await browser.close();
})();
