#!/usr/bin/env python3
"""Monta o Reel CI-01 (A doutora pontual): versão pronta e versão limpa."""
import json, os, subprocess, sys

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(W, "media")
B = os.path.join(W, "build")
O = os.path.join(W, "saida")
os.makedirs(O, exist_ok=True)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FPS = 30


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(" ".join(cmd)[:2000])
        print(r.stderr[-3000:])
        sys.exit(1)


def txt(name, s):
    p = os.path.join(B, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)
    return p


# ---------- linha do tempo ----------
GANCHO = 2.5
CARTELA = 6.0
FECHA = 3.0
# cena: arquivo, fator de velocidade, segundos congelados no fim, dia, hora inicial (h, m, s)
CENAS = [
    ("s1", 0.80, 0.0, 1, (7, 58, 10)),
    ("s2", 0.87, 0.0, 1, (8, 41, 5)),
    ("s3", 0.90, 1.5, 2, (7, 50, 12)),
    ("s4", 1.00, 0.0, 2, (8, 43, 20)),
    ("s5", 1.00, 0.6, 3, (7, 30, 14)),
    ("s6", 0.90, 0.0, 3, (8, 45, 2)),
]
SRC = {"s1": 4, "s2": 4, "s3": 6, "s4": 4, "s5": 8, "s6": 8}

starts, t = [], GANCHO
for c in CENAS:
    starts.append(t)
    t += SRC[c[0]] / c[1] + c[2]
FIM_CENAS = t
INI_CART = FIM_CENAS
INI_FECHA = INI_CART + CARTELA
TOTAL = INI_FECHA + FECHA

# falas: (arquivo, início absoluto, fim da legenda, quem, texto)
FALAS = [
    ("l1", 3.20, 7.60, "Kelly", "Bom dia, dona Marta! Pode sentar, a doutora já já chega."),
    ("l2", 7.85, 12.05, "Dra. Renata", "Bom dia, gente! Desculpa, o trânsito tava um caos…"),
    ("l3", 13.10, 15.80, "Kelly", "Ué, dona Marta, chegou cedo, hein?"),
    ("l4", 15.80, 20.25, "Dona Marta", "Trouxe meu cafezinho, minha filha. Já sei como é."),
    ("l5", 20.95, 23.65, "Dra. Renata", "Hoje não foi culpa minha, juro!"),
    ("l6", 26.30, 29.20, "Kelly", "Quer uma mantinha, dona Marta?"),
    ("l7", 29.40, 32.85, "Dona Marta", "Aceito… me acorda quando ela chegar, tá?"),
    ("n1", 34.20, 35.70, "Dra. Renata", "Ai, me desculpa, me desculpa…"),
    ("n2", 35.70, 38.90, "Kelly", "Shhh… silêncio, que ela tá dormindo."),
    ("n3", 39.10, 40.20, "Dra. Renata", "Tá dormindo?"),
    ("n4", 40.40, 45.30, "Kelly", "Chegou cedinho pra esperar você… você sempre atrasa."),
]
# sons: (arquivo, início absoluto, ganho em dB)
SONS = [
    ("porta", 3.00, -8), ("passos", 8.60, -10), ("porta", 11.40, -9),
    ("porta", 12.60, -9), ("termica", 14.40, -14),
    ("porta", 20.45, -8), ("passos", 20.70, -10),
    ("porta", 24.80, -9), ("manta", 27.70, 6),
    ("porta", 33.90, -7), ("passos", 34.00, -12),
]
AMB_FIM = 46.0


# ---------- cenas ----------
def cena(i, pronta):
    nome, f, hold, dia, (h, m, s) = CENAS[i]
    out = os.path.join(B, f"{'p' if pronta else 'c'}_{nome}.mp4")
    if os.path.exists(out):
        return out
    vf = [f"setpts=PTS/{f}", f"fps={FPS}"]
    if hold:
        vf.append(f"tpad=stop_mode=clone:stop_duration={hold}")
    vf.append("scale=1080:1920,setsar=1")
    if pronta:
        vf += [
            "eq=saturation=0.78:contrast=0.94:brightness=0.01",
            "colorbalance=bs=0.05:bm=0.02:bh=0.02",
            "vignette=angle=PI/5",
            "noise=alls=9:allf=t+u",
            "fps=15", f"fps={FPS}",
        ]
        cam = txt("cam.txt", "CAM 01 · RECEPÇÃO")
        sel = txt("selo.txt", "SIMULAÇÃO · IA")
        dia_t = txt(f"dia{i}.txt", f"DIA {dia}")
        osd = "fontfile=%s:fontcolor=0xEDEFE6:shadowcolor=black@0.8:shadowx=2:shadowy=2" % FM
        vf += [
            f"drawbox=x=0:y=0:w=iw:h=150:color=black@0.35:t=fill",
            f"drawtext={osd}:text='● REC':fontsize=46:x=44:y=52:fontcolor=0xFF3B4E:enable='lt(mod(t,1),0.6)'",
            f"drawtext={osd}:textfile='{cam}':fontsize=40:x=250:y=56",
            f"drawtext={osd}:textfile='{dia_t}':fontsize=40:x=w-tw-44:y=56",
            f"drawtext={osd}:text='{h:02d}\\:{m:02d}\\:%{{eif\\:{s}+trunc(t)\\:d\\:2}}':fontsize=40:x=w-tw-44:y=104",
            f"drawtext={osd}:textfile='{sel}':fontsize=30:x=44:y=110:fontcolor=0xEDEFE6@0.85",
        ]
    run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(M, nome + ".mp4"), "-an",
         "-vf", ",".join(vf), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    return out


def cartao(nome, dur, linhas, pronta):
    out = os.path.join(B, f"{'p' if pronta else 'c'}_{nome}.mp4")
    vf = ["noise=alls=4:allf=t"] if pronta else []
    if pronta:
        for j, (texto, tam, cor, y, fonte) in enumerate(linhas):
            p = txt(f"{nome}{j}.txt", texto)
            vf.append(f"drawtext=fontfile={fonte}:textfile='{p}':fontsize={tam}:fontcolor={cor}:x=(w-tw)/2:y={y}")
    args = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
            f"color=c=0x101418:s=1080x1920:r={FPS}:d={dur}"]
    if vf:
        args += ["-vf", ",".join(vf)]
    run(args + ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out])
    return out


def video(pronta):
    segs = [cartao("gancho", GANCHO, [
        ("Quando eu lembro da câmera", 56, "white", 760, FB),
        ("da recepção da Dra. Renata…", 56, "white", 850, FB),
        ("[aqui entra a tua selfie]", 34, "0x9AA59F", 1010, FR)], pronta)]
    segs += [cena(i, pronta) for i in range(len(CENAS))]
    segs.append(cartao("cartela", CARTELA, [
        ("40 min de atraso por dia", 62, "white", 700, FB),
        ("=", 62, "0xFFE14D", 800, FB),
        ("22 consultas a menos", 62, "0xFFE14D", 900, FB),
        ("no mês.", 62, "0xFFE14D", 990, FB),
        ("simulação · consultas de 40 min", 32, "0x9AA59F", 1100, FR)], pronta))
    segs.append(cartao("fecha", FECHA, [
        ("Atraso não é defeito", 58, "white", 640, FB),
        ("de caráter, tá?", 58, "white", 730, FB),
        ("É agenda sem folga.", 58, "white", 820, FB),
        ("Comenta", 70, "white", 960, FB),
        ("DIAGNÓSTICO", 96, "0xFFE14D", 1050, FB),
        ("[aqui entra a tua selfie]", 34, "0x9AA59F", 1200, FR)], pronta))
    lista = os.path.join(B, f"lista_{'p' if pronta else 'c'}.txt")
    with open(lista, "w") as fh:
        for sg in segs:
            fh.write(f"file '{sg}'\n")
    out = os.path.join(B, f"video_{'p' if pronta else 'c'}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", out])
    return out


# ---------- áudio ----------
def audio():
    ins, fl = [], []
    k = 0
    for nome, ini, *_ in FALAS:
        ins += ["-i", os.path.join(M, nome + ".mp3")]
        fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={int(ini*1000)}|{int(ini*1000)}[a{k}]")
        k += 1
    for nome, ini, db in SONS:
        ins += ["-i", os.path.join(M, nome + ".mp3")]
        fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={db}dB,adelay={int(ini*1000)}|{int(ini*1000)}[a{k}]")
        k += 1
    amb_dur = AMB_FIM - GANCHO + 0.8
    ins += ["-stream_loop", "1", "-i", os.path.join(M, "amb.mp3")]
    fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{amb_dur},volume=-14dB,"
              f"afade=t=in:st=0:d=0.6,afade=t=out:st={amb_dur-0.8}:d=0.8,adelay={int(GANCHO*1000-300)}|{int(GANCHO*1000-300)}[a{k}]")
    k += 1
    fl.append("".join(f"[a{j}]" for j in range(k)) + f"amix=inputs={k}:normalize=0:duration=longest,"
              f"apad=whole_dur={TOTAL},atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[mix]")
    out = os.path.join(B, "audio.wav")
    run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fl), "-map", "[mix]", out])
    return out


# ---------- legendas ----------
def ts(x, srt=True):
    h, r = divmod(x, 3600)
    m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s-int(s))*1000)):03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def legendas():
    srt = os.path.join(O, "CI-01_legendas.srt")
    with open(srt, "w", encoding="utf-8") as f:
        for n, (_, a, b, quem, texto) in enumerate(FALAS, 1):
            f.write(f"{n}\n{ts(a)} --> {ts(b)}\n{texto}\n\n")
    ass = os.path.join(B, "legendas.ass")
    with open(ass, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
                "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                "Alignment, MarginL, MarginR, MarginV, Encoding\n"
                "Style: Fala,DejaVu Sans,54,&H004DE1FF,&H004DE1FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,1,2,90,90,520,1\n"
                "Style: Marca,DejaVu Sans,112,&H00FFFFFF,&H00FFFFFF,&H50000000,&H00000000,-1,0,0,0,100,100,2,0,3,26,0,5,60,60,0,1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for _, a, b, quem, texto in FALAS:
            f.write(f"Dialogue: 0,{ts(a, False)},{ts(b, False)},Fala,{quem},0,0,0,,{texto}\n")
        for i, (_, _, _, dia, (h, m, _)) in enumerate(CENAS):
            a = starts[i]
            f.write(f"Dialogue: 1,{ts(a, False)},{ts(a + 1.9, False)},Marca,,0,0,0,,"
                    f"{{\\fad(120,280)}}DIA {dia}\\N{{\\fs82\\c&H4DE1FF&}}{h}:{m:02d} DA MANHÃ\n")
    return srt, ass


def final(vid, aud, ass, nome):
    out = os.path.join(O, nome)
    vf = ["-vf", f"subtitles={ass}"] if ass else []
    run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", aud] + vf +
        ["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-maxrate", "12M", "-bufsize", "24M",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", out])
    return out


if __name__ == "__main__":
    print(json.dumps({"inicios_cenas": [round(x, 3) for x in starts], "fim_cenas": round(FIM_CENAS, 3),
                      "total": round(TOTAL, 3)}))
    aud = audio()
    srt, ass = legendas()
    vp = video(True)
    vc = video(False)
    print(final(vp, aud, ass, "CI-01_A-doutora-pontual_PRONTA.mp4"))
    if not os.path.exists(os.path.join(O, "CI-01_A-doutora-pontual_LIMPA.mp4")):
        print(final(vc, aud, None, "CI-01_A-doutora-pontual_LIMPA.mp4"))
    print(srt)
