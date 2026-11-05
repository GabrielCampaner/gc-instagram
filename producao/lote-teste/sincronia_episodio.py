#!/usr/bin/env python3
"""Sincronia labial de um episódio inteiro (sync-3 pelo fal.ai), a partir do JSON de montagem.

Uso (precisa de FAL_KEY):
  python3 producao/lote-teste/sincronia_episodio.py producao/lote-teste/montagem/E-02.json [--custo]

Cada fala com "rosto": [x, y] (ponto no rosto de quem fala, no primeiro quadro da cena já no tempo
final) entra na sincronia. Para cada cena com fala:
  1. o clipe é cortado no tempo final (de/ate, vel, hold);
  2. cada fala passa pelo sync-3 em sequência (a saída de uma é a entrada da outra), só na boca
     de quem fala, com silêncio no resto;
  3. o resultado vai para media/<clipe>_sync.mp4 e a cena ganha "video" no JSON.
Pula a cena que já tem o _sync.mp4. Custo: US$ 0,133 por segundo de clipe, por fala.
"""
import json, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from gerar_fal import MEDIA  # noqa: E402
from sincronia_fal import sincronizar  # noqa: E402

POR_SEG = 8 / 60


def tempo_final(c, saida):
    v = c.get("vel", 1.0)
    vf = [f"trim={c['de']}:{c['ate']}", "setpts=PTS-STARTPTS", f"setpts=PTS/{v}", "fps=30"]
    if c.get("hold"):
        vf.append(f"tpad=stop_mode=clone:stop_duration={c['hold']}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(MEDIA, c["clip"] + ".mp4"), "-an",
                    "-vf", ",".join(vf), "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                    "-pix_fmt", "yuv420p", saida], check=True)


def plano(j):
    """[(índice da cena, cena, [falas com rosto])] das cenas que precisam de sincronia."""
    out = []
    for i, c in enumerate(j["cenas"]):
        fs = sorted([f for f in j["falas"] if f["cena"] == i and f.get("rosto")], key=lambda f: f["t"])
        if fs:
            out.append((i, c, fs))
    return out


def duracao(c):
    return (c["ate"] - c["de"]) / c.get("vel", 1.0) + c.get("hold", 0)


def cena(c, falas):
    final = os.path.join(MEDIA, c["clip"] + "_sync.mp4")
    if os.path.exists(final):
        print("já existe", os.path.basename(final))
        return
    tmp = tempfile.mkdtemp()
    atual = os.path.join(tmp, "base.mp4")
    tempo_final(c, atual)
    for k, f in enumerate(falas):
        prox = os.path.join(tmp, f"passo{k}.mp4")
        sincronizar(atual, os.path.join(MEDIA, f["a"] + ".mp3"), f["t"], f["rosto"][0], f["rosto"][1], prox)
        atual = prox
    shutil.copy(atual, final)
    print("pronto", os.path.basename(final))


if __name__ == "__main__":
    arq = sys.argv[1]
    j = json.load(open(arq))
    p = plano(j)
    pend = [(i, c, fs) for i, c, fs in p if not os.path.exists(os.path.join(MEDIA, c["clip"] + "_sync.mp4"))]
    seg = sum(duracao(c) * len(fs) for _, c, fs in pend)
    print(f"{j['id']}: {len(pend)} cenas, {sum(len(fs) for *_, fs in pend)} passagens, "
          f"{seg:.1f} s de clipe, US$ {seg * POR_SEG:.2f}")
    if "--custo" in sys.argv:
        sys.exit()
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda x: cena(x[1], x[2]), pend))
    for i, c, fs in p:
        if os.path.exists(os.path.join(MEDIA, c["clip"] + "_sync.mp4")):
            c["video"] = c["clip"] + "_sync.mp4"
    json.dump(j, open(arq, "w"), ensure_ascii=False, indent=1)
