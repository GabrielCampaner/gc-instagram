#!/usr/bin/env python3
"""Gera as falas de falas.json pelo fal.ai (Eleven v4), 2 tomadas cada, em media/<id>_t1.mp3 e _t2.mp3.

Uso (precisa de FAL_KEY):  python3 producao/lote-teste/falar_fal.py [ids...]
Pula as falas que já têm arquivo. Custo: US$ 0,08 por mil caracteres.
"""
import json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from gerar_fal import http, esperar, baixar, MEDIA  # noqa: E402

TTS = "elevenlabs/tts/eleven-v4"
spec = json.load(open(os.path.join(AQUI, "falas.json")))


def uma(item):
    f, tomada = item
    saida = os.path.join(MEDIA, f"{f['id']}_t{tomada}.mp3")
    if os.path.exists(saida):
        return
    r = http("POST", f"https://queue.fal.run/{TTS}", {
        "text": f["texto"], "voice": spec["vozes"][f["voz"]], "language_code": "pt",
        "stability": 0.45, "similarity_boost": 0.8, "seed": 11 * tomada})
    res = esperar(TTS, r["request_id"])
    baixar(res["audio"]["url"], saida)


if __name__ == "__main__":
    ids = sys.argv[1:]
    os.makedirs(MEDIA, exist_ok=True)
    fila = [(f, t) for f in spec["falas"] if not ids or f["id"] in ids for t in (1, 2)]
    chars = sum(len(f["texto"]) for f, _ in fila)
    print(f"{len(fila)} gerações, {chars} caracteres, cerca de US$ {chars * 0.08 / 1000:.3f}")
    with ThreadPoolExecutor(6) as ex:
        for e in ex.map(lambda it: (uma(it), None)[1], fila):
            pass
