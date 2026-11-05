const I = require('./icons');
const C = { azul: '#0081FF', azulEsc: '#0062D6', verm: '#F22A18', graf: '#4D4D4D', gelo: '#F2F7FF', fio: '#D9E6F7' };

const PH = {
  nome: 'Dr. Miguel Nasser Hissa', crm: 'CRM-CE 2113',
  end: 'Rua Machado de Assis, 514 · Damas · Fortaleza', endCompleto: 'Rua Machado de Assis, 514 · Damas · Fortaleza-CE',
  fone: '(85) 98619-7965',
};

const CSS = `
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#fff}
body{font-family:"din-2014",sans-serif;color:${C.graf};-webkit-font-smoothing:antialiased;font-kerning:normal;font-variant-ligatures:common-ligatures}
.ab{position:relative;overflow:hidden}
.fundo{position:absolute;left:0;top:0;width:100%;height:100%;background:#fff}
.abs{position:absolute;display:block}
.t{white-space:pre;display:block}
.col{position:absolute;display:flex;flex-direction:column;align-items:flex-start}
.row{display:flex;align-items:center}
.ico{display:block;flex:none}
.guide{background:rgba(0,129,255,.10);outline:3px dashed rgba(0,98,214,.55);outline-offset:-3px}
body.export .guide{visibility:hidden}
body.solo [data-l]:not(.on){visibility:hidden!important}
body.solo .on{visibility:visible!important}
body.solo, body.solo .ab{background:transparent!important}
`;

function page(w, h, inner, extraCss = '') {
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://use.typekit.net/oqx7mxz.css">
<style>${CSS}${extraCss}</style></head><body class="export">
<div class="ab" id="ab" style="width:${w}px;height:${h}px">${inner}</div></body></html>`;
}

// atributos de camada para o PSD
const L = (name, group, kind, extra = '') => `data-l="${name}" data-g="${group}" data-k="${kind}" ${extra}`;

// texto: font = [peso, estilo], size, lh (px), cor, tracking (em)
function txt({ name, group, text, size, lh, weight = 400, italic = false, color = C.graf, track = 0, style = '', cls = '' }) {
  return `<span class="t ${cls}" ${L(name, group, 'text')} style="font-size:${size}px;line-height:${lh}px;font-weight:${weight};font-style:${italic ? 'italic' : 'normal'};color:${color};letter-spacing:${track}em;${style}">${text}</span>`;
}

function icon(name, group, svgStr, style = '') {
  return `<span class="ico" ${L(name, group, 'icon')} style="${style}">${svgStr}</span>`;
}

function shape(name, group, style) {
  return `<span class="abs-shape" ${L(name, group, 'shape')} style="display:block;${style}"></span>`;
}

module.exports = { C, PH, CSS, page, L, txt, icon, shape, I };
