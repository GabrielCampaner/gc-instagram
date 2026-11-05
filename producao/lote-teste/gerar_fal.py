#!/usr/bin/env python3
"""Gera os quadros extras e os clipes do lote de teste pelo fal.ai.

Uso (precisa da variável de ambiente FAL_KEY):
  python3 producao/lote-teste/gerar_fal.py custo            # só mostra o custo, não gera nada
  python3 producao/lote-teste/gerar_fal.py quadros          # E-01_B e E-05_B, 2 variações cada
  python3 producao/lote-teste/gerar_fal.py videos [ids...]  # clipes cujo quadro já existe em quadros/

Clipes: Veo 3.1 Fast image-to-video, 1080p, 9:16, sem áudio (US$ 0,10/s).
Quadros: Nano Banana Pro edit, 2K, 9:16 (US$ 0,15 por imagem).
Cada pedido enviado fica em media/pedidos.json: rodar de novo retoma o pedido em vez de pagar outro.
"""
import base64, json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
QUADROS = os.path.join(AQUI, "quadros")
MEDIA = os.path.join(AQUI, "media")
PEDIDOS = os.path.join(MEDIA, "pedidos.json")
VEO = "fal-ai/veo3.1/fast/image-to-video"
NBP = "fal-ai/nano-banana-pro/edit"
NBP_T2I = "fal-ai/nano-banana-pro"  # sem imagem de entrada
USD_VIDEO_S = 0.10
USD_IMAGEM = 0.15
DOLAR = 5.48

spec = json.load(open(os.path.join(AQUI, "cenas.json")))


def chave():
    k = os.environ.get("FAL_KEY")
    if not k:
        sys.exit("Falta a variável de ambiente FAL_KEY.")
    return k


def http(metodo, url, corpo=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(url, data=dados, method=metodo, headers={
        "Authorization": "Key " + chave(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {url}: {e.read()[:500]!r}")


def data_uri(caminho):
    return "data:image/jpeg;base64," + base64.b64encode(open(caminho, "rb").read()).decode()


def carregar_pedidos():
    return json.load(open(PEDIDOS)) if os.path.exists(PEDIDOS) else {}


def salvar_pedidos(p):
    os.makedirs(MEDIA, exist_ok=True)
    json.dump(p, open(PEDIDOS, "w"), indent=1)


def esperar(endpoint, req_id):
    base = f"https://queue.fal.run/{endpoint.split('/')[0]}/{endpoint.split('/')[1]}/requests/{req_id}"
    while True:
        st = http("GET", base + "/status")
        if st.get("status") == "COMPLETED":
            return http("GET", base)
        if st.get("status") not in ("IN_QUEUE", "IN_PROGRESS"):
            raise RuntimeError(f"{req_id}: {st}")
        time.sleep(8)


def baixar(url, destino):
    urllib.request.urlretrieve(url, destino)
    print("  salvo", os.path.relpath(destino, AQUI))


def custo():
    total_s = sum(c["dur"] for c in spec["clipes"])
    n_img = 2 * len(spec["quadros_extra"])
    usd = total_s * USD_VIDEO_S + n_img * USD_IMAGEM
    print(f"Clipes: {len(spec['clipes'])}, {total_s} s x US$ {USD_VIDEO_S:.2f} = US$ {total_s * USD_VIDEO_S:.2f}")
    print(f"Quadros extras: {n_img} imagens x US$ {USD_IMAGEM:.2f} = US$ {n_img * USD_IMAGEM:.2f}")
    print(f"Total: US$ {usd:.2f} (cerca de R$ {usd * DOLAR:.0f}), uma tentativa por clipe")


def quadros(ids):
    pedidos = carregar_pedidos()
    alvo = [q for q in spec["quadros_extra"] if not ids or q["id"] in ids]
    for q in alvo:
        chave_p = "quadro:" + q["id"]
        if chave_p not in pedidos:
            imgs = [os.path.join(QUADROS, q["base"] + ".jpg")] if q.get("base") else []
            imgs += [os.path.join(RAIZ, p) for p in q.get("refs", [])]
            faltando = [p for p in imgs if not os.path.exists(p)]
            if faltando:
                print("sem imagem de entrada, pulando", q["id"], faltando)
                continue
            corpo = {"prompt": q["prompt"], "aspect_ratio": "9:16", "resolution": "2K",
                     "num_images": q.get("n", 2), "output_format": "jpeg"}
            if imgs:
                corpo["image_urls"] = [data_uri(p) for p in imgs]
            r = http("POST", f"https://queue.fal.run/{NBP if imgs else NBP_T2I}", corpo)
            pedidos[chave_p] = r["request_id"]
            salvar_pedidos(pedidos)
            print("enviado", q["id"], r["request_id"])
    for q in alvo:
        if "quadro:" + q["id"] not in pedidos:
            continue
        ep = NBP if (q.get("base") or q.get("refs")) else NBP_T2I
        res = esperar(ep, pedidos["quadro:" + q["id"]])
        for i, im in enumerate(res.get("images", []), 1):
            baixar(im["url"], os.path.join(QUADROS, f"{q['id']}_v{i}.jpg"))
    print("Escolha a variação e copie para quadros/<id>.jpg (ex.: E-01_B_v1.jpg -> E-01_B.jpg).")


def videos(ids):
    os.makedirs(MEDIA, exist_ok=True)
    pedidos = carregar_pedidos()
    fila = []
    for c in spec["clipes"]:
        if ids and c["id"] not in ids:
            continue
        saida = os.path.join(MEDIA, c["id"] + ".mp4")
        quadro = os.path.join(QUADROS, c["quadro"] + ".jpg")
        if os.path.exists(saida):
            continue
        if not os.path.exists(quadro):
            print("sem quadro, pulando", c["id"], "->", c["quadro"])
            continue
        chave_p = "video:" + c["id"]
        if chave_p not in pedidos:
            neg = c.get("negativo") or spec["negativo_cctv"] + (", standing up, leaving" if c.get("sentados") else "")
            r = http("POST", f"https://queue.fal.run/{VEO}", {
                "prompt": c["prompt"], "negative_prompt": neg, "image_url": data_uri(quadro),
                "aspect_ratio": "9:16", "resolution": "1080p", "duration": f"{c['dur']}s",
                "generate_audio": False})
            pedidos[chave_p] = r["request_id"]
            salvar_pedidos(pedidos)
            print("enviado", c["id"], r["request_id"])
        fila.append((c, pedidos[chave_p], saida))

    def um(item):
        c, rid, saida = item
        try:
            res = esperar(VEO, rid)
            baixar(res["video"]["url"], saida)
        except Exception as e:  # mostra e segue com os outros
            print("FALHOU", c["id"], e)

    with ThreadPoolExecutor(6) as ex:
        list(ex.map(um, fila))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "custo"
    {"custo": lambda: custo(), "quadros": lambda: quadros(sys.argv[2:]),
     "videos": lambda: videos(sys.argv[2:])}[cmd]()
