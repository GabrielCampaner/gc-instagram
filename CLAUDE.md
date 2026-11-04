# Notas para o Claude

## Ferramentas conectadas (série Circuito Interno · Os Doutores)

- **ElevenLabs (conector completo "Conector Claude Eleven Labs")**: vozes, falas, sons, imagens e vídeo no mesmo canvas.
  - Imagem: Nano Banana Pro (`gemini-3-pro-image`), 9:16, 2K. Edição com imagem de entrada custa mais que geração.
  - Vídeo: Veo 3.1 Fast (`veo-3.1-fast-generate-001`), 9:16, 1080p, **sem áudio** (o áudio sai do ElevenLabs). Kling 4.0 sai mais caro.
  - Canvas do piloto CI-01: flow `L5nXJaMctwi1nCxolgz8`.
  - Vozes salvas: CI · Kelly `29HxveKS0Gbg95FjkOLi`, CI · Dra. Renata `egWVlTU24Py3R6DyhmgD`, CI · Dona Marta `LWgMh66nVQMbF67LyvtY`.
  - Som de câmera nas falas: Audio Effects com `cheap_microphone` + `small_room` + distância 0,6 (gratuito).
- **Adobe (conector "Adobe")**: ferramentas online da Adobe (montar vídeo por linha do tempo, redimensionar, exportar, Photoshop e InDesign online). Não abre o Premiere do computador, não põe legenda nem texto no vídeo e só aceita arquivos do Creative Cloud (recusa links do ElevenLabs).
- **Gemini/Veo na conta Google**: existe na conta, mas não há conector do Gemini nas sessões do Claude. A rede do ambiente bloqueia `generativelanguage.googleapis.com`.
- **Rede do ambiente**: `elevenlabsusercontent.com` já foi liberado em Allowed domains (04/11/2026): dá para baixar vídeos e áudios do ElevenLabs e montar o Reel aqui com ffmpeg. `at.adobe.com` e `*.adobe.io` também foram liberados: dá para enviar arquivos direto para o Creative Cloud (asset_initialize_file_upload → PUT das partes → asset_finalize_file_upload). Os vídeos do CI-01 estão na pasta "Circuito Interno" do Creative Cloud.
- **Montagem do Reel**: `producao/ci-01/build/montar.py` monta a versão PRONTA (legendas, letreiro REC/CAM/hora, selo SIMULAÇÃO · IA, visual de câmera, cartela) e a LIMPA, mais o `.srt`. Espera os arquivos baixados em `producao/ci-01/media/` (s1–s6.mp4, l1–l7.mp3, n1–n4.mp3, amb, porta, passos, termica, manta) e grava em `producao/ci-01/saida/`. Para outro episódio, copie e troque a linha do tempo (CENAS, FALAS, SONS).

## Preferências

- Fazer tudo pelo Claude, sem passos manuais no Flow.
- Máximo realismo. Mostrar o custo em créditos antes de gerar.
- Página do projeto (roteiros, prompts, linha do tempo): https://claude.ai/artifact/Wd9YGWXSBaGoi1s8p8xbZA
- Reel final em `midia/<slug>/reels.mp4`, 1080×1920, 30 qps.
- Série Circuito Interno: vídeos curtos, com direcionamento claro e legenda caprichada. Cada cena abre com a marcação grande no meio da tela, "DIA 1" e "7:58 DA MANHÃ" (amarelo), por ~2 s; legendas das falas em amarelo com contorno preto, longe dos 20% de baixo; letreiro REC/CAM/hora no topo e selo "SIMULAÇÃO · IA".
- Chamada final: "Comenta DIAGNÓSTICO" em amarelo e, embaixo, pequeno em branco, "entenda como ganhar mais dinheiro sem perder a agenda" (não "Comenta 7"). Sem selfie no fim.

## Lições dos prompts de vídeo (CI-01)

- Quem entra pela porta de vidro sem abrir: deixar uma folha já aberta no quadro inicial e pedir "walks in through the open side, never touching the glass".
- Quem abre a porta: "pushes the glass entrance door open, the door swings back and closes"; dizer que só essa porta se mexe.
- Pessoa sumindo: pedir que fique visível do começo ao fim e pôr "person disappearing, ghost" no prompt negativo.
- Duas pessoas conversando de perto pode parecer beijo: manter distância ("about two meters apart, faces never close").
