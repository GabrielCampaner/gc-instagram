# Calendário do Instagram da GC

Publicador grátis do Instagram de Gabriel Campaner. Os posts são criados com o Claude na pasta `Artes/GC`; este repositório
guarda o calendário e as imagens, e o GitHub Actions publica cada post no horário, pela API oficial do Instagram.

## Como funciona

- `calendario.json`: os posts (id, data e hora, tipo, legenda, mídias, status). Só sai o que está `agendado`, e só com `"ativo": true`.
- `midia/<slug>/NN.jpg`: as imagens em JPG (a API só aceita JPG). O repositório é público porque o Instagram busca as imagens por endereço.
- `publicados.json`: o registro do robô (id no Instagram, link, data, erro). Não edite à mão.
- `.github/workflows/publicar.yml`: roda a cada 10 minutos e publica o que já venceu. Atraso maior que 6 horas não sai (avisa por e-mail).
- `.github/workflows/renovar_token.yml`: toda segunda renova o token da Meta, que vale 60 dias.

Status dos posts: `agendado` (sai no horário), `pendente` (falta confirmar algo, não sai), `pausado` (tirado à mão, não sai).

## Uso no dia a dia (no computador)

```
cd Documents/Artes/GC
node _scripts/enviar_calendario.js Conteudo/Lote_03/lote03.js            # manda o lote (converte, grava, envia)
node _scripts/enviar_calendario.js Conteudo/Lote_03/lote03.js --liberar L3-06,L3-09   # libera pendências resolvidas
node ../gc-instagram/publicador/status.js                                # mostra o calendário
```

Para mudar data ou legenda, mude no arquivo do lote e mande de novo. Post já publicado nunca é mexido.

## Configuração (uma vez)

1. **Meta**: app próprio em developers.facebook.com com o caso de uso de Instagram (API com login do Instagram), a conta
   profissional conectada e um token gerado. O app fica em modo de desenvolvimento: só publica na própria conta, sem revisão.
2. **Segredo `IG_TOKEN`**: Settings > Secrets and variables > Actions > New repository secret, com o token da Meta.
3. **Teste**: Actions > Publicar no Instagram > Run workflow > `conferir` (lê a conta) e depois `teste` com um id (prepara o
   post no Instagram sem publicar).
4. **Ligar**: `"ativo": true` no `calendario.json`.
5. Opcional, **segredo `GH_PAT`**: token do GitHub (fine-grained, só este repositório, permissão Secrets: read and write). Só é
   preciso se a renovação semanal avisar que a Meta devolveu um token novo.

## Limites da API do Instagram

Carrossel até 10 imagens · legenda até 2.200 caracteres e 30 hashtags · até 50 publicações por dia · Stories sem figurinha
(enquete, caixinha e link continuam no app) · Reels por MP4 na pasta da mídia (tipo `reels`).
