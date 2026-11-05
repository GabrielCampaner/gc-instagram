#!/usr/bin/env python3
"""Gera a capa 1080x1920 de um Reel da série a partir de um quadro do vídeo.

Uso:  python3 producao/pipeline/capa.py producao/lote-teste/montagem/capas.json
Cada capa: imagem de fundo, corte, letreiro de câmera (CI) ou selo (PO), caixa de detecção
em volta do doutor e a manchete grande dentro da faixa central 3:4 (aparece inteira na grade do perfil).
"""
import base64, io, json, os, sys
from PIL import Image
import subprocess, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;position:relative;overflow:hidden;background:#000;font-family:'Inter Display','Inter',sans-serif}
.bg{position:absolute;inset:0;background:url(data:image/jpeg;base64,__BG__) center/cover;filter:saturate(.82) contrast(.96)}
.bot{position:absolute;left:0;right:0;top:880px;height:1040px;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.62) 32%,rgba(0,0,0,.86))}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 55%,rgba(0,0,0,0) 45%,rgba(0,0,0,.55) 100%)}
.top{position:absolute;left:0;right:0;top:0;height:640px;background:linear-gradient(rgba(0,0,0,.82),rgba(0,0,0,.55) 70%,rgba(0,0,0,0))}
.hud{position:absolute;left:0;right:0;top:0;height:160px;background:rgba(0,0,0,.4);font-family:'JetBrains Mono',monospace;font-weight:800;color:#EDEFE6;font-size:38px}
.hud .rec{position:absolute;left:44px;top:50px;color:#FF3B4E;font-size:44px}
.hud .cam{position:absolute;left:262px;top:56px}
.hud .dia{position:absolute;right:44px;top:56px}
.hud .hora{position:absolute;right:44px;top:104px}
.hud .selo{position:absolute;left:44px;top:112px;font-size:27px;opacity:.85}
.tag{position:absolute;left:70px;top:__Y0__px;background:#FFE14D;color:#111;font-weight:900;font-size:30px;letter-spacing:3px;padding:10px 18px;border-radius:6px}
.kick{position:absolute;left:70px;right:70px;top:__Y1__px;color:#fff;font-weight:600;font-size:38px;line-height:1.2;text-shadow:0 2px 8px rgba(0,0,0,.6)}
.tit{position:absolute;left:66px;right:60px;top:__Y2__px;color:#fff;font-weight:900;font-size:__TAM__px;line-height:.98;letter-spacing:-1px;text-transform:uppercase;text-shadow:0 4px 18px rgba(0,0,0,.65)}
.tit b{color:#FFE14D;font-weight:900}
.box{position:absolute;border:5px solid #FFE14D;box-shadow:0 0 0 2px rgba(0,0,0,.35)}
.box span{position:absolute;left:-5px;top:-50px;background:#FFE14D;color:#111;font-family:'JetBrains Mono',monospace;font-weight:800;font-size:26px;padding:6px 12px;white-space:nowrap}
.ia{position:absolute;right:44px;bottom:300px;color:#fff;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:24px;background:rgba(0,0,0,.45);padding:6px 12px;border-radius:4px}
</style></head><body>
<div class="bg"></div><div class="vig"></div>__GRAD__
__HUD__
<div class="tag">__TAG__</div>
<div class="kick">__KICK__</div>
<div class="tit">__TIT__</div>
__BOX__
</body></html>"""


def fundo(c):
    im = Image.open(os.path.join(RAIZ, c["imagem"])).convert("RGB")
    im = im.resize((1080, round(im.height * 1080 / im.width)))
    if c.get("crop"):  # mesmo corte do vídeo, em proporção do quadro 1080x1920
        x, y, w, h = c["crop"]
        im = im.resize((1080, 1920)).crop((x, y, x + w, y + h)).resize((1080, 1920))
    else:
        im = im.resize((1080, 1920))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode()


def html(c):
    hud = ""
    if c.get("hud"):
        h = c["hud"]
        hud = (f'<div class="hud"><div class="rec">● REC</div><div class="cam">{h["cam"]}</div>'
               f'<div class="dia">{h["dia"]}</div><div class="hora">{h["hora"]}</div>'
               f'<div class="selo">SIMULAÇÃO · IA</div></div>')
    box = ""
    if c.get("caixa"):
        x0, y0, x1, y1, rot = c["caixa"]
        box = (f'<div class="box" style="left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px">'
               f'<span>{rot}</span></div>')
    if not c.get("hud"):
        box += '<div class="ia">SIMULAÇÃO · IA</div>'
    tit = "<br>".join(c["titulo"])
    return (HTML.replace("__BG__", fundo(c)).replace("__HUD__", hud).replace("__TAG__", c["tag"])
            .replace("__KICK__", c["kicker"]).replace("__TIT__", tit).replace("__BOX__", box)
            .replace("__GRAD__", '<div class="bot"></div><div class="top" style="height:260px"></div>' if c.get("baixo") else '<div class="top"></div>')
            .replace("__TAM__", str(c.get("tam", 112))).replace("__Y0__", str(c.get("y", 300)))
            .replace("__Y1__", str(c.get("y", 300) + 72)).replace("__Y2__", str(c.get("y", 300) + 140)))


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    saida = os.path.join(RAIZ, spec.get("saida", "producao/lote-teste/saida"))
    os.makedirs(saida, exist_ok=True)
    tmp = tempfile.mkdtemp()
    pares = []
    for c in spec["capas"]:
        h = os.path.join(tmp, c["id"] + ".html")
        open(h, "w", encoding="utf-8").write(html(c))
        pares.append([h, os.path.join(saida, f"{c['id']}_capa.jpg")])
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});"
          f"for(const [h,o] of {json.dumps(pares)}){{await p.goto('file://'+h);await p.waitForTimeout(300);"
          "await p.screenshot({path:o,type:'jpeg',quality:92});console.log(o);}await b.close();})()")
    subprocess.run(["node", "-e", js], check=True)
