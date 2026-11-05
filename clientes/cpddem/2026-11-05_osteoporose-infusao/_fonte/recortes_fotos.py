# Recortes das fotos do Adobe Stock no tamanho exato de cada peça
import sys
from PIL import Image
# Uso: python3 recortes_fotos.py <pasta com os AdobeStock_*.jpeg>  →  grava em ./assets/
import os
F = sys.argv[1].rstrip('/') + '/'; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets') + '/'; os.makedirs(OUT, exist_ok=True)
def crop(src, name, w, h, cx, cy, zoom=1.0):
    im = Image.open(F + f'AdobeStock_{src}.jpeg').convert('RGB'); W, H = im.size
    r = w / h
    ch = H / zoom; cw = ch * r
    if cw > W: cw = W; ch = cw / r
    x0 = min(max(cx * W - cw / 2, 0), W - cw); y0 = min(max(cy * H - ch / 2, 0), H - ch)
    out = im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((w, h), Image.LANCZOS)
    out.save(OUT + name, quality=94, subsampling=0)
    print(name, (w, h), 'src box', [round(v) for v in (x0, y0, x0 + cw, y0 + ch)])
crop('436582561', 'foto_familia_story.jpg', 1080, 880, 0.47, 0.5)
crop('593175984', 'foto_infusao_story.jpg', 1080, 800, 0.45, 0.5)
crop('593175984', 'foto_infusao_unico.jpg', 1080, 760, 0.45, 0.5)
crop('673613237', 'foto_equipe_story.jpg', 1080, 800, 0.52, 0.5)
crop('671528341', 'foto_consulta_whatsapp.jpg', 1080, 540, 0.55, 0.30)
