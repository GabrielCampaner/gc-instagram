#!/usr/bin/env python3
"""Sincronia labial de um episódio inteiro (sync-3 pelo fal.ai), a partir do JSON de montagem.

Uso (precisa de FAL_KEY):
  python3 producao/lote-teste/sincronia_episodio.py producao/lote-teste/montagem/E-02.json [--custo]

Cada fala com "rosto": [x, y] (ponto no rosto de quem fala, no primeiro quadro da cena já no tempo
final; ou no quadro "rosto_quadro", quando o rosto está pequeno ou de costas no começo) entra na sincronia. Para cada cena com fala:
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


def passo(c, k):
    """Saída da passagem k (só as falas 0..k sincronizadas), guardada para retomar sem pagar de novo."""
    return os.path.join(MEDIA, f"{c['clip']}_sync_p{k}.mp4")


def mais_avancado(c, n):
    """O arquivo mais adiantado da cena: o final, ou a última passagem salva, ou None."""
    final = os.path.join(MEDIA, c["clip"] + "_sync.mp4")
    if os.path.exists(final):
        return final
    for k in range(n - 1, -1, -1):
        if os.path.exists(passo(c, k)):
            return passo(c, k)
    return None


def cena(c, falas):
    final = os.path.join(MEDIA, c["clip"] + "_sync.mp4")
    if os.path.exists(final):
        print("já existe", os.path.basename(final), flush=True)
        return
    tmp = tempfile.mkdtemp()
    atual = os.path.join(tmp, "base.mp4")
    tempo_final(c, atual)
    try:
        for k, f in enumerate(falas):
            if os.path.exists(passo(c, k)):
                atual = passo(c, k)
                continue
            prox = os.path.join(tmp, f"passo{k}.mp4")
            sincronizar(atual, os.path.join(MEDIA, f["a"] + ".mp3"), f["t"], f["rosto"][0], f["rosto"][1], prox,
                        f.get("rosto_quadro", 0))
            shutil.copy(prox, passo(c, k))
            atual = passo(c, k)
    except Exception as e:  # ex.: saldo do fal acabou; o que já saiu fica salvo
        print("FALHOU", c["clip"], str(e)[:300], flush=True)
        return
    shutil.copy(atual, final)
    for k in range(len(falas)):
        if os.path.exists(passo(c, k)):
            os.remove(passo(c, k))
    print("pronto", os.path.basename(final), flush=True)


if __name__ == "__main__":
    arq = sys.argv[1]
    j = json.load(open(arq))
    p = plano(j)
    pend = [(i, c, fs) for i, c, fs in p if not os.path.exists(os.path.join(MEDIA, c["clip"] + "_sync.mp4"))]
    falta = [(c, [k for k in range(len(fs)) if not os.path.exists(passo(c, k))]) for _, c, fs in pend]
    seg = sum(duracao(c) * len(ks) for c, ks in falta)
    print(f"{j['id']}: {len(pend)} cenas, {sum(len(ks) for _, ks in falta)} passagens, "
          f"{seg:.1f} s de clipe, US$ {seg * POR_SEG:.2f}", flush=True)
    if "--custo" not in sys.argv:
        with ThreadPoolExecutor(4) as ex:
            list(ex.map(lambda x: cena(x[1], x[2]), pend))
    # a montagem usa o que estiver mais adiantado (final ou passagem parcial)
    for i, c, fs in p:
        v = mais_avancado(c, len(fs))
        if v:
            c["video"] = os.path.basename(v)
    json.dump(j, open(arq, "w"), ensure_ascii=False, indent=1)
