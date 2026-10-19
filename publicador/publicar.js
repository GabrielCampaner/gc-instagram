// Publicador do Instagram da GC. Roda no GitHub Actions a cada 10 minutos e publica os posts do calendario.json que já venceram,
// pela API oficial do Instagram (login do Instagram, app próprio na Meta). Registra cada publicação em publicados.json.
// Ações (variável ACAO):
//   publicar  (padrão do agendamento) publica o que venceu, se o calendário estiver com "ativo": true
//   conferir  mostra a conta, a cota do dia e os últimos posts, sem publicar
//   teste     prepara o post POST_ID no Instagram (imagens, legenda, carrossel) e confere, sem publicar
// Variáveis: IG_TOKEN (segredo do GitHub), MIDIA_BASE (endereço público da pasta do repositório), IG_API_VERSAO (opcional).
const fs = require("fs"), path = require("path");
const RAIZ = path.resolve(__dirname, "..");
const API = "https://graph.instagram.com/" + (process.env.IG_API_VERSAO || "v25.0");
const TOKEN = process.env.IG_TOKEN || "";
const ACAO = process.env.ACAO || "publicar";
const POST_ID = (process.env.POST_ID || "").trim();
const BASE = (process.env.MIDIA_BASE || "").replace(/\/?$/, "/");
const ATRASO_MAX_H = 6, TENTATIVAS_MAX = 3;

const cal = JSON.parse(fs.readFileSync(path.join(RAIZ, "calendario.json"), "utf8"));
const ARQ_PUB = path.join(RAIZ, "publicados.json");
const pub = fs.existsSync(ARQ_PUB) ? JSON.parse(fs.readFileSync(ARQ_PUB, "utf8")) : {};
const salvarPub = () => fs.writeFileSync(ARQ_PUB, JSON.stringify(pub, null, 2) + "\n", "utf8");
const espera = ms => new Promise(r => setTimeout(r, ms));
const hora = iso => new Date(iso).toLocaleString("pt-BR", { timeZone: "America/Fortaleza", dateStyle: "short", timeStyle: "short" });

async function ig(metodo, rota, params = {}) {
    const corpo = new URLSearchParams({ ...params, access_token: TOKEN });
    const r = metodo === "GET" ? await fetch(API + rota + "?" + corpo) : await fetch(API + rota, { method: "POST", body: corpo });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || j.error) {
        const e = j.error || {};
        throw new Error("Instagram " + r.status + " em " + rota + ": " + (e.message || JSON.stringify(j).slice(0, 300)) + (e.error_user_msg ? " (" + e.error_user_msg + ")" : ""));
    }
    return j;
}
async function aguardarPronto(id, limiteS) {
    for (let t = 0; t <= limiteS; t += 5) {
        const s = await ig("GET", "/" + id, { fields: "status_code,status" });
        if (s.status_code === "FINISHED") return;
        if (s.status_code === "ERROR" || s.status_code === "EXPIRED") throw new Error("o Instagram recusou a mídia (" + s.status_code + "): " + (s.status || ""));
        await espera(5000);
    }
    throw new Error("a mídia " + id + " não ficou pronta em " + limiteS + " s");
}
const url = m => BASE + m.split("/").map(encodeURIComponent).join("/");
const ehVideo = m => /\.(mp4|mov)$/i.test(m);

// Monta o post no Instagram (container) e espera ele ficar pronto. Devolve o id para publicar.
async function preparar(p) {
    if (!BASE || BASE === "/") throw new Error("falta MIDIA_BASE (endereço público das mídias)");
    if (!p.midias || !p.midias.length) throw new Error("post sem mídia");
    let c;
    if (p.tipo === "story") {
        const m = p.midias[0];
        c = await ig("POST", "/me/media", ehVideo(m) ? { media_type: "STORIES", video_url: url(m) } : { media_type: "STORIES", image_url: url(m) });
        await aguardarPronto(c.id, ehVideo(m) ? 600 : 120);
        return c.id;
    }
    if (p.tipo === "reels") {
        c = await ig("POST", "/me/media", { media_type: "REELS", video_url: url(p.midias[0]), caption: p.legenda, share_to_feed: "true" });
        await aguardarPronto(c.id, 600);
        return c.id;
    }
    if (p.midias.length === 1) {
        c = await ig("POST", "/me/media", { image_url: url(p.midias[0]), caption: p.legenda });
        await aguardarPronto(c.id, 120);
        return c.id;
    }
    const filhos = [];
    for (const m of p.midias) {
        const f = await ig("POST", "/me/media", ehVideo(m) ? { media_type: "VIDEO", video_url: url(m), is_carousel_item: "true" } : { image_url: url(m), is_carousel_item: "true" });
        filhos.push({ id: f.id, video: ehVideo(m) });
    }
    for (const f of filhos) await aguardarPronto(f.id, f.video ? 600 : 120);
    c = await ig("POST", "/me/media", { media_type: "CAROUSEL", children: filhos.map(f => f.id).join(","), caption: p.legenda });
    await aguardarPronto(c.id, 120);
    return c.id;
}
// Se a mesma legenda já está entre os últimos posts, não publica de novo (proteção contra registro perdido).
async function jaNoFeed(p) {
    const alvo = (p.legenda || "").trim();
    if (!alvo || p.tipo === "story") return null;
    const r = await ig("GET", "/me/media", { fields: "id,caption,permalink,timestamp", limit: "15" });
    return (r.data || []).find(m => (m.caption || "").trim() === alvo) || null;
}

async function conferir() {
    const eu = await ig("GET", "/me", { fields: "id,username,account_type" });
    console.log("Conta: @" + eu.username + " (" + eu.account_type + ", id " + eu.id + ")");
    const lim = await ig("GET", "/me/content_publishing_limit", { fields: "quota_usage,config" }).catch(e => ({ erro: e.message }));
    const d = (lim.data || [])[0];
    console.log(d ? "Cota de publicação: " + d.quota_usage + " de " + ((d.config || {}).quota_total || "?") + " nas últimas 24 h" : "Cota: " + (lim.erro || "sem resposta"));
    const ult = await ig("GET", "/me/media", { fields: "caption,permalink,timestamp", limit: "5" });
    console.log("Últimos posts:");
    for (const m of ult.data || []) console.log("  " + hora(m.timestamp) + "  " + m.permalink + "  " + (m.caption || "").split("\n")[0].slice(0, 60));
    const ag = cal.posts.filter(p => p.status === "agendado" && !(pub[p.id] || {}).media_id);
    console.log("Calendário " + (cal.ativo ? "ATIVO" : "desligado (\"ativo\": false)") + ": " + ag.length + " agendados, " + cal.posts.filter(p => p.status === "pendente").length + " pendentes, " + Object.values(pub).filter(r => r.media_id).length + " publicados.");
    if (BASE && BASE !== "/" && cal.posts[0]) {
        const teste = url(cal.posts[0].midias[0]), r = await fetch(teste, { method: "HEAD" });
        console.log("Mídia pública: " + r.status + " " + (r.headers.get("content-type") || "") + "  " + teste);
    }
}

async function publicar() {
    if (!cal.ativo) { console.log("Calendário desligado (\"ativo\": false). Nada publicado."); return; }
    const agora = Date.now();
    const vencidos = cal.posts.filter(p => p.status === "agendado" && !(pub[p.id] || {}).media_id && new Date(p.quando) <= agora)
        .sort((a, b) => new Date(a.quando) - new Date(b.quando));
    if (!vencidos.length) {
        const prox = cal.posts.filter(p => p.status === "agendado" && !(pub[p.id] || {}).media_id && new Date(p.quando) > agora).sort((a, b) => new Date(a.quando) - new Date(b.quando))[0];
        console.log("Nada para publicar agora." + (prox ? " Próximo: " + prox.id + " em " + hora(prox.quando) + "." : ""));
        return;
    }
    let falhas = 0;
    for (const p of vencidos) {
        const reg = pub[p.id] || (pub[p.id] = { tentativas: 0 });
        const atrasoH = (agora - new Date(p.quando)) / 3600e3;
        if (atrasoH > ATRASO_MAX_H) {
            if (!reg.atrasado) {
                reg.atrasado = true;
                reg.erro = "passou " + Math.round(atrasoH) + " h do horário; não publiquei para não atropelar o calendário";
                salvarPub(); falhas++;
                console.error("Atrasado: " + p.id + " (" + reg.erro + ")");
            }
            continue;
        }
        if (reg.tentativas >= TENTATIVAS_MAX) continue;
        try {
            reg.tentativas++;
            const existente = await jaNoFeed(p);
            if (existente) {
                Object.assign(reg, { media_id: existente.id, permalink: existente.permalink, publicado_em: existente.timestamp, obs: "já estava no feed" });
            } else {
                const criacao = await preparar(p);
                const m = await ig("POST", "/me/media_publish", { creation_id: criacao });
                const info = await ig("GET", "/" + m.id, { fields: "permalink,timestamp" }).catch(() => ({}));
                Object.assign(reg, { media_id: m.id, permalink: info.permalink || "", publicado_em: info.timestamp || new Date().toISOString() });
            }
            delete reg.erro;
            salvarPub();
            console.log("Publicado: " + p.id + " " + p.titulo + "  " + (reg.permalink || reg.media_id));
        } catch (e) {
            reg.erro = e.message;
            salvarPub(); falhas++;
            console.error("Falhou " + p.id + " (tentativa " + reg.tentativas + " de " + TENTATIVAS_MAX + "): " + e.message);
        }
    }
    if (falhas) process.exitCode = 1;   // o GitHub manda e-mail quando a execução falha
}

(async () => {
    if (!TOKEN) {
        if (ACAO === "publicar") { console.log("Sem o segredo IG_TOKEN ainda. Nada a fazer."); return; }
        throw new Error("Falta o segredo IG_TOKEN (GitHub > Settings > Secrets and variables > Actions).");
    }
    if (ACAO === "conferir") return conferir();
    if (ACAO === "teste") {
        const p = cal.posts.find(x => x.id === POST_ID);
        if (!p) throw new Error("Post " + (POST_ID || "(vazio)") + " não está no calendário.");
        console.log("Preparando " + p.id + " (" + p.tipo + ", " + p.midias.length + " mídias) sem publicar...");
        const id = await preparar(p);
        console.log("OK: o Instagram aceitou as imagens e a legenda de " + p.id + " (container " + id + "). Nada foi publicado; o preparo expira sozinho em 24 h.");
        return;
    }
    return publicar();
})().catch(e => { console.error(e.message); process.exit(1); });
