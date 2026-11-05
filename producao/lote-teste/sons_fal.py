#!/usr/bin/env python3
"""Gera o som ambiente sincronizado de cada clipe pelo fal.ai (Mirelo SFX 2.0, video-to-audio).

Uso (precisa de FAL_KEY):  python3 producao/lote-teste/sons_fal.py [clipes...]
Salva media/<clipe>_sfx.wav. US$ 0,01 por segundo, 1 amostra por clipe. Pula o que já existe.
"""
import base64, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from gerar_fal import http, esperar, baixar, MEDIA  # noqa: E402

SFX = "mirelo-ai/sfx2.0/video-to-audio"
SEM_FALA = "music, singing, speech, talking, voices"
SONS = {
    "CI-09": ("doctor's office, upbeat pop dance track playing quietly from a smartphone speaker on a tripod, "
              "sneakers squeaking on the tile floor, a phone on the desk vibrating and buzzing again and again", "speech, talking"),
    "PO-02": ("inside a parked car at dawn, engine off, very quiet, distant traffic, a few birds outside, "
              "slow tired breathing, seat creak", SEM_FALA),
    "CI-11_d1": ("elegant clinic reception inauguration party, champagne glasses clinking, light applause, "
                 "cheerful crowd chatter in the background", "music, singing"),
    "CI-11_d2": ("busy medical clinic waiting room, low murmur of patients, footsteps on porcelain floor, "
                 "a phone ringing softly at the front desk", "music, singing"),
    "CI-11_d3": ("empty clinic reception at night, quiet air conditioning hum, calculator buttons clicking, "
                 "paper rustling", SEM_FALA),
    "CI-12_a": ("quiet upscale clinic reception in the morning, soft air conditioning, a few footsteps", SEM_FALA),
    "CI-12_b": ("busy clinic reception, desk phone ringing, smartphone notification pings again and again, "
                "patients murmuring impatiently", "music, singing"),
    "CI-12_c": ("quiet clinic reception in the evening, soft air conditioning hum", SEM_FALA),
    "CI-13_a": ("quiet elegant doctor's office, soft air conditioning hum, leather chair creak, "
                "distant city traffic through the window", SEM_FALA),
    "CI-13_b": ("quiet elegant doctor's office, soft air conditioning hum, leather chair creak, "
                "distant city traffic through the window", SEM_FALA),
    "CI-13_c": ("quiet elegant doctor's office, soft air conditioning hum, leather chair creak, "
                "distant city traffic through the window", SEM_FALA),
}


def um(clipe):
    saida = os.path.join(MEDIA, clipe + "_sfx.wav")
    if os.path.exists(saida):
        return
    leve = os.path.join(MEDIA, clipe + "_leve.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(MEDIA, clipe + ".mp4"),
                    "-vf", "scale=540:960", "-c:v", "libx264", "-crf", "30", "-an", leve], check=True)
    uri = "data:video/mp4;base64," + base64.b64encode(open(leve, "rb").read()).decode()
    prompt, neg = SONS[clipe]
    r = http("POST", f"https://queue.fal.run/{SFX}", {
        "video_url": uri, "text_prompt": prompt, "negative_prompt": neg, "num_samples": 1,
        "duration": 10, "preserve_speech": False})
    res = esperar(SFX, r["request_id"])
    audios = res.get("audio") or res.get("audios") or res.get("outputs") or []
    if isinstance(audios, dict):
        audios = [audios]
    baixar(audios[0]["url"], saida)
    os.remove(leve)


def _seguro(c):
    try:
        um(c)
    except Exception as e:
        print("FALHOU", c, e)


if __name__ == "__main__":
    alvo = sys.argv[1:] or list(SONS)
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(_seguro, alvo))
