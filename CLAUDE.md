# Notas para o Claude

## Ferramentas conectadas (série Circuito Interno · Os Doutores)

- **ElevenLabs (conector completo "Conector Claude Eleven Labs")**: vozes, falas, sons, imagens e vídeo no mesmo canvas.
  - Imagem: Nano Banana Pro (`gemini-3-pro-image`), 9:16, 2K. Edição com imagem de entrada custa mais que geração.
  - Vídeo: Veo 3.1 Fast (`veo-3.1-fast-generate-001`), 9:16, 1080p, **sem áudio** (o áudio sai do ElevenLabs). Kling 4.0 sai mais caro.
  - Canvas do piloto CI-01: flow `L5nXJaMctwi1nCxolgz8`.
  - Vozes salvas: CI · Kelly `29HxveKS0Gbg95FjkOLi`, CI · Dra. Renata `egWVlTU24Py3R6DyhmgD`, CI · Dona Marta `LWgMh66nVQMbF67LyvtY`.
  - Som de câmera nas falas: Audio Effects com `cheap_microphone` + `small_room` + distância 0,6 (gratuito).
- **Adobe (conector "Adobe")**: ferramentas online da Adobe (montar vídeo por linha do tempo, redimensionar, exportar, Photoshop e InDesign online). Não abre o Premiere do computador, não põe legenda nem texto no vídeo e só aceita arquivos do Creative Cloud (recusa links do ElevenLabs).
- **Gemini/Veo na conta Google**: existe na conta, mas não há conector do Gemini. A API (`generativelanguage.googleapis.com`) responde daqui desde 04/11/2026, só falta a chave (`GEMINI_API_KEY`, do AI Studio), cobrada à parte do Google AI Pro: Nano Banana Pro US$ 0,134 por imagem 1K/2K.
- **fal.ai**: `queue.fal.run` responde daqui; precisa de `FAL_KEY` nas variáveis do ambiente (só vale numa sessão nova). Veo 3.1 Fast image-to-video 1080p sem áudio US$ 0,10/s (o endpoint sai do ar no fal em 17/11/2026); Nano Banana Pro edit US$ 0,15 por imagem. Script pronto: `producao/lote-teste/gerar_fal.py`.
- **Comparação de preço (04/11/2026)**: ElevenLabs cobra ≈ US$ 0,11/s no Veo Fast (quase igual ao fal), mas imagem com referência custa 1.827 a 3.045 créditos (US$ 0,33 a 0,55), 2 a 3 vezes o fal/Gemini. Preferir fal/Gemini para imagem e vídeo quando houver chave; ElevenLabs para voz e som.
- **Saldo do ElevenLabs**: conferir antes de rodar lote. Em 04/11/2026 a cota do plano (124.553 créditos) acabou no meio dos quadros do lote de teste.
- **Rede do ambiente**: `elevenlabsusercontent.com` já foi liberado em Allowed domains (04/11/2026): dá para baixar vídeos e áudios do ElevenLabs e montar o Reel aqui com ffmpeg. `at.adobe.com` e `*.adobe.io` também foram liberados: dá para enviar arquivos direto para o Creative Cloud (asset_initialize_file_upload → PUT das partes → asset_finalize_file_upload). Os vídeos do CI-01 estão na pasta "Circuito Interno" do Creative Cloud.
- **Montagem do Reel**: `producao/ci-01/build/montar.py` monta a versão PRONTA (legendas, letreiro REC/CAM/hora, selo SIMULAÇÃO · IA, visual de câmera, cartela) e a LIMPA, mais o `.srt`. Espera os arquivos baixados em `producao/ci-01/media/` (s1–s6.mp4, l1–l7.mp3, n1–n4.mp3, amb, porta, passos, termica, manta) e grava em `producao/ci-01/saida/`. Para outro episódio, copie e troque a linha do tempo (CENAS, FALAS, SONS).

## Preferências

- Fazer tudo pelo Claude, sem passos manuais no Flow.
- Não depender só do ElevenLabs: usar fal.ai, Gemini etc. quando sair mais barato com a mesma qualidade.
- Máximo realismo. Mostrar o custo em créditos antes de gerar.
- Página do projeto (roteiros, prompts, linha do tempo): https://claude.ai/artifact/Wd9YGWXSBaGoi1s8p8xbZA
- Reel final em `midia/<slug>/reels.mp4`, 1080×1920, 30 qps.
- Série Circuito Interno: vídeos curtos, com direcionamento claro e legenda caprichada. Cada cena abre com a marcação grande no meio da tela, "DIA 1" e "7:58 DA MANHÃ" (amarelo), por ~2 s; legendas das falas em amarelo com contorno preto, longe dos 20% de baixo; letreiro REC/CAM/hora no topo e selo "SIMULAÇÃO · IA".
- Chamada final (desde 05/11/2026), em três ações na ordem: "➤ Encaminha pra quem precisa ver", "♥ Curte aqui" e "e comenta DIAGNÓSTICO" (DIAGNÓSTICO grande em amarelo); embaixo, pequeno em branco, "entenda como ganhar mais dinheiro sem perder a agenda". Na legenda do post: "Manda pra quem precisa ver, curte aqui e comenta DIAGNÓSTICO que eu te mando o nível da tua clínica." Nada de "Comenta 7". Sem selfie no fim.
- O CI-01 já foi publicado e está fechado: não mexer mais nele. Ele é a referência de formato para os próximos.
- Público pagante: doutores de 35 a 55 anos que ainda investem, vivem na correria, atendem muito plano, fazem conta e não sabem se o mês fechou (mentalidade antiga, mas bom pagante). Personagens dessa idade.
- Cenários de alto padrão (mármore, madeira, clínica chique) para contrastar com a dor. Evitar clínica com cara de popular ou antiga. Dores fortes do dia a dia: investiu na clínica e não teve retorno, tráfego pago sem medir conversão, desconto por medo de falar preço, faturamento sem saber se sobrou.
- Todo vídeo sai com três peças: o Reel, a capa (1080×1920, manchete dentro da faixa central 3:4) e a legenda do post (primeira linha forte, história, conta, dica prática, chamada, aviso de IA).
- Abertura sem tela preta: a frase de gancho vai no topo da primeira cena. Fechamento forte: o último quadro congela, a câmera dá zoom em REC, a gravação "pausa", a conta aparece com os números subindo, depois a frase e a chamada.

## Lote de teste (5S-01, CI-09, PO-02, E-01, E-02, E-05)

- Tudo em `producao/lote-teste/`: `quadros/` (quadros iniciais escolhidos), `cenas.json` (prompts dos 18 clipes e dos 2 quadros extras), `gerar_fal.py`.
- Canvas no ElevenLabs: flow `OXRmzVQrrGmtzwtid4ac`, com os 13 clipes do 5S-01, CI-09, PO-02, E-01 e E-02 já ligados ao quadro inicial. Os 5 do E-05 só estão no `cenas.json`.
- Referências dos personagens (recortes dos carrosséis): `producao/refs/`. O Gabriel é gerado como nos carrosséis: sem óculos, camisa azul-marinho de manga longa, relógio. Sempre à esquerda do quadro; o doutor à direita.
- 05/11/2026: os 3 sem o Gabriel viraram roteiros novos de alto padrão: CI-11 (Dra. Helena, clínica nova com agenda de plano), CI-12 (Dr. Otávio, R$ 15 mil de tráfego sem medir) e CI-13 (Dra. Sofia, desconto que ninguém pediu), mais o PO-02 (Dr. Caio no carro). O CI-02 (Dr. Mauro, clínica simples) e o CI-09 (o clipe saiu com balões roxos falsos no celular) ficaram de reserva. Com o Gabriel: E-06, E-02 e E-04, esperando a gravação da voz dele.
- Esteira, tudo pelo fal.ai (chave em `FAL_KEY`): `gerar_fal.py quadros|videos <ids>` (Nano Banana Pro e Veo 3.1 Fast), `falar_fal.py` (Eleven v4 com vozes da biblioteca, `falas.json`), `sons_fal.py` (Mirelo SFX: som ambiente gerado a partir do próprio vídeo). Montagem: `producao/pipeline/montar_ci.py producao/lote-teste/montagem/<id>.json`; capas: `producao/pipeline/capa.py producao/lote-teste/montagem/capas.json`. Saída em `producao/lote-teste/saida/`; legendas de post em `producao/lote-teste/legendas_post.md`.
- O Veo às vezes barra um clipe por "content checker" (aconteceu com o tablet de desenho de corpo da Dra. Sofia); refazer o pedido costuma passar. Às vezes ele inventa letreiro na tela: cortar na montagem (`crop` no JSON) em vez de gerar de novo.
- 05/11/2026: E-02 (Helena), E-04 (Sofia) e E-06 (Renata) prontos com a voz gravada do Gabriel, em `midia/e-0*/`. As gravações dele ficam em `producao/lote-teste/gravacoes/` (fora do Git: o repositório é público). Para cortar as falas: transcrição com tempo por palavra (`fal-ai/whisper`, áudio em mp3) e as pausas do `silencedetect`; a voz dele entra 2,5 dB abaixo para igualar à dos doutores.
- Vozes por personagem: Helena "Isabela" `Pxxu743NJcLUqO1QxfD6`, Sofia "Sofia - Natural" `n2a9VtkZLl8j1FSXHsL7`, Otávio "Kenn" `R3mQ9kzdIW8y3atS1Ec2`, Caio "Cirilo" `1DXriIY2zhyCt1cj8onn` (biblioteca, servem no fal). A Renata é a voz salva do CI-01, só no ElevenLabs.
- Não pôr nomes de pessoas no prompt de vídeo: o Veo escreveu "GABRIEL" e "Dra. Helena" na tela. Descrever ("o homem de camisa azul à esquerda"). Doutor que reage precisa estar de frente para a câmera: se o quadro deixar alguém de costas, pedir câmera na parede lateral.
- Sincronia labial (desde 05/11/2026): toda fala passa pelo sync-3 (`fal-ai/sync-lipsync/v3`, US$ 8/min) com o áudio real, apontando o rosto de quem fala (`options.active_speaker_detection.coordinates` no primeiro quadro). Script: `producao/lote-teste/sincronia_fal.py CLIPE FALA INICIO X Y SAIDA`. Testado na fala do preço da Sofia (E-04): ficou natural. No prompt do clipe, quem ouve fica de boca fechada.
- O Gabriel dos vídeos precisa sair das fotos reais dele (os carrosséis eram imagens de IA e não parecem com ele; ele usa óculos). Esperando as fotos e um vídeo curto dele falando.
- Formato "Os Doutores em cena": etiquetas de nome (GABRIEL / DRA. X) depois da marcação, zoom digital em quem ouve (`zoom` na cena do JSON), marcação só na primeira cena (é uma reunião contínua).

## Lições dos prompts de vídeo (CI-01)

- Quem entra pela porta de vidro sem abrir: deixar uma folha já aberta no quadro inicial e pedir "walks in through the open side, never touching the glass".
- Quem abre a porta: "pushes the glass entrance door open, the door swings back and closes"; dizer que só essa porta se mexe.
- Pessoa sumindo: pedir que fique visível do começo ao fim e pôr "person disappearing, ghost" no prompt negativo.
- Duas pessoas conversando de perto pode parecer beijo: manter distância ("about two meters apart, faces never close").
