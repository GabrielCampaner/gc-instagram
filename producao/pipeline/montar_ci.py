#!/usr/bin/env python3
"""Monta um Reel da série (formato CI · câmera interna, ou PO · pensamento oculto) a partir de um JSON.

Uso:  python3 producao/pipeline/montar_ci.py producao/lote-teste/montagem/CI-11.json

O JSON traz: clipes e trechos, falas, marcações de dia e hora, gancho do topo e o fechamento.
Fechamento padrão (CI): congela o último quadro, zoom de câmera de segurança em REC,
a gravação "pausa", a conta aparece com os números subindo, a frase e a chamada final.
Grava em producao/lote-teste/saida/<id>_PRONTA.mp4, <id>_LIMPA.mp4 e <id>.srt.
"""
import json, os, subprocess, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FPS = 30
COR = {"b": "&H00FFFFFF&", "a": "&H004DE1FF&", "v": "&H005F5AFF&", "c": "&H009FA59A&"}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(" ".join(cmd)[:3000])
        print(r.stderr[-3000:])
        sys.exit(1)
    return r.stdout


def dur(p):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())


def ts(x, srt=True):
    h, r = divmod(max(x, 0), 3600)
    m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


class Reel:
    def __init__(self, arq):
        self.j = json.load(open(arq))
        j = self.j
        self.id = j["id"]
        self.media = os.path.join(RAIZ, j.get("media", "producao/lote-teste/media"))
        self.saida = os.path.join(RAIZ, j.get("saida", "producao/lote-teste/saida"))
        self.b = os.path.join(j.get("build", "/tmp/montar_ci"), self.id)
        os.makedirs(self.b, exist_ok=True)
        os.makedirs(self.saida, exist_ok=True)
        self.cctv = j.get("formato", "CI") == "CI"
        # linha do tempo
        self.ini, t = [], 0.0
        for c in j["cenas"]:
            self.ini.append(t)
            c["dur"] = (c["ate"] - c["de"]) / c.get("vel", 1.0) + c.get("hold", 0)
            t += c["dur"]
        self.fim_cenas = t
        f = j["fecho"]
        self.rec = f.get("rec", 1.2)
        self.pausa = f.get("pausa", 7.0)
        self.ini_pausa = t + self.rec
        self.total = t + self.rec + self.pausa

    # ---------- arquivos de texto para drawtext ----------
    def tf(self, nome, s):
        p = os.path.join(self.b, nome)
        open(p, "w", encoding="utf-8").write(s)
        return p

    def relogio(self, t0, ate=None):
        """drawtext do relógio HH:MM:SS que anda com o vídeo (ou parado, se ate=None e t0 fixo)."""
        e = f"{t0}+trunc(t)" if ate is None else f"{t0}"
        return (f"%{{eif\\:trunc(({e})/3600)\\:d\\:2}}\\:%{{eif\\:mod(trunc(({e})/60)\\,60)\\:d\\:2}}"
                f"\\:%{{eif\\:mod(trunc({e})\\,60)\\:d\\:2}}")

    def look(self):
        if self.cctv:
            return ["eq=saturation=0.80:contrast=0.95:brightness=0.01", "colorbalance=bs=0.04:bm=0.02:bh=0.02",
                    "vignette=angle=PI/5", "noise=alls=8:allf=t+u", "fps=15", f"fps={FPS}"]
        return ["eq=saturation=0.92:contrast=1.03", "vignette=angle=PI/4", "noise=alls=5:allf=t"]

    def hud(self, cena, rec_ate=None, pausa_de=None, t0=None):
        """Letreiro de câmera: REC piscando, câmera, rótulo do dia, relógio e selo."""
        if not self.cctv:
            return []
        osd = f"fontfile={FM}:fontcolor=0xEDEFE6:shadowcolor=black@0.8:shadowx=2:shadowy=2"
        cam = self.tf("cam.txt", cena.get("cam", "CAM 01 · RECEPÇÃO"))
        rot = self.tf(f"rot_{id(cena)}.txt", cena.get("rotulo", ""))
        sel = self.tf("selo.txt", "SIMULAÇÃO · IA")
        h, m, s = cena["hora"]
        base = h * 3600 + m * 60 + s if t0 is None else t0
        f = [f"drawbox=x=0:y=0:w=iw:h=160:color=black@0.40:t=fill"]
        rec_en = "lt(mod(t\\,1)\\,0.6)" if rec_ate is None else f"lt(t\\,{rec_ate})*lt(mod(t\\,1)\\,0.6)"
        f.append(f"drawtext={osd}:text='● REC':fontsize=46:x=44:y=52:fontcolor=0xFF3B4E:enable='{rec_en}'")
        if pausa_de is not None:
            f.append(f"drawbox=x=48:y=58:w=12:h=36:color=0xFFE14D:t=fill:enable='gte(t\\,{pausa_de})'")
            f.append(f"drawbox=x=68:y=58:w=12:h=36:color=0xFFE14D:t=fill:enable='gte(t\\,{pausa_de})'")
            f.append(f"drawtext={osd}:text='PAUSE':fontsize=40:x=96:y=56:fontcolor=0xFFE14D:enable='gte(t\\,{pausa_de})'")
        f.append(f"drawtext={osd}:textfile='{cam}':fontsize=38:x=260:y=58")
        f.append(f"drawtext={osd}:textfile='{rot}':fontsize=38:x=w-tw-44:y=58")
        if pausa_de is None:
            f.append(f"drawtext={osd}:text='{self.relogio(base)}':fontsize=38:x=w-tw-44:y=106")
        else:
            f.append(f"drawtext={osd}:text='{self.relogio(base)}':fontsize=38:x=w-tw-44:y=106:enable='lt(t\\,{pausa_de})'")
            parado = base + int(pausa_de)
            f.append(f"drawtext={osd}:text='{self.relogio(parado, ate=True)}':fontsize=38:x=w-tw-44:y=106"
                     f":enable='gte(t\\,{pausa_de})'")
            f.append(f"drawtext={osd}:text='ZOOM 1.5x':fontsize=30:x=(w-tw)/2:y=112:enable='gte(t\\,0.4)'")
        f.append(f"drawtext={osd}:textfile='{sel}':fontsize=28:x=44:y=114:fontcolor=0xEDEFE6@0.85")
        return f

    def enquadra(self):
        c = self.j.get("crop")
        if c:
            return [f"crop={c[0]}:{c[1]}:{c[2]}:{c[3]}", "scale=1080:1920,setsar=1"]
        return ["scale=1080:1920,setsar=1"]

    # ---------- vídeo ----------
    def cena(self, i, pronta):
        c = self.j["cenas"][i]
        out = os.path.join(self.b, f"{'p' if pronta else 'c'}_{i}.mp4")
        v = c.get("vel", 1.0)
        vf = [f"trim={c['de']}:{c['ate']}", "setpts=PTS-STARTPTS", f"setpts=PTS/{v}", f"fps={FPS}"]
        if c.get("hold"):
            vf.append(f"tpad=stop_mode=clone:stop_duration={c['hold']}")
        vf += self.enquadra()
        if pronta:
            vf += self.look() + self.hud(c)
        run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(self.media, c["clip"] + ".mp4"), "-an",
             "-vf", ",".join(vf), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), out])
        return out

    def fecho(self, pronta):
        """Último quadro congelado: zoom em REC e, depois, PAUSE escurecendo."""
        c = self.j["cenas"][-1]
        f = self.j["fecho"]
        quadro = os.path.join(self.b, "ultimo.png")
        v = c.get("vel", 1.0)
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(max(c["ate"] - 0.06, 0)), "-i",
             os.path.join(self.media, c["clip"] + ".mp4"), "-frames:v", "1",
             "-vf", ",".join(self.enquadra()), quadro])
        zf, zx, zy = f.get("zoom", [1.4, 540, 960])
        d = self.rec + self.pausa
        n = int(round(d * FPS))
        zr = max(self.rec - 0.15, 0.3) * FPS
        ease = f"(min(on/{zr}\\,1)*min(on/{zr}\\,1)*(3-2*min(on/{zr}\\,1)))"
        z = f"1+{zf - 1}*{ease}"
        cx = f"(1080+({zx * 2}-1080)*{ease})"
        cy = f"(1920+({zy * 2}-1920)*{ease})"
        vf = ["scale=2160:3840",
              f"zoompan=z='{z}':x='max(0\\,min(iw-iw/zoom\\,{cx}-iw/zoom/2))'"
              f":y='max(0\\,min(ih-ih/zoom\\,{cy}-ih/zoom/2))':d=1:s=1080x1920:fps={FPS}",
              "setsar=1"]
        if pronta:
            vf += self.look()
            if self.cctv:
                vf.append(f"eq=brightness='if(lt(t\\,{self.rec})\\,0\\,-0.22*min((t-{self.rec})/0.45\\,1))'"
                          f":saturation='if(lt(t\\,{self.rec})\\,1\\,1-0.35*min((t-{self.rec})/0.45\\,1))':eval=frame")
                h, m, s = c["hora"]
                t0 = h * 3600 + m * 60 + s + int(c["dur"])
                vf += self.hud(c, rec_ate=self.rec, pausa_de=self.rec, t0=t0)
            else:
                vf.append(f"eq=brightness='-0.34*min(t/0.8\\,1)':eval=frame")
        out = os.path.join(self.b, f"{'p' if pronta else 'c'}_fecho.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", quadro,
             "-vf", ",".join(vf), "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), out])
        return out

    def video(self, pronta):
        segs = [self.cena(i, pronta) for i in range(len(self.j["cenas"]))] + [self.fecho(pronta)]
        lista = os.path.join(self.b, f"lista_{pronta}.txt")
        open(lista, "w").write("".join(f"file '{s}'\n" for s in segs))
        out = os.path.join(self.b, f"video_{'p' if pronta else 'c'}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", out])
        return out

    # ---------- áudio ----------
    def audio(self):
        ins, fl, k = [], [], 0
        filtro_cam = ("highpass=f=170,lowpass=f=5600,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                      "aecho=0.8:0.5:22|41:0.22|0.12") if self.cctv else "highpass=f=90,acompressor=threshold=-22dB:ratio=2.5"

        def add(src, filtros, ini, lavfi=False, dur_s=None):
            nonlocal k
            if lavfi:
                ins.extend(["-f", "lavfi", "-t", f"{dur_s}", "-i", src])
            else:
                ins.extend(["-i", src])
            ms = int(max(ini, 0) * 1000)
            fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,{filtros},adelay={ms}|{ms}[a{k}]")
            k += 1

        # som ambiente de cada cena (gerado a partir do vídeo)
        for i, c in enumerate(self.j["cenas"]):
            sfx = os.path.join(self.media, c["clip"] + "_sfx.wav")
            if not os.path.exists(sfx):
                continue
            v = c.get("vel", 1.0)
            fx = f"atrim={c['de']}:{c['ate']},asetpts=PTS-STARTPTS"
            if abs(v - 1) > 0.01:
                fx += f",atempo={v}"
            fx += f",volume={c.get('sfx_db', -6)}dB,afade=t=in:d=0.08,afade=t=out:st={max(c['dur'] - c.get('hold', 0) - 0.12, 0)}:d=0.12"
            add(sfx, fx, self.ini[i])
        # falas
        for fa in self.j["falas"]:
            ini = self.ini[fa["cena"]] + fa["t"]
            add(os.path.join(self.media, fa["a"] + ".mp3"), f"{filtro_cam},volume={fa.get('db', 0)}dB", ini)
        # sons do fechamento (sintetizados)
        P = self.ini_pausa
        fs = self.j["fecho"].get("sons", {})
        if self.cctv:
            add("aevalsrc='0.06*sin(2*PI*(260+160*t)*t)*(1-exp(-20*t))':s=48000", "volume=0dB",
                self.fim_cenas + 0.05, True, max(self.rec - 0.1, 0.3))
            add("aevalsrc='0.35*sin(2*PI*1750*t)*(lt(t,0.07)+gte(t,0.12)*lt(t,0.19))':s=48000", "volume=0dB", P, True, 0.25)
        for t0, d in fs.get("ticks", []):
            add("aevalsrc='0.16*sin(2*PI*2400*t)*exp(-500*mod(t,0.03))':s=48000", "volume=0dB", P + t0, True, d)
        for t0 in fs.get("impacto", []):
            add("aevalsrc='0.9*sin(2*PI*52*t)*exp(-3.5*t)+0.25*(random(0)*2-1)*exp(-25*t)':s=48000", "volume=-2dB",
                P + t0, True, 1.4)
        for t0 in fs.get("pop", []):
            add("aevalsrc='0.4*sin(2*PI*(600+900*exp(-30*t))*t)*exp(-22*t)':s=48000", "volume=-4dB", P + t0, True, 0.25)
        add("aevalsrc='0.07*(sin(2*PI*98*t)+0.6*sin(2*PI*147*t))*(0.7+0.3*sin(2*PI*0.5*t))':s=48000",
            f"afade=t=in:d=0.8,afade=t=out:st={self.pausa - 0.7}:d=0.7", P, True, self.pausa)
        fl.append("".join(f"[a{j}]" for j in range(k)) + f"amix=inputs={k}:normalize=0:duration=longest,"
                  f"apad=whole_dur={self.total},atrim=0:{self.total},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[mix]")
        out = os.path.join(self.b, "audio.wav")
        run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fl), "-map", "[mix]", out])
        return out

    # ---------- legendas e textos ----------
    def legendas(self):
        j = self.j
        ev = []
        srt = []
        # falas
        for n, fa in enumerate([x for x in j["falas"] if x.get("texto")], 1):
            a = self.ini[fa["cena"]] + fa["t"]
            b = a + dur(os.path.join(self.media, fa["a"] + ".mp3")) + 0.2
            ev.append(f"Dialogue: 2,{ts(a, False)},{ts(b, False)},Fala,,0,0,0,,{fa['texto']}")
            srt.append(f"{n}\n{ts(a)} --> {ts(b)}\n{fa['texto']}\n")
        # marcação grande de dia e hora no começo de cada cena
        for i, c in enumerate(j["cenas"]):
            if c.get("marca"):
                a = self.ini[i] + c.get("marca_de", 0.0)
                l1, l2 = c["marca"]
                ev.append(f"Dialogue: 1,{ts(a, False)},{ts(a + 1.9, False)},Marca,,0,0,0,,"
                          f"{{\\fad(120,280)}}{l1}\\N{{\\fs80\\c&H4DE1FF&}}{l2}")
        # gancho no topo da primeira cena
        if j.get("gancho"):
            g = j["gancho"]
            ev.append(f"Dialogue: 3,{ts(0.0, False)},{ts(g.get('ate', 3.2), False)},Gancho,,0,0,0,,"
                      f"{{\\fad(0,250)}}" + "\\N".join(g["linhas"]))
        # pensamento escrito (formato PO)
        for p in j.get("pensamento", []):
            ev.append(f"Dialogue: 3,{ts(p['de'], False)},{ts(p['ate'], False)},Pensa,,0,0,0,,{{\\fad(150,200)}}{p['txt']}")
        # fechamento
        P = self.ini_pausa
        f = j["fecho"]
        textos = list(f["textos"])
        if f.get("cta_de") is not None:
            c0 = f["cta_de"]
            y0 = f.get("cta_y", 860)
            textos += [
                {"de": c0, "y": y0, "tam": 62, "cor": "b", "txt": "Comenta"},
                {"de": c0, "y": y0 + 105, "tam": 108, "cor": "a", "txt": f.get("cta", "DIAGNÓSTICO")},
                {"de": c0 + 0.3, "y": y0 + 222, "tam": 40, "cor": "b", "txt": f.get("sub", ["entenda como ganhar mais dinheiro"])[0], "fonte": "r"},
                {"de": c0 + 0.3, "y": y0 + 272, "tam": 40, "cor": "b", "txt": f.get("sub", ["", "sem perder a agenda"])[1], "fonte": "r"},
                {"de": c0 + 0.55, "y": y0 + 420, "tam": 32, "cor": "c", "txt": "@gabrielcampaner", "fonte": "r"},
            ]
        for tx in textos:
            a = P + tx["de"]
            b = P + tx.get("ate", self.pausa)
            cor = COR[tx.get("cor", "b")]
            neg = "\\b0" if tx.get("fonte") == "r" else ""
            base = f"{{\\an5\\pos(540,{tx['y']})\\fs{tx['tam']}\\c{cor}{neg}"
            pop = "\\fscx118\\fscy118\\t(0,160,\\fscx100\\fscy100)\\fad(90,180)}"
            if "conta" in tx:
                alvo, pre, suf = tx["conta"]
                passos = 18
                dcont = tx.get("dcont", 0.6)
                for s in range(passos):
                    val = int(alvo * (s + 1) / (passos + 1))
                    a1 = a + dcont * s / passos
                    a2 = a + dcont * (s + 1) / passos
                    ev.append(f"Dialogue: 4,{ts(a1, False)},{ts(a2, False)},Fecho,,0,0,0,,{base}}}{pre}{fmt(val)}{suf}")
                ev.append(f"Dialogue: 4,{ts(a + dcont, False)},{ts(b, False)},Fecho,,0,0,0,,{base}{pop}{pre}{fmt(alvo)}{suf}")
            else:
                ev.append(f"Dialogue: 4,{ts(a, False)},{ts(b, False)},Fecho,,0,0,0,,{base}{pop}{tx['txt']}")
        ass = os.path.join(self.b, "textos.ass")
        with open(ass, "w", encoding="utf-8") as fh:
            fh.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
                     "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
                     "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                     "Alignment, MarginL, MarginR, MarginV, Encoding\n"
                     "Style: Fala,DejaVu Sans,54,&H004DE1FF,&H004DE1FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,1,2,90,90,520,1\n"
                     "Style: Marca,DejaVu Sans,108,&H00FFFFFF,&H00FFFFFF,&H50000000,&H00000000,-1,0,0,0,100,100,2,0,3,26,0,5,60,60,0,1\n"
                     "Style: Gancho,DejaVu Sans,50,&H00FFFFFF,&H00FFFFFF,&H70000000,&H00000000,-1,0,0,0,100,100,0,0,3,16,0,8,70,70,232,1\n"
                     "Style: Pensa,DejaVu Sans,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,1,5,80,80,0,1\n"
                     "Style: Fecho,DejaVu Sans,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,5,2,5,60,60,0,1\n\n"
                     "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            fh.write("\n".join(ev) + "\n")
        sp = os.path.join(self.saida, f"{self.id}.srt")
        open(sp, "w", encoding="utf-8").write("\n".join(srt))
        return ass, sp

    def final(self, vid, aud, ass, nome):
        out = os.path.join(self.saida, nome)
        vf = ["-vf", f"subtitles={ass}"] if ass else []
        run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", aud] + vf +
            ["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
             "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
             "-t", f"{self.total:.3f}", out])
        return out


def fmt(n):
    return f"{n:,}".replace(",", ".")


if __name__ == "__main__":
    r = Reel(sys.argv[1])
    print(json.dumps({"id": r.id, "inicios": [round(x, 2) for x in r.ini], "fim_cenas": round(r.fim_cenas, 2),
                      "pausa": round(r.ini_pausa, 2), "total": round(r.total, 2)}))
    aud = r.audio()
    ass, srt = r.legendas()
    print(r.final(r.video(True), aud, ass, f"{r.id}_PRONTA.mp4"))
    if "--limpa" in sys.argv:
        print(r.final(r.video(False), aud, None, f"{r.id}_LIMPA.mp4"))
