// v2 · linha humanizada: foto no topo + painel branco com a marca; benefícios, dúvidas e CTA explicado
const { C, PH, page, L, txt, icon, shape, I } = require('./design');
const path = require('path');
const LOGO = { 'logo_horizontal.png': 'CPDDEM_logo_horizontal_transparente.png', 'arcos_azuis.png': 'CPDDEM_grafismo_arcos_azuis.png' };
// logos vêm de ../logo; fotos recortadas ficam em ./assets (fora do Git, ver LEIA-ME)
const A = (f) => 'file://' + (LOGO[f] ? path.join(__dirname, '..', 'logo', LOGO[f]) : path.join(__dirname, 'assets', f));
const W = 1080;

const STOCK = { familia: '436582561', equipe: '374753388', medica: '1890701560' };

// ---------- peças base ----------
const fundo = (cor = '#FFFFFF') => `<div class="fundo" ${L('Fundo', 'Fundo', 'fill')} style="background:${cor}"></div>`;
const logo = (w) => `<img src="${A('logo_horizontal.png')}" ${L('Logo CPDDEM (horizontal)', 'Logo', 'image')} style="display:block;flex:none;width:${w}px;height:${Math.round(w * 1315 / 2458)}px">`;
const idTexto = `Diretor técnico-médico: ${PH.nome}\n${PH.crm} · ${PH.rqe}\n${PH.end}`;
const marca = (logoW = 250) => `<div class="row" style="width:100%">
    ${logo(logoW)}
    ${txt({ name: 'Identificação do diretor técnico-médico', group: 'Rodapé', text: idTexto, size: 26, lh: 34, style: 'margin-left:30px' })}
  </div>`;

function foto(key, file, w, h, top = 0) {
  return `<img class="abs" src="${A(file)}" ${L(`Foto (Adobe Stock ${STOCK[key]})`, 'Foto', 'image')} style="left:0;top:${top}px;width:${w}px;height:${h}px">`;
}
function ilustrativa(right, bottom) {
  return `<div class="abs row" style="right:${right}px;top:${bottom - 46}px;height:46px">
    ${shape('Selo imagem ilustrativa (fundo)', 'Foto', 'position:absolute;left:0;top:0;width:100%;height:100%;background:rgba(0,0,0,0.38);border-radius:23px')}
    ${txt({ name: 'Imagem ilustrativa', group: 'Foto', text: 'Imagem ilustrativa', size: 24, lh: 30, weight: 400, color: '#FFFFFF', style: 'position:relative;margin:0 20px' })}
  </div>`;
}
const painel = (top, h) => shape('Painel branco', 'Painel', `position:absolute;left:0;top:${top}px;width:${W}px;height:${h - top + 80}px;background:#FFFFFF;border-radius:56px 56px 0 0`);
function arcos({ h, left, top, name = 'Arcos azuis do símbolo', opacity = 1 }) {
  const w = Math.round(h * 1230 / 1727);
  return `<img class="abs" src="${A('arcos_azuis.png')}" ${L(name, 'Grafismo', 'image')} style="left:${left}px;top:${top}px;width:${w}px;height:${h}px;opacity:${opacity}">`;
}
const guias = (extra = '') => `
  <div class="guide abs" ${L('Área livre do topo (250 px)', 'Guias', 'guide')} style="left:0;top:0;width:1080px;height:250px"></div>
  <div class="guide abs" ${L('Área livre da base (270 px)', 'Guias', 'guide')} style="left:0;top:1650px;width:1080px;height:270px"></div>${extra}`;
const cartaoTopo = (top = 236, h = 196) => shape('Cartão da marca', 'Logo', `position:absolute;left:48px;top:${top}px;width:984px;height:${h}px;background:#FFFFFF;border-radius:36px`);

// pílula de ação (texto + seta), fundo gelo
function pilula({ name, group = 'CTA', text, size = 40, h = 88, bg = C.gelo, color = C.azulEsc, arrow = 'right', mt = 0 }) {
  return `<div class="row" style="position:relative;height:${h}px;padding:0 34px 0 38px;margin-top:${mt}px">
    ${shape(`${name} (fundo)`, group, `position:absolute;left:0;top:0;width:100%;height:100%;background:${bg};border-radius:${h / 2}px`)}
    ${txt({ name, group, text, size, lh: size + 8, weight: 700, color, style: 'position:relative' })}
    ${icon(`${name} · seta`, group, I.seta(Math.round(size * 1.1), color, arrow), 'position:relative;margin-left:14px')}
  </div>`;
}

// lista com visto
function lista(itens, { group = 'Benefícios', size = 36, lh = 46, color = C.graf, chk = C.azul, chkBg = '#E3EEFF', gap = 22, iconSize = 46 }) {
  return itens.map((t, i) => `<div class="row" style="align-items:flex-start;margin-top:${i ? gap : 0}px">
      ${icon(`Visto ${i + 1}`, group, I.check(iconSize, chk, chkBg), `margin-right:20px;margin-top:${Math.round((lh - iconSize) / 2)}px`)}
      ${txt({ name: `Item ${i + 1}`, group, text: t, size, lh, weight: 400, color })}
    </div>`).join('');
}

// passos com número em círculo
function passos(dados, { group = 'Passos', size = 36, lh = 44, tSize = 40, circ = 64, gap = 26 }) {
  return dados.map(([n, t, d], i) => {
    const g = `${group}/Passo ${n}`;
    return `<div class="row" style="align-items:flex-start;margin-top:${i ? gap : 0}px">
      <div style="position:relative;width:${circ}px;height:${circ}px;flex:none;margin-right:26px;display:flex;align-items:center;justify-content:center">
        ${shape(`Círculo ${n}`, g, `position:absolute;left:0;top:0;width:100%;height:100%;background:${C.azul};border-radius:50%`)}
        ${txt({ name: `Número ${n}`, group: g, text: n, size: 38, lh: 44, weight: 700, color: '#FFFFFF', style: 'position:relative' })}
      </div>
      <div style="display:flex;flex-direction:column">
        ${txt({ name: `Título ${n}`, group: g, text: t, size: tSize, lh: tSize + 6, weight: 700, color: '#222B38' })}
        ${txt({ name: `Descrição ${n}`, group: g, text: d, size, lh, weight: 400, color: C.graf, style: 'margin-top:4px' })}
      </div>
    </div>`;
  }).join('');
}

// balões de conversa (dúvidas)
function balao(n, tipo, text, { size = 36, lh = 46, maxW = 800, group = 'Dúvidas' }) {
  const p = tipo === 'q';
  const g = `${group}/Dúvida ${n}`;
  const name = p ? `Pergunta ${n}` : `Resposta ${n}`;
  return `<div style="display:flex;width:100%;justify-content:${p ? 'flex-start' : 'flex-end'};margin-top:${p ? 30 : 12}px">
    <div class="row" style="position:relative;max-width:${maxW}px;padding:22px 30px">
      ${shape(`${name} (balão)`, g, `position:absolute;left:0;top:0;width:100%;height:100%;background:${p ? '#FFFFFF' : C.azulEsc};border-radius:${p ? '8px 34px 34px 34px' : '34px 8px 34px 34px'}`)}
      ${txt({ name, group: g, text, size, lh, weight: p ? 700 : 400, color: p ? '#222B38' : '#FFFFFF', style: 'position:relative' })}
    </div>
  </div>`;
}

const STEPS = [
  ['1', 'Consulta de avaliação', 'O médico conversa com você e confirma\nse a infusão é indicada.'],
  ['2', 'Aplicação aqui na clínica', 'Na veia, como um soro, numa poltrona\nconfortável e com a equipe por perto.'],
  ['3', 'Retorno', 'Você volta para tirar dúvidas\ne receber orientações.'],
];
const DUVIDAS = [
  ['Preciso de consulta antes?', 'Sim. A infusão só é feita depois\nda avaliação e com indicação médica.'],
  ['A aplicação dói?', 'É feita na veia, parecida com tomar\nsoro. A equipe acompanha você o tempo todo.'],
  ['Como posso pagar?', 'Em até 12x no cartão de crédito.'],
];

// ---------- SEQUÊNCIA ----------
function seq1() {
  const PT = 820;
  const inner = `
  ${fundo()}
  ${foto('familia', 'foto_familia_story.jpg', 1080, 880)}
  ${ilustrativa(36, PT - 24)}
  ${painel(PT, 1920)}
  <div class="col" style="left:88px;top:${PT + 44}px;width:904px">
    ${marca(250)}
    ${txt({ name: 'Chamada', group: 'Textos', text: 'SAÚDE ÓSSEA', size: 34, lh: 40, weight: 600, italic: true, color: C.verm, track: 0.08, style: 'margin-top:44px' })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'Recebeu o diagnóstico\nde osteoporose?', size: 90, lh: 92, weight: 800, color: C.azul, track: -0.01, style: 'margin-top:10px' })}
    ${txt({ name: 'Texto', group: 'Textos', text: 'Existe tratamento por infusão. No CPDDEM,\na nossa equipe avalia o seu caso e\nacompanha você em cada etapa.', size: 38, lh: 50, style: 'margin-top:22px' })}
    ${pilula({ name: 'Convite: ver como funciona', text: 'Toque para ver como funciona', size: 38, h: 84, mt: 34 })}
  </div>
  ${guias()}`;
  return { name: 'Story 1 · Gancho', w: W, h: 1920, html: page(W, 1920, inner) };
}

function seq2() {
  const PT = 740;
  const inner = `
  ${fundo()}
  ${foto('equipe', 'foto_equipe_story.jpg', 1080, 800)}
  ${ilustrativa(36, PT - 24)}
  ${painel(PT, 1920)}
  <div class="col" style="left:88px;top:${PT + 44}px;width:904px">
    ${marca(250)}
    ${txt({ name: 'Chamada', group: 'Textos', text: 'COMO FUNCIONA', size: 34, lh: 40, weight: 600, italic: true, color: C.verm, track: 0.08, style: 'margin-top:40px' })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'Feito aqui na clínica,\ncom a equipe ao seu lado', size: 76, lh: 80, weight: 800, color: C.azul, track: -0.01, style: 'margin-top:10px' })}
    <div style="width:100%;margin-top:36px">${passos(STEPS, { size: 32, lh: 40, tSize: 38, circ: 60, gap: 24 })}</div>
  </div>
  ${guias()}`;
  return { name: 'Story 2 · Como funciona', w: W, h: 1920, html: page(W, 1920, inner) };
}

function seq3() {
  const itens = [
    'Consulta de avaliação antes\nde qualquer aplicação',
    'Aplicação aqui na clínica, com a\nequipe acompanhando do início ao fim',
    'Uma alternativa ao tratamento em\ncomprimidos, quando o médico indicar',
    'Retorno com orientações\ndepois da aplicação',
    'Pagamento em até 12x\nno cartão de crédito',
  ];
  const inner = `
  ${fundo(C.azulEsc)}
  <span class="abs" ${L('Degradê do fundo', 'Fundo', 'raster')} style="left:0;top:0;width:1080px;height:1920px;background:linear-gradient(180deg, ${C.azul} 0%, ${C.azulEsc} 70%)"></span>
  ${arcos({ h: 1100, left: 660, top: 1560, opacity: 0.9 })}
  ${cartaoTopo(236, 196)}
  <div class="col" style="left:88px;top:267px;width:904px">${marca(250)}</div>
  <div class="col" style="left:88px;top:520px;width:904px">
    ${txt({ name: 'Chamada', group: 'Textos', text: 'BENEFÍCIOS', size: 34, lh: 40, weight: 600, italic: true, color: '#BFF6FF', track: 0.08 })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'O que você encontra\nno CPDDEM', size: 84, lh: 88, weight: 800, color: '#FFFFFF', track: -0.01, style: 'margin-top:10px' })}
    <div style="width:100%;margin-top:52px">${lista(itens, { size: 41, lh: 52, color: '#FFFFFF', chk: C.azulEsc, chkBg: '#FFFFFF', gap: 38, iconSize: 52 })}</div>
  </div>
  ${guias()}`;
  return { name: 'Story 3 · Benefícios', w: W, h: 1920, html: page(W, 1920, inner) };
}

function seq4() {
  const inner = `
  ${fundo(C.gelo)}
  ${arcos({ h: 700, left: 830, top: -280 })}
  ${cartaoTopo(236, 196)}
  <div class="col" style="left:88px;top:267px;width:904px">${marca(250)}</div>
  <div class="col" style="left:88px;top:500px;width:904px">
    ${txt({ name: 'Chamada', group: 'Textos', text: 'DÚVIDAS FREQUENTES', size: 34, lh: 40, weight: 600, italic: true, color: C.verm, track: 0.08 })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'O que mais perguntam\npara a nossa equipe', size: 76, lh: 80, weight: 800, color: C.azul, track: -0.01, style: 'margin-top:10px' })}
    <div style="width:100%;margin-top:14px">
      ${DUVIDAS.map(([q, a], i) => balao(i + 1, 'q', q, { size: 40, lh: 48 }) + balao(i + 1, 'a', a, { size: 36, lh: 46, maxW: 880 })).join('')}
    </div>
    ${txt({ name: 'Ponte para o próximo story', group: 'CTA', text: 'Ficou outra dúvida? É só chamar no WhatsApp.', size: 38, lh: 46, weight: 600, color: C.azulEsc, style: 'margin-top:44px' })}
  </div>
  ${guias()}`;
  return { name: 'Story 4 · Dúvidas', w: W, h: 1920, html: page(W, 1920, inner) };
}

function seq5() {
  const PT = 740;
  const inner = `
  ${fundo()}
  ${foto('medica', 'foto_medica_story.jpg', 1080, 800)}
  ${ilustrativa(36, PT - 24)}
  ${painel(PT, 1920)}
  <div class="col" style="left:88px;top:${PT + 44}px;width:904px">
    ${marca(250)}
    ${txt({ name: 'Headline', group: 'CTA', text: 'Agende sua avaliação', size: 96, lh: 100, weight: 800, color: C.azul, track: -0.01, style: 'margin-top:44px' })}
    ${txt({ name: 'Texto', group: 'CTA', text: 'Fale com a nossa equipe pelo WhatsApp.\nA gente tira suas dúvidas e marca a consulta.', size: 40, lh: 52, style: 'margin-top:16px' })}
    <div class="row" style="margin-top:40px">
      ${icon('Ícone toque', 'CTA', I.mao(56, C.azulEsc), 'margin-right:14px')}
      ${txt({ name: 'Instrução: toque no link', group: 'CTA', text: 'Toque no link abaixo para conversar', size: 42, lh: 50, weight: 700, color: C.azulEsc })}
    </div>
    <div style="position:relative;width:700px;height:120px;margin-top:16px">
      ${shape('Base da figurinha de link', 'CTA', `position:absolute;left:0;top:0;width:100%;height:100%;background:${C.gelo};border-radius:60px`)}
      <div class="guide abs" ${L('Área da figurinha de link (700 × 120)', 'Guias', 'guide')} style="left:0;top:0;width:700px;height:120px"></div>
    </div>
    <div class="row" style="margin-top:26px">
      ${icon('Ícone WhatsApp', 'CTA', I.whatsapp(46, C.azulEsc), 'margin-right:14px')}
      ${txt({ name: 'Número do WhatsApp', group: 'CTA', text: `ou chame no ${PH.fone}`, size: 38, lh: 46, weight: 600, color: C.graf })}
    </div>
    ${txt({ name: 'Pagamento', group: 'CTA', text: 'Pagamento em até 12x no cartão de crédito', size: 32, lh: 40, weight: 400, color: C.graf, style: 'margin-top:18px' })}
  </div>
  ${guias()}`;
  return { name: 'Story 5 · Agende', w: W, h: 1920, html: page(W, 1920, inner) };
}

// ---------- STORY ÚNICO ----------
function story() {
  const PT = 700;
  const inner = `
  ${fundo()}
  ${foto('equipe', 'foto_equipe_unico.jpg', 1080, 760)}
  ${ilustrativa(36, PT - 24)}
  ${painel(PT, 1920)}
  <div class="col" style="left:88px;top:${PT + 44}px;width:904px">
    ${marca(250)}
    ${txt({ name: 'Chamada', group: 'Textos', text: 'SAÚDE ÓSSEA', size: 34, lh: 40, weight: 600, italic: true, color: C.verm, track: 0.08, style: 'margin-top:36px' })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'Osteoporose tem\ntratamento por infusão', size: 84, lh: 86, weight: 800, color: C.azul, track: -0.01, style: 'margin-top:8px' })}
    <div style="width:100%;margin-top:26px">${lista(['Consulta de avaliação antes de começar', 'Aplicação aqui na clínica, com a equipe', 'Pagamento em até 12x no cartão'], { size: 36, lh: 44, gap: 14, iconSize: 44 })}</div>
    <div class="row" style="margin-top:30px">
      ${icon('Ícone toque', 'CTA', I.mao(50, C.azulEsc), 'margin-right:14px')}
      ${txt({ name: 'Instrução: toque no link', group: 'CTA', text: 'Toque no link e agende sua avaliação', size: 38, lh: 46, weight: 700, color: C.azulEsc })}
    </div>
    <div style="position:relative;width:700px;height:120px;margin-top:14px">
      ${shape('Base da figurinha de link', 'CTA', `position:absolute;left:0;top:0;width:100%;height:100%;background:${C.gelo};border-radius:60px`)}
      <div class="guide abs" ${L('Área da figurinha de link (700 × 120)', 'Guias', 'guide')} style="left:0;top:0;width:700px;height:120px"></div>
    </div>
  </div>
  ${guias()}`;
  return { name: 'Story único', w: W, h: 1920, html: page(W, 1920, inner) };
}

// ---------- WHATSAPP 1080x1350 ----------
function whatsapp() {
  const PT = 490;
  const inner = `
  ${fundo()}
  ${foto('medica', 'foto_medica_whatsapp.jpg', 1080, 540)}
  ${ilustrativa(32, PT - 22)}
  ${painel(PT, 1350)}
  ${shape('Faixa do rodapé', 'Rodapé', `position:absolute;left:0;top:1240px;width:1080px;height:110px;background:${C.gelo}`)}
  <div class="col" style="left:88px;top:${PT + 38}px;width:904px">
    ${logo(230)}
    ${txt({ name: 'Headline', group: 'Textos', text: 'Osteoporose tem\ntratamento por infusão', size: 72, lh: 74, weight: 800, color: C.azul, track: -0.01, style: 'margin-top:24px' })}
    <div style="width:100%;margin-top:22px">${lista(['Consulta de avaliação antes de começar', 'Aplicação aqui na clínica, com a equipe ao seu lado', 'Pagamento em até 12x no cartão de crédito'], { size: 32, lh: 40, gap: 12, iconSize: 40 })}</div>
    <div class="row" style="margin-top:28px;width:100%">
      <div class="row" style="position:relative;height:92px;padding:0 40px 0 32px">
        ${shape('Botão (fundo)', 'CTA', `position:absolute;left:0;top:0;width:100%;height:100%;background:${C.azulEsc};border-radius:46px`)}
        ${icon('Ícone WhatsApp', 'CTA', I.whatsapp(46, '#FFFFFF'), 'position:relative;margin-right:14px')}
        ${txt({ name: 'Botão: Agende sua avaliação', group: 'CTA', text: 'Agende sua avaliação', size: 40, lh: 48, weight: 700, color: '#FFFFFF', style: 'position:relative' })}
      </div>
      ${txt({ name: 'Número do WhatsApp', group: 'CTA', text: PH.fone, size: 38, lh: 46, weight: 700, color: C.graf, style: 'margin-left:28px' })}
    </div>
  </div>
  ${txt({ name: 'Identificação do diretor técnico-médico', group: 'Rodapé', text: `CPDDEM · ${PH.endCompleto}\nDiretor técnico-médico: ${PH.nome} · ${PH.crm} · ${PH.rqe}`, size: 26, lh: 34, style: 'position:absolute;left:88px;top:1261px' })}
  `;
  return { name: 'WhatsApp · Principal', w: W, h: 1350, html: page(W, 1350, inner) };
}

function whatsappDuvidas() {
  const inner = `
  ${fundo(C.gelo)}
  ${arcos({ h: 560, left: 860, top: -230 })}
  <div class="col" style="left:88px;top:70px;width:904px">
    ${logo(230)}
    ${txt({ name: 'Chamada', group: 'Textos', text: 'DÚVIDAS FREQUENTES', size: 32, lh: 38, weight: 600, italic: true, color: C.verm, track: 0.08, style: 'margin-top:30px' })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'Infusão para osteoporose', size: 66, lh: 70, weight: 800, color: C.azul, track: -0.01, style: 'margin-top:6px' })}
    <div style="width:100%;margin-top:0px">
      ${DUVIDAS.map(([q, a], i) => balao(i + 1, 'q', q, { size: 34, lh: 42 }) + balao(i + 1, 'a', a, { size: 32, lh: 40, maxW: 820 })).join('')}
    </div>
    ${txt({ name: 'Fechamento', group: 'CTA', text: 'Ficou outra dúvida? É só responder esta mensagem.', size: 34, lh: 42, weight: 600, color: C.azulEsc, style: 'margin-top:36px' })}
  </div>
  ${shape('Faixa do rodapé', 'Rodapé', `position:absolute;left:0;top:1240px;width:1080px;height:110px;background:#FFFFFF`)}
  ${txt({ name: 'Identificação do diretor técnico-médico', group: 'Rodapé', text: `CPDDEM · ${PH.endCompleto}\nDiretor técnico-médico: ${PH.nome} · ${PH.crm} · ${PH.rqe}`, size: 26, lh: 34, style: 'position:absolute;left:88px;top:1261px' })}
  `;
  return { name: 'WhatsApp · Dúvidas', w: W, h: 1350, html: page(W, 1350, inner) };
}

module.exports = { seq1, seq2, seq3, seq4, seq5, story, whatsapp, whatsappDuvidas };
