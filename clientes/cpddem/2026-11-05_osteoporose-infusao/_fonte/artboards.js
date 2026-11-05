const { C, PH, page, L, txt, icon, shape, I } = require('./design');

const path = require('path');
const ASSET = { 'logo_horizontal.png': 'CPDDEM_logo_horizontal_transparente.png', 'logo_simbolo.png': 'CPDDEM_logo_simbolo_transparente.png',
  'arcos_azuis.png': 'CPDDEM_grafismo_arcos_azuis.png', 'arco_vermelho.png': 'CPDDEM_grafismo_arco_vermelho.png' };
const A = (f) => 'file://' + path.join(__dirname, '..', 'logo', ASSET[f]);
const idLinhas = `Diretor técnico-médico: ${PH.nome}\n${PH.crm} · ${PH.rqe} · ${PH.end}`;

// ---------- grafismo ----------
function arcos({ h, left, top, rot = 0, opacity = 1, name = 'Arcos azuis do símbolo' }) {
  const w = Math.round(h * 1230 / 1727);
  return `<img class="abs" src="${A('arcos_azuis.png')}" ${L(name, 'Grafismo', 'image')} style="left:${left}px;top:${top}px;width:${w}px;height:${h}px;transform:rotate(${rot}deg);opacity:${opacity}">`;
}
function arcoVermelho({ h, left, top, rot = 0, name = 'Arco vermelho do símbolo' }) {
  const w = Math.round(h * 1230 / 1727);
  return `<img class="abs" src="${A('arco_vermelho.png')}" ${L(name, 'Grafismo', 'image')} style="left:${left}px;top:${top}px;width:${w}px;height:${h}px;transform:rotate(${rot}deg)">`;
}
const fundo = () => `<div class="fundo" ${L('Fundo branco', 'Fundo', 'fill')}></div>`;
const logo = (w, style = '') => `<img src="${A('logo_horizontal.png')}" ${L('Logo CPDDEM (horizontal)', 'Logo', 'image')} style="display:block;width:${w}px;height:${Math.round(w * 1315 / 2458)}px;${style}">`;

// ---------- blocos ----------
function passos({ d2 = null, align = 'center', group = 'Passos', num = 72, numW = 82, tSize = 42, tLh = 48, dSize = 34, dLh = 42, gap = 26, desc = true, icons = false, iconSize = 64, card = false, cardPad = '24px 28px', tColor = C.graf }) {
  const dados = [
    ['1', 'Avaliação', 'Consulta médica para confirmar a indicação.', I.prancheta],
    ['2', 'Aplicação', d2 || 'Infusão na veia, feita na clínica com acompanhamento da equipe.', I.soro],
    ['3', 'Acompanhamento', 'Retorno e orientações depois da aplicação.', I.calendario],
  ];
  return dados.map(([n, t, d, ic], i) => {
    const g = `${group}/Passo ${n}`;
    const inner = `
      <div class="row" style="align-items:${align};position:relative;${card ? `padding:${cardPad};` : ''}">
        ${txt({ name: `Número ${n}`, group: g, text: n, size: num, lh: num, weight: 700, color: C.azul, style: `width:${numW}px;flex:none;` })}
        <div style="display:flex;flex-direction:column;${align === 'flex-start' ? `padding-top:${Math.round((num - tLh) / 2)}px` : ''}">
          ${txt({ name: `Título ${n}`, group: g, text: t, size: tSize, lh: tLh, weight: 700, color: tColor })}
          ${desc ? txt({ name: `Descrição ${n}`, group: g, text: d, size: dSize, lh: dLh, weight: 400, color: C.graf, style: 'margin-top:2px' }) : ''}
        </div>
        ${icons ? icon(`Ícone ${n}`, g, ic(iconSize, C.azul), `margin-left:auto`) : ''}
      </div>`;
    const cardBg = card ? shape(`Cartão ${n}`, g, `position:absolute;left:0;top:0;right:0;bottom:0;background:${C.gelo};border-radius:24px`) : '';
    return `<div style="position:relative;width:100%;margin-top:${i ? gap : 0}px">${cardBg}${inner}</div>`;
  }).join('');
}

function pagamento({ size = 36, lh = 44, iconSize = 48, group = 'CTA', mt = 0 }) {
  return `<div class="row" style="margin-top:${mt}px">
    ${icon('Ícone cartão', group, I.cartao(iconSize, C.azul), 'margin-right:16px')}
    ${txt({ name: 'Pagamento', group, text: 'Pagamento em até 12x no cartão de crédito', size, lh, weight: 600, color: C.graf })}
  </div>`;
}

// ---------- STORY 1080x1920 ----------
function story() {
  const inner = `
  ${fundo()}
  ${arcos({ h: 900, left: 742, top: -330 })}
  <div class="col" style="left:88px;top:250px;width:904px">
    ${logo(320)}
    ${txt({ name: 'Identificação do diretor técnico-médico', group: 'Rodapé', text: idLinhas, size: 26, lh: 34, style: 'margin-top:16px' })}
    ${txt({ name: 'Chamada', group: 'Textos', text: 'SAÚDE ÓSSEA', size: 34, lh: 40, weight: 600, italic: true, color: C.verm, track: 0.08, style: 'margin-top:44px' })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'Infusão para\nosteoporose', size: 122, lh: 116, weight: 800, color: C.azul, track: -0.005, style: 'margin-top:10px' })}
    ${txt({ name: 'Subtítulo', group: 'Textos', text: 'Tratamento por via intravenosa, aplicado\nno CPDDEM com avaliação e indicação médica.', size: 44, lh: 57, style: 'margin-top:22px' })}
    <div style="width:100%;margin-top:30px">${passos({ numW: 76, tSize: 42, tLh: 48, dSize: 34, dLh: 42, gap: 20, d2: 'Infusão na veia, feita na clínica\ncom acompanhamento da equipe.' })}</div>
    ${pagamento({ mt: 26 })}
    <div class="row" style="margin-top:24px">
      ${icon('Ícone WhatsApp', 'CTA', I.whatsapp(58, C.azulEsc), 'margin-right:18px')}
      ${txt({ name: 'Botão: Agende sua avaliação', group: 'CTA', text: 'Agende sua avaliação', size: 48, lh: 56, weight: 700, color: C.azulEsc })}
    </div>
    <div class="guide" ${L('Área da figurinha de link (700 × 120)', 'Guias', 'guide')} style="margin-top:12px;width:700px;height:120px"></div>
  </div>
  <div class="guide abs" ${L('Área livre do topo (250 px)', 'Guias', 'guide')} style="left:0;top:0;width:1080px;height:250px"></div>
  <div class="guide abs" ${L('Área livre da base (270 px)', 'Guias', 'guide')} style="left:0;top:1650px;width:1080px;height:270px"></div>
  `;
  return { name: 'Story', w: 1080, h: 1920, html: page(1080, 1920, inner) };
}


// ---------- WHATSAPP 1080x1350 ----------
function whatsapp() {
  const inner = `
  ${fundo()}
  ${arcos({ h: 660, left: 818, top: -250 })}
  ${shape('Faixa do rodapé', 'Rodapé', `position:absolute;left:0;top:1232px;width:1080px;height:118px;background:${C.gelo}`)}
  <div class="col" style="left:88px;top:68px;width:904px">
    ${logo(270)}
    ${txt({ name: 'Chamada', group: 'Textos', text: 'SAÚDE ÓSSEA', size: 34, lh: 40, weight: 600, italic: true, color: C.verm, track: 0.08, style: 'margin-top:34px' })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'Infusão para\nosteoporose', size: 106, lh: 102, weight: 800, color: C.azul, track: -0.005, style: 'margin-top:8px' })}
    ${txt({ name: 'Subtítulo', group: 'Textos', text: 'Tratamento por via intravenosa, aplicado\nno CPDDEM com avaliação e indicação médica.', size: 40, lh: 52, style: 'margin-top:20px' })}
    <div style="width:100%;margin-top:26px">${passos({ num: 64, numW: 68, tSize: 38, tLh: 44, dSize: 32, dLh: 40, gap: 14, d2: 'Infusão na veia, feita na clínica\ncom acompanhamento da equipe.' })}</div>
    ${pagamento({ size: 34, lh: 42, iconSize: 46, mt: 22 })}
    <div class="row" style="margin-top:26px;width:100%">
      <div class="row" style="position:relative;height:100px;padding:0 44px 0 36px">
        ${shape('Botão (fundo)', 'CTA', `position:absolute;left:0;top:0;width:100%;height:100%;background:${C.azulEsc};border-radius:50px`)}
        ${icon('Ícone WhatsApp', 'CTA', I.whatsapp(50, '#FFFFFF'), 'position:relative;margin-right:16px')}
        ${txt({ name: 'Botão: Agende sua avaliação', group: 'CTA', text: 'Agende sua avaliação', size: 44, lh: 52, weight: 700, color: '#FFFFFF', style: 'position:relative' })}
      </div>
      ${txt({ name: 'Número do WhatsApp', group: 'CTA', text: PH.fone, size: 40, lh: 48, weight: 700, color: C.graf, style: 'margin-left:30px' })}
    </div>
  </div>
  ${txt({ name: 'Identificação do diretor técnico-médico', group: 'Rodapé', text: `CPDDEM · ${PH.endCompleto}\nDiretor técnico-médico: ${PH.nome} · ${PH.crm} · ${PH.rqe}`, size: 26, lh: 34, style: 'position:absolute;left:88px;top:1257px' })}
  `;
  return { name: 'WhatsApp', w: 1080, h: 1350, html: page(1080, 1350, inner) };
}

// ---------- SEQUÊNCIA DE 3 STORIES ----------
function cabecalhoStory(logoW = 380) {
  return `${logo(logoW)}
    ${txt({ name: 'Identificação do diretor técnico-médico', group: 'Rodapé', text: idLinhas, size: 26, lh: 34, style: 'margin-top:18px' })}`;
}
const guiasStory = () => `
  <div class="guide abs" ${L('Área livre do topo (250 px)', 'Guias', 'guide')} style="left:0;top:0;width:1080px;height:250px"></div>
  <div class="guide abs" ${L('Área livre da base (270 px)', 'Guias', 'guide')} style="left:0;top:1650px;width:1080px;height:270px"></div>`;

function seq1() {
  const inner = `
  ${fundo()}
  ${arcos({ h: 1000, left: 700, top: -360 })}
  <div class="col" style="left:88px;top:250px;width:904px">
    ${cabecalhoStory()}
  </div>
  <div class="col" style="left:88px;top:790px;width:904px">
    ${txt({ name: 'Chamada', group: 'Textos', text: 'SAÚDE ÓSSEA', size: 40, lh: 48, weight: 600, italic: true, color: C.verm, track: 0.08 })}
    ${txt({ name: 'Headline', group: 'Textos', text: 'Osteoporose\ntem tratamento\npor infusão', size: 140, lh: 134, weight: 800, color: C.azul, track: -0.005, style: 'margin-top:14px' })}
    ${shape('Fio vermelho', 'Textos', `width:96px;height:6px;background:${C.verm};border-radius:3px;margin-top:56px`)}
    <div class="row" style="margin-top:44px">
      ${txt({ name: 'Convite: veja como funciona', group: 'CTA', text: 'Veja como funciona no CPDDEM', size: 48, lh: 56, weight: 600, color: C.azulEsc })}
      ${icon('Seta', 'CTA', I.seta(52, C.azulEsc), 'margin-left:16px')}
    </div>
  </div>
  ${guiasStory()}`;
  return { name: 'Sequência 1 de 3', w: 1080, h: 1920, html: page(1080, 1920, inner) };
}

function seq2() {
  const inner = `
  ${fundo()}
  ${arcos({ h: 760, left: 800, top: -300 })}
  <div class="col" style="left:88px;top:250px;width:904px">
    ${cabecalhoStory()}
    ${txt({ name: 'Título: Como funciona', group: 'Textos', text: 'Como funciona', size: 108, lh: 108, weight: 800, color: C.azul, track: -0.005, style: 'margin-top:96px' })}
    <div style="width:100%;margin-top:52px">${passos({ num: 96, numW: 92, tSize: 50, tLh: 56, dSize: 40, dLh: 50, gap: 28, card: true, cardPad: '34px 36px 34px 36px', icons: true, iconSize: 72,
      d2: 'Infusão na veia, feita na clínica\ncom acompanhamento da equipe.' }).replace('Consulta médica para confirmar a indicação.', 'Consulta médica para\nconfirmar a indicação.').replace('Retorno e orientações depois da aplicação.', 'Retorno e orientações\ndepois da aplicação.')}</div>
  </div>
  ${guiasStory()}`;
  return { name: 'Sequência 2 de 3', w: 1080, h: 1920, html: page(1080, 1920, inner) };
}

function seq3() {
  const inner = `
  ${fundo()}
  ${arcos({ h: 760, left: 800, top: -300 })}
  <div class="col" style="left:88px;top:250px;width:904px">
    ${cabecalhoStory()}
  </div>
  <div class="col" style="left:88px;top:780px;width:904px">
    ${icon('Ícone WhatsApp grande', 'CTA', I.whatsapp(96, C.azul))}
    ${txt({ name: 'Headline: Agende sua avaliação', group: 'CTA', text: 'Agende sua\navaliação', size: 140, lh: 134, weight: 800, color: C.azul, track: -0.005, style: 'margin-top:28px' })}
    <div class="guide" ${L('Área da figurinha de link (700 × 120)', 'Guias', 'guide')} style="margin-top:36px;width:700px;height:120px"></div>
    ${txt({ name: 'Número do WhatsApp', group: 'CTA', text: 'WhatsApp ' + PH.fone, size: 44, lh: 52, weight: 700, color: C.graf, style: 'margin-top:28px' })}
    ${shape('Fio vermelho', 'Textos', `width:96px;height:6px;background:${C.verm};border-radius:3px;margin-top:56px`)}
    ${pagamento({ size: 38, lh: 46, iconSize: 52, mt: 40 })}
  </div>
  ${guiasStory()}`;
  return { name: 'Sequência 3 de 3', w: 1080, h: 1920, html: page(1080, 1920, inner) };
}

module.exports = { story, whatsapp, seq1, seq2, seq3 };

