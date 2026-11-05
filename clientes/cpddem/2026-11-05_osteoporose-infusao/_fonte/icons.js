// Ícones de linha (traço 4 px no tamanho final), desenhados num grid de 48.
// sw(size) converte 4 px finais para unidades do viewBox.
const sw = (size, px = 4) => (px * 48 / size).toFixed(3);

function svg(size, color, body, extra = '') {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 48 48" fill="none" stroke="${color}" stroke-width="${sw(size)}" stroke-linecap="round" stroke-linejoin="round" ${extra}>${body}</svg>`;
}

// WhatsApp: balão em linha + fone preenchido
function whatsapp(size, color, filled = false) {
  const bubble = `<path d="M24 5.5C13.8 5.5 5.5 13.6 5.5 23.6c0 3.4 1 6.6 2.6 9.3L5.5 42.5l9.9-2.6c2.6 1.4 5.5 2.2 8.6 2.2 10.2 0 18.5-8.1 18.5-18.1S34.2 5.5 24 5.5z"/>`;
  const handset = `<path stroke="none" fill="${color}" d="M18.3 14.6c.5 0 1 .1 1.3.9l2 4.7c.2.6.1 1.1-.3 1.5l-1.6 1.9c-.3.4-.3.8-.1 1.2 1.3 2.3 3.2 4.1 5.6 5.4.4.2.9.2 1.2-.1l1.9-1.7c.4-.4 1-.5 1.5-.3l4.7 2.1c.7.3.9.8.8 1.3-.4 2.6-2.6 4.5-5.4 4.4-7.9-.4-14.9-7.6-15.2-15.3-.1-2.6 1.6-5.1 3.6-6z"/>`;
  return svg(size, color, bubble + handset);
}

function cartao(size, color) {
  return svg(size, color, `<rect x="5" y="11" width="38" height="27" rx="4.5"/><path d="M5 19.5h38"/><path d="M11.5 30.5h9"/>`);
}

function prancheta(size, color) { // avaliação
  return svg(size, color, `<rect x="10" y="8.5" width="28" height="34" rx="4"/><path d="M18 8.5V6.5c0-.8.7-1.5 1.5-1.5h9c.8 0 1.5.7 1.5 1.5v2"/><path d="M17 26.5l5 5 9-10"/>`);
}

function soro(size, color) { // aplicação (bolsa de infusão com câmara de gotejamento)
  return svg(size, color, `<path d="M24 3.5v3.5"/><rect x="13.5" y="7" width="21" height="22" rx="5"/><path d="M18.5 13.5h6M18.5 18.5h6M18.5 23.5h3.5"/><path d="M24 29v3.5"/><rect x="20.5" y="32.5" width="7" height="6.5" rx="1.8"/><path d="M24 39v5.5"/>`);
}

function calendario(size, color) { // acompanhamento
  return svg(size, color, `<rect x="6.5" y="10" width="35" height="32" rx="4.5"/><path d="M6.5 19h35"/><path d="M16 6v7.5M32 6v7.5"/><path d="M17.5 30l4.5 4.5 8.5-8.5"/>`);
}

function seta(size, color, dir = 'right') {
  const rot = { right: 0, down: 90, left: 180, up: 270 }[dir];
  return svg(size, color, `<g transform="rotate(${rot} 24 24)"><path d="M8 24h31"/><path d="M27 12l12 12-12 12"/></g>`);
}

module.exports = { whatsapp, cartao, prancheta, soro, calendario, seta };
