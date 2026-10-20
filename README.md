# Calendário do Instagram da GC

Publicador grátis do Instagram de Gabriel Campaner. Os posts são criados com o Claude na pasta `Artes/GC`; este repositório
guarda o calendário e as imagens, e o GitHub Actions publica cada post no horário, pela API oficial do Instagram.

## Como funciona

- `calendario.json`: os posts (id, data e hora, tipo, legenda, mídias, status). Só sai o que está `agendado`, e só com `"ativo": true`.
- `midia/<slug>/NN.jpg`: as imagens em JPG (a API só aceita JPG). O repositório é público porque o Instagram busca as imagens por endereço.
- `publicados.json`: o registro do robô (id no Instagram, link, data, erro). Não edite à mão.
- `feed.json` e `insights.json`: últimos posts do perfil e métricas (alcance, visualizações, envios, salvos), atualizados pelo robô.
- `.github/workflows/publicar.yml`: publica o que já venceu. Ele se mantém sozinho em ciclo de 10 minutos (cada execução dispara a próxima, que espera no ambiente `intervalo`), porque o agendador do GitHub atrasa e pula execuções. Se chegar até 12 minutos antes do horário, espera e publica na hora. Atraso maior que 6 horas não sai (avisa por e-mail).
- `.github/workflows/renovar_token.yml`: toda segunda renova o token da Meta, que vale 60 dias.

Status dos posts: `agendado` (sai no horário), `pendente` (falta confirmar algo, não sai), `pausado` (tirado à mão, não sai).

## Uso no dia a dia (no computador)

```
cd Documents/Artes/GC
node _scripts/enviar_calendario.js                       # junta tudo de Conteudo/ e põe os novos nos próximos horários livres
node _scripts/enviar_calendario.js --refazer             # redistribui tudo o que não saiu, 2 por dia a partir de amanhã
node _scripts/enviar_calendario.js --liberar L3-06,GC-10 # libera pendências do "Confirmar"
node _scripts/enviar_calendario.js --palavras HORA,MAPA  # automações de palavra-chave confirmadas
node ../gc-instagram/publicador/status.js                # mostra o calendário
node ../gc-instagram/publicador/pedir.js conferir        # o robô confere a conta e responde aqui
node ../gc-instagram/publicador/pedir.js teste GC-04     # prepara o post no Instagram sem publicar
node ../gc-instagram/publicador/pedir.js insights        # alcance e engajamento agora (também roda todo dia às 23h41)
```

Horários: 08h30 (prefere post único) e 18h30 (prefere carrossel e Reels). Data comemorativa e Black Friday ficam na data
original. Cada post publicado (ou falha) vira um comentário na issue "Avisos de publicação", com quantos posts faltam.
O `pedir.js` grava `pedido.json`, envia, e o robô devolve a resposta em `ultimo_resultado.txt` (sem abrir o site).

## Configuração (uma vez)

1. **Meta**: app próprio em developers.facebook.com com o caso de uso de Instagram (API com login do Instagram), a conta
   profissional conectada e um token gerado. O app fica em modo de desenvolvimento: só publica na própria conta, sem revisão.
2. **Segredo `IG_TOKEN`**: Settings > Secrets and variables > Actions > New repository secret, com o token da Meta.
3. **Teste**: Actions > Publicar no Instagram > Run workflow > `conferir` (lê a conta) e depois `teste` com um id (prepara o
   post no Instagram sem publicar).
4. **Ligar**: `"ativo": true` no `calendario.json`.
5. **Ambiente `intervalo`**: Settings > Environments > intervalo > marque **Wait timer** com 10 minutos > Save protection rules. Sem isso o ciclo fica desligado e o robô depende só do agendador do GitHub.
6. Opcional, **segredo `GH_PAT`**: token do GitHub (fine-grained, só este repositório, permissão Secrets: read and write). Só é
   preciso se a renovação semanal avisar que a Meta devolveu um token novo.

## Limites da API do Instagram

Carrossel até 10 imagens · legenda até 2.200 caracteres e 30 hashtags · até 50 publicações por dia · Stories sem figurinha
(enquete, caixinha e link continuam no app) · Reels por MP4 na pasta da mídia (tipo `reels`).
