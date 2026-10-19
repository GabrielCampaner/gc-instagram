// Mostra o calendário: o que já saiu, o que está agendado, pendente ou com erro. Não precisa de token.
// Uso: node publicador/status.js [--tudo]   (sem --tudo, esconde o que já foi publicado)
const fs = require("fs"), path = require("path");
const RAIZ = path.resolve(__dirname, "..");
const cal = JSON.parse(fs.readFileSync(path.join(RAIZ, "calendario.json"), "utf8"));
const ARQ_PUB = path.join(RAIZ, "publicados.json");
const pub = fs.existsSync(ARQ_PUB) ? JSON.parse(fs.readFileSync(ARQ_PUB, "utf8")) : {};
const tudo = process.argv.includes("--tudo");
const hora = iso => new Date(iso).toLocaleString("pt-BR", { timeZone: "America/Fortaleza", weekday: "short", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
const cont = {};
console.log("Calendário " + (cal.ativo ? "ATIVO" : "DESLIGADO (\"ativo\": false, nada sai)") + "\n");
for (const p of [...cal.posts].sort((a, b) => new Date(a.quando) - new Date(b.quando))) {
    const r = pub[p.id] || {};
    const sit = r.media_id ? "publicado" : r.atrasado ? "atrasado" : r.erro ? "erro" : p.status;
    cont[sit] = (cont[sit] || 0) + 1;
    if (sit === "publicado" && !tudo) continue;
    const extra = sit === "publicado" ? r.permalink : r.erro ? r.erro : p.pendencia || "";
    console.log([p.id.padEnd(7), hora(p.quando).padEnd(18), p.tipo.padEnd(9), (p.midias.length + " mídia").padEnd(9), sit.padEnd(10), p.titulo].join(" ") + (extra ? "\n          " + extra : ""));
}
console.log("\n" + Object.entries(cont).map(([k, v]) => v + " " + k).join(" · "));
