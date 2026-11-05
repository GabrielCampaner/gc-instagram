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
    "E-02_p1": ("elegant private office, quiet air conditioning, distant city traffic through the window, pen tapping on paper", SEM_FALA),
    "E-02_p2": ("elegant private office, quiet air conditioning, distant city traffic, leather chair creak", SEM_FALA),
    "E-02_p3": ("elegant private office, quiet room tone, pen writing on a paper notepad", SEM_FALA),
    "E-02_p4": ("elegant private office, quiet room tone, pen scribbling and underlining on a notepad, paper sliding across a wooden desk", SEM_FALA),
    "E-02_p5": ("elegant private office, quiet room tone, a pen clicking closed and placed on a wooden desk", SEM_FALA),
    "E-04_p1": ("elegant doctor's office in the evening, quiet room tone, soft air conditioning, a pen being fiddled with", SEM_FALA),
    "E-04_p2": ("elegant doctor's office in the evening, quiet room tone, a pen placed on a desk, a deep breath", SEM_FALA),
    "E-04_p3": ("elegant doctor's office in the evening, very quiet room tone, soft air conditioning", SEM_FALA),
    "E-04_p4": ("elegant doctor's office in the evening, quiet room tone, soft air conditioning, leather chair creak", SEM_FALA),
    "E-06_p1": ("bright office in the morning, a heavy leather handbag dropped on a wooden floor, an office chair dragged and someone sitting down fast, out of breath", SEM_FALA),
    "E-06_p2": ("bright office in the morning, quiet room tone, birds outside the window, soft air conditioning", SEM_FALA),
    "E-06_p3": ("bright office in the morning, quiet room tone, soft air conditioning", SEM_FALA),
    "E-06_p4": ("bright office in the morning, a smartphone slid across a wooden desk, quiet room tone", SEM_FALA),
    "E-06_p5": ("bright office in the morning, quiet room tone, soft air conditioning", SEM_FALA),
    "CI-14_s1": ("upscale clinic reception, a hand slapping hard on a marble counter twice, tense silence, "
                 "patients shifting in their seats, soft air conditioning", SEM_FALA),
    "CI-14_s2": ("upscale clinic reception, tense silence, a chair creak, uncomfortable murmur of patients", SEM_FALA),
    "CI-14_s3": ("quiet elegant doctor's office, soft air conditioning hum, paper rustling, leather chair creak", SEM_FALA),
    "CI-14_s3b": ("quiet elegant doctor's office, soft air conditioning hum, paper rustling, leather chair creak", SEM_FALA),
    "CI-14_s4": ("doctor's office, a chair pushed back fast, papers and an envelope swept off a wooden desk and falling "
                 "on the floor, a pen holder falling and pens scattering, fast footsteps leaving, a door opening", SEM_FALA),
    "CI-14_s5": ("upscale clinic reception, fast angry high-heel footsteps on porcelain floor, a ceramic flower pot "
                 "knocked off a counter and shattering on the floor, brochures and a card machine falling, "
                 "a glass door closing, then shocked silence and a gasp", SEM_FALA),
    "CI-15_s1": ("city sidewalk in an upscale neighborhood in the late morning, light traffic passing, distant birds, "
                 "phone keyboard tapping, a child fidgeting", SEM_FALA),
    "CI-15_s2": ("overcrowded clinic reception, two desk phones ringing at the same time, card machine beeping and "
                 "printing a receipt, constant murmur of many patients, a glass door opening", "music, singing"),
    "CI-15_s3": ("overcrowded clinic reception, desk phone ringing again and again, keyboard typing, card machine beeps, "
                 "constant murmur of patients", "music, singing"),
    "CI-15_s4": ("overcrowded clinic reception, desk phone ringing, murmur of patients, a glass door opening and closing", "music, singing"),
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
