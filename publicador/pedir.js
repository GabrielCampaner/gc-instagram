// Pede uma ação ao robô do GitHub e espera a resposta, sem abrir o site: grava pedido.json, envia, e lê ultimo_resultado.txt.
// Uso: node publicador/pedir.js conferir
//      node publicador/pedir.js teste L3-01      (prepara no Instagram sem publicar)
const fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const RAIZ = path.resolve(__dirname, "..");
const [acao = "conferir", id = ""] = process.argv.slice(2);
if (!["conferir", "teste", "midias", "insights"].includes(acao)) { console.error("Ações: conferir | teste <id> | midias | insights"); process.exit(1); }
const git = (...a) => execFileSync("git", a, { cwd: RAIZ, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
const ARQ_RES = path.join(RAIZ, "ultimo_resultado.txt");
const lerRes = () => fs.existsSync(ARQ_RES) ? fs.readFileSync(ARQ_RES, "utf8") : "";
const espera = ms => new Promise(r => setTimeout(r, ms));

(async () => {
    git("pull", "--rebase", "--autostash", "--quiet");
    const antes = lerRes();
    fs.writeFileSync(path.join(RAIZ, "pedido.json"), JSON.stringify({ acao, id, pedido_em: new Date().toISOString() }, null, 2) + "\n", "utf8");
    git("add", "pedido.json");
    git("commit", "-m", "Pedido: " + acao + (id ? " " + id : ""));
    git("push", "--quiet");
    console.log("Pedido enviado (" + acao + (id ? " " + id : "") + "). Esperando o robô...");
    for (let t = 0; t < 600; t += 15) {
        await espera(15000);
        try { git("pull", "--rebase", "--autostash", "--quiet"); } catch (e) { continue; }
        const res = lerRes();
        if (res && res !== antes) { console.log("\n" + res.trim()); return; }
    }
    console.error("Sem resposta em 10 minutos. Veja a aba Actions do repositório.");
    process.exit(1);
})().catch(e => { console.error(e.message); process.exit(1); });
