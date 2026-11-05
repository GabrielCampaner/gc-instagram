# Recortes das fotos do Adobe Stock no tamanho exato de cada peça
# Uso: python3 recortes_fotos.py <pasta com os AdobeStock_*.jpeg> <pasta de saída>
import sys, os
from PIL import Image, ImageOps
F = sys.argv[1].rstrip('/') + '/'; OUT = sys.argv[2].rstrip('/') + '/'; os.makedirs(OUT, exist_ok=True)
def crop(src, name, w, h, cx, cy, zoom=1.0, espelhar=False):
    im = Image.open(F + f'AdobeStock_{src}.jpeg').convert('RGB')
    if espelhar: im = ImageOps.mirror(im)
    W, H = im.size; r = w / h
    ch = H / zoom; cw = ch * r
    if cw > W: cw = W; ch = cw / r
    x0 = min(max(cx * W - cw / 2, 0), W - cw); y0 = min(max(cy * H - ch / 2, 0), H - ch)
    im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((w, h), Image.LANCZOS).save(OUT + name, quality=94, subsampling=0)
    print(name, (w, h), 'recorte', [round(v) for v in (x0, y0, x0 + cw, y0 + ch)], 'espelhada' if espelhar else '')
crop('436582561', 'foto_familia_story.jpg', 1080, 880, 0.47, 0.5)                 # avó e neta (story 1)
crop('374753388', 'foto_equipe_story.jpg', 1080, 800, 0.50, 0.5, espelhar=True)   # equipe com paciente (story 2)
crop('374753388', 'foto_equipe_unico.jpg', 1080, 760, 0.50, 0.5, espelhar=True)   # story único
crop('1890701560', 'foto_medica_story.jpg', 1080, 800, 0.60, 0.0, zoom=1.2)       # médica e paciente (story 5)
crop('1890701560', 'foto_medica_whatsapp.jpg', 1080, 540, 0.50, 0.0)              # WhatsApp principal
