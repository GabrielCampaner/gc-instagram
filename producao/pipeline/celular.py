#!/usr/bin/env python3
"""Tela de celular desenhada por nós (conversa de mensagens ou notificação), com fundo transparente,
para sobrepor ao vídeo na montagem. O Veo nunca desenha texto de tela: sai torto e com nomes reais.

Uso:  python3 producao/pipeline/celular.py producao/lote-teste/montagem/CI-15_chat.json
Grava um .mov com transparência (qtrle) no caminho de "saida" do JSON e uma prévia .png do último estado.

JSON:
  {"saida": "...mov", "dur": 9, "tipo": "chat" | "notificacao",
   "contato": "Clínica Venna", "status": "online", "x": 190, "y": 470, "largura": 700, "altura": 1080,
   "eventos": [{"t": 0, "tipo": "dia", "txt": "TERÇA"},
               {"t": 0, "tipo": "eu", "txt": "...", "hora": "14:47"},
               {"t": 2.4, "tipo": "ela", "txt": "...", "hora": "19:27"},
               {"t": 3.0, "tipo": "ler"},                       # as minhas viram ✓✓ azul
               {"t": 6.8, "tipo": "digitando", "txt": "Vou passar aí."}]}   # texto na caixa
  notificação: {"tipo": "notificacao", "app": "Mensagens", "titulo": "...", "txt": "...", "de": 0.0, "y": 190}
"""
import html as H, json, os, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FPS = 30

CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;background:transparent;overflow:hidden;font-family:'Inter','Helvetica Neue',Arial,sans-serif}
.cel{position:absolute;border-radius:64px;background:#0d0d0f;padding:18px;box-shadow:0 30px 80px rgba(0,0,0,.55),0 0 0 3px #2b2b30 inset}
.tela{position:relative;width:100%;height:100%;border-radius:48px;overflow:hidden;background:#ece5dd;display:flex;flex-direction:column}
.barra{height:46px;background:#0b5e55;color:#fff;font-size:22px;font-weight:600;display:flex;justify-content:space-between;align-items:center;padding:0 34px}
.topo{background:#0b5e55;color:#fff;display:flex;align-items:center;gap:18px;padding:14px 24px 18px}
.av{width:72px;height:72px;border-radius:50%;background:#e9d8c4;color:#7a5a3a;font-weight:800;font-size:34px;display:flex;align-items:center;justify-content:center}
.nome{font-size:31px;font-weight:700;line-height:1.1}.st{font-size:22px;opacity:.85}
.msgs{flex:1;min-height:0;overflow:hidden;display:flex;flex-direction:column;justify-content:flex-end;gap:10px;padding:18px 20px 14px}
.dia{align-self:center;background:#e1f2fb;color:#4a5a63;font-size:21px;font-weight:600;padding:7px 18px;border-radius:12px;margin:8px 0}
.b{max-width:80%;padding:12px 16px 10px;border-radius:18px;font-size:29px;line-height:1.28;color:#111;box-shadow:0 1px 1px rgba(0,0,0,.12);position:relative}
.eu{align-self:flex-end;background:#d9fdd3;border-top-right-radius:6px}
.ela{align-self:flex-start;background:#fff;border-top-left-radius:6px}
.h{display:inline-block;margin-left:14px;font-size:19px;color:#667781;vertical-align:-4px;white-space:nowrap}
.ck{font-size:20px;letter-spacing:-6px;margin-left:6px;color:#8696a0}.ck.az{color:#34b7f1}
.cx{display:flex;align-items:center;gap:14px;padding:12px 16px 22px;background:#f0f0f0}
.in{flex:1;background:#fff;border-radius:34px;padding:16px 24px;font-size:28px;color:#111;min-height:62px}
.in.vz{color:#8696a0}
.bt{width:64px;height:64px;border-radius:50%;background:#0b8f7a;color:#fff;font-size:30px;display:flex;align-items:center;justify-content:center}
.not{position:absolute;left:40px;right:40px;background:rgba(245,245,247,.97);border-radius:36px;padding:24px 28px;display:flex;gap:22px;align-items:center;box-shadow:0 18px 50px rgba(0,0,0,.45)}
.ic{width:84px;height:84px;border-radius:20px;background:#25a87a;color:#fff;font-size:44px;display:flex;align-items:center;justify-content:center;flex:none}
.nt{flex:1}.na{font-size:22px;color:#555;display:flex;justify-content:space-between;text-transform:uppercase;letter-spacing:1px}
.nn{font-size:30px;font-weight:700;color:#111;margin-top:4px}.nx{font-size:30px;color:#222;margin-top:2px}"""


def estado_chat(s, t):
    ev = [e for e in s["eventos"] if e["t"] <= t + 1e-6]
    lidas = max([e["t"] for e in ev if e["tipo"] == "ler"], default=-1)
    corpo, caixa = [], ""
    for e in ev:
        if e["tipo"] == "dia":
            corpo.append(f'<div class="dia">{H.escape(e["txt"])}</div>')
        elif e["tipo"] in ("eu", "ela"):
            ck = ""
            if e["tipo"] == "eu":
                az = " az" if e["t"] <= lidas else ""
                ck = f'<span class="ck{az}">✓✓</span>'
            corpo.append(f'<div class="b {e["tipo"]}">{H.escape(e["txt"])}<span class="h">{e["hora"]}{ck}</span></div>')
        elif e["tipo"] == "digitando":
            caixa = e["txt"]
        elif e["tipo"] == "enviou":
            caixa = ""
    caixa_html = (f'<div class="in">{H.escape(caixa)}|</div>' if caixa else '<div class="in vz">Mensagem</div>')
    tela = (f'<div class="barra"><span>{s.get("relogio", "11:44")}</span><span>●●● 5G ▮</span></div>'
            f'<div class="topo"><span style="font-size:34px">‹</span><div class="av">{s.get("inicial", s["contato"][0])}</div>'
            f'<div><div class="nome">{H.escape(s["contato"])}</div><div class="st">{H.escape(s.get("status", "online"))}</div></div></div>'
            f'<div class="msgs">{"".join(corpo)}</div>'
            f'<div class="cx">{caixa_html}<div class="bt">➤</div></div>')
    if s.get("tela_cheia"):  # a tela do celular ocupando o quadro inteiro (9:16), mesma diagramação, ampliada
        L = s.get("largura_tela", 564)
        return (f'<div style="position:absolute;left:0;top:0;width:{L}px;height:{L * 16 / 9:.1f}px;'
                f'transform:scale({1080 / L:.5f});transform-origin:0 0"><div class="tela" style="border-radius:0">{tela}</div></div>')
    k = s.get("escala", 1)
    return (f'<div class="cel" style="left:{s["x"]}px;top:{s["y"]}px;width:{s["largura"]}px;height:{s["altura"]}px;'
            f'transform:scale({k});transform-origin:0 0">'
            f'<div class="tela">{tela}</div></div>')


def estado_notif(s, t):
    if t < s.get("de", 0):
        return ""
    return (f'<div class="not" style="top:{s.get("y", 190)}px"><div class="ic">✉</div><div class="nt">'
            f'<div class="na"><span>{H.escape(s.get("app", "Mensagens"))}</span><span>agora</span></div>'
            f'<div class="nn">{H.escape(s["titulo"])}</div><div class="nx">{H.escape(s["txt"])}</div></div></div>')


def tempos(s):
    if s["tipo"] == "notificacao":
        return sorted({0.0, float(s.get("de", 0))})
    return sorted({0.0} | {float(e["t"]) for e in s["eventos"]})


def render(arq):
    s = json.load(open(arq))
    saida = os.path.join(RAIZ, s["saida"])
    tmp = tempfile.mkdtemp()
    ts = tempos(s)
    pares = []
    for k, t in enumerate(ts):
        corpo = estado_notif(s, t) if s["tipo"] == "notificacao" else estado_chat(s, t)
        h = os.path.join(tmp, f"e{k}.html")
        open(h, "w", encoding="utf-8").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{corpo}</body></html>')
        pares.append([h, os.path.join(tmp, f"e{k}.png")])
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});"
          f"for(const [h,o] of {json.dumps(pares)}){{await p.goto('file://'+h);await p.waitForTimeout(150);"
          "await p.screenshot({path:o,omitBackground:true});}await b.close();})()")
    subprocess.run(["node", "-e", js], check=True)
    # cada estado dura até o próximo; o último vai até o fim
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        for k, t in enumerate(ts):
            fim = ts[k + 1] if k + 1 < len(ts) else s["dur"]
            f.write(f"file '{pares[k][1]}'\nduration {max(fim - t, 1 / FPS):.3f}\n")
        f.write(f"file '{pares[-1][1]}'\n")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-vf", f"fps={FPS},format=argb",
                    "-t", str(s["dur"]), "-c:v", "qtrle", saida], check=True)
    prev = os.path.splitext(saida)[0] + "_previa.png"
    subprocess.run(["cp", pares[-1][1], prev], check=True)
    print(saida)
    if s.get("encolher"):
        encolher(s, tmp)


def encolher(s, tmp):
    """Transição: a tela cheia (último estado da conversa) diminui até virar o celular na mão, na posição de "encolher"."""
    e = s["encolher"]
    L = s.get("largura_tela", 564)
    s0 = 1080 / L
    n = max(int(round(e.get("dur", 0.6) * FPS)), 2)
    estado = estado_chat(dict(s, tela_cheia=False, x=0, y=0, largura=L + 36, altura=round(L * 16 / 9) + 36), s["dur"])
    pares = []
    for i in range(n + 1):
        u = i / n
        p = u * u * (3 - 2 * u)  # entra e sai suave
        k = e.get("escala", 1)
        esc = s0 + (k - s0) * p
        tx = -18 * s0 + (e["x"] + 18 * s0) * p
        ty = -18 * s0 + (e["y"] + 18 * s0) * p  # (tx, ty) é o canto do aparelho; a tela fica 18*esc para dentro
        raio = 48 * p
        corpo = (f'<div style="position:absolute;left:0;top:0;transform:translate({tx:.2f}px,{ty:.2f}px) scale({esc:.5f});'
                 f'transform-origin:0 0"><style>.tela{{border-radius:{raio:.1f}px!important}}.cel{{box-shadow:0 30px 80px '
                 f'rgba(0,0,0,{0.55 * p:.2f})}}</style>{estado}</div>')
        h = os.path.join(tmp, f"enc{i}.html")
        open(h, "w", encoding="utf-8").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{corpo}</body></html>')
        pares.append([h, os.path.join(tmp, f"enc{i:03d}.png")])
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});"
          f"for(const [h,o] of {json.dumps(pares)}){{await p.goto('file://'+h);await p.waitForTimeout(60);"
          "await p.screenshot({path:o,omitBackground:true});}await b.close();})()")
    subprocess.run(["node", "-e", js], check=True)
    saida = os.path.join(RAIZ, e["saida"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(tmp, "enc%03d.png"),
                    "-vf", "format=argb", "-c:v", "qtrle", saida], check=True)
    print(saida)


def sons(pasta):
    """Sons de tela sintetizados (grátis): mensagem enviada/recebida e notificação."""
    os.makedirs(pasta, exist_ok=True)
    feitos = {
        "som_msg_eu.mp3": "0.5*sin(2*PI*(1250-500*t)*t)*exp(-38*t)",
        "som_msg_ela.mp3": "0.5*sin(2*PI*(820+300*t)*t)*exp(-30*t)",
        "som_notif.mp3": "0.45*(sin(2*PI*1318*t)*exp(-9*t)*lt(t\\,0.18)+sin(2*PI*1760*(t-0.16))*exp(-7*(t-0.16))*gte(t\\,0.16))",
    }
    for nome, expr in feitos.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d=0.7",
                        "-ac", "1", "-b:a", "128k", os.path.join(pasta, nome)], check=True)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        render(a)
        sons(os.path.dirname(os.path.join(RAIZ, json.load(open(a))["saida"])))
