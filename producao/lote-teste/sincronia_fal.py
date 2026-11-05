#!/usr/bin/env python3
"""Sincronia labial com o áudio real (sync-3, da sync.so, pelo fal.ai).

Uso (precisa de FAL_KEY):
  python3 producao/lote-teste/sincronia_fal.py CLIPE FALA INICIO X Y SAIDA
    CLIPE   vídeo do clipe (ex.: media/E-04_p3.mp4)
    FALA    áudio da fala (ex.: media/E-04_s2_t1.mp3)
    INICIO  em que segundo do clipe a fala começa
    X Y     ponto no rosto de quem fala, no primeiro quadro (o modelo mexe só nessa boca)
    SAIDA   vídeo resultante, mesma duração do clipe

Custo: US$ 8 por minuto de vídeo processado (US$ 0,13 por segundo).
"""
import json, os, subprocess, sys, tempfile, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from gerar_fal import http, esperar, baixar  # noqa: E402

SYNC = "fal-ai/sync-lipsync/v3"


def subir(caminho, tipo):
    """Envia um arquivo para o armazenamento do fal e devolve a URL pública."""
    ini = http("POST", "https://rest.alpha.fal.ai/storage/upload/initiate",
               {"content_type": tipo, "file_name": os.path.basename(caminho)})
    req = urllib.request.Request(ini["upload_url"], data=open(caminho, "rb").read(), method="PUT",
                                 headers={"Content-Type": tipo})
    urllib.request.urlopen(req, timeout=300).read()
    return ini["file_url"]


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip())


def sincronizar(clipe, fala, inicio, x, y, saida):
    tmp = tempfile.mkdtemp()
    total = dur(clipe)
    audio = os.path.join(tmp, "fala.wav")
    ms = int(inicio * 1000)
    # silêncio até a fala começar e depois dela, até o fim do clipe
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", fala, "-af",
                    f"adelay={ms}|{ms},apad=whole_dur={total},atrim=0:{total}", "-ar", "44100", "-ac", "1", audio],
                   check=True)
    v_url = subir(clipe, "video/mp4")
    a_url = subir(audio, "audio/wav")
    r = http("POST", f"https://queue.fal.run/{SYNC}", {
        "video_url": v_url, "audio_url": a_url, "sync_mode": "cut_off",
        "options": {"active_speaker_detection": {"coordinates": [int(x), int(y)], "frame_number": 0}}})
    print("enviado", os.path.basename(saida), r["request_id"])
    res = esperar(SYNC, r["request_id"])
    baixar(res["video"]["url"], saida)


if __name__ == "__main__":
    c, f, i, x, y, s = sys.argv[1:7]
    sincronizar(c, f, float(i), x, y, s)
