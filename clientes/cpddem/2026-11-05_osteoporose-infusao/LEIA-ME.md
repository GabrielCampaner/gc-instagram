# CPDDEM · Infusão para osteoporose · v2 (5/11/2026)

A v1 (só tipografia, sem foto, com texto técnico) foi recusada pelo Gabriel. A v2 muda a linha:

- **Humanizada**: fotos de pessoas reais (Adobe Stock), texto em conversa com o paciente e com a família, sem jargão.
- **Mais conteúdo útil**: além do "como funciona", entram benefícios e as dúvidas mais comuns, em formato de conversa.
- **CTA que se explica**: o último story diz o que fazer ("Toque no link abaixo para conversar"), tem uma base para a
  figurinha de link e o número por extenso para quem prefere digitar.
- **Marca presente**: a logo fica sempre sobre branco (painel ou cartão), com a identificação do diretor técnico-médico.

**Ainda com marcadores** (`[Nome]`, `[nº]`, `[endereço]`, `(85) 9XXXX-XXXX`): não publicar até fechar as pendências abaixo.

## Peças

| Arquivo | Tamanho | O que é |
|---|---|---|
| `CPDDEM_osteoporose_story_1de5_v2.png` | 1080 × 1920 | Gancho: "Recebeu o diagnóstico de osteoporose?" (foto avó e neta) |
| `CPDDEM_osteoporose_story_2de5_v2.png` | 1080 × 1920 | Como funciona: 3 passos (foto da infusão) |
| `CPDDEM_osteoporose_story_3de5_v2.png` | 1080 × 1920 | Benefícios: o que a pessoa encontra no CPDDEM |
| `CPDDEM_osteoporose_story_4de5_v2.png` | 1080 × 1920 | Dúvidas frequentes em balões de conversa |
| `CPDDEM_osteoporose_story_5de5_v2.png` | 1080 × 1920 | Agende sua avaliação: figurinha de link + número (foto da equipe) |
| `CPDDEM_osteoporose_story_unico_v2.png` | 1080 × 1920 | Versão resumida em um story só |
| `CPDDEM_osteoporose_whatsapp_v2.jpg` | 1080 × 1350 | Lista de transmissão: peça principal |
| `CPDDEM_osteoporose_whatsapp_duvidas_v2.jpg` | 1080 × 1350 | Lista de transmissão: dúvidas frequentes |
| `legenda_whatsapp.txt` | — | Texto para enviar junto (asteriscos = negrito no WhatsApp) |
| `previa_todas_as_pecas_v2.png` | — | Todas as peças lado a lado; nos stories com link, a figurinha aparece simulada |

Recomendação: no Instagram, publicar a sequência de 5 stories (uma ideia por tela). No WhatsApp, enviar as duas imagens
como foto, com HD ativado, e a legenda.

### Figurinha de link (stories 5 e único)

No app do Instagram: figurinha > Link > colar o `wa.me` do CPDDEM > texto personalizado "AGENDAR AVALIAÇÃO". Posicione
sobre a base azul-clara abaixo de "Toque no link…". A prévia mostra como fica.

## PSDs (não ficam no repositório)

`psd/CPDDEM_osteoporose_v2.psd` (Story único + 2 WhatsApp) e `psd/CPDDEM_osteoporose_sequencia_v2.psd` (5 stories) foram
enviados como anexo na conversa. Ficam fora do Git porque o repositório é público e a licença do Adobe Stock não permite
deixar a foto disponível para download como arquivo solto (dentro da arte publicada pode).

Ao abrir no Photoshop:
1. Clique em **Atualizar** quando ele avisar das camadas de texto.
2. DIN 2014 vem do Adobe Fonts (Regular, Demi, Demi Italic, Bold, Extra Bold); ative se pedir.
3. Grupos: Fundo, Foto, Grafismo, Painel, Logo, Textos, Passos, Benefícios, Dúvidas, CTA, Rodapé e Guias (oculto, com as
   áreas livres de 250 px no topo, 270 px na base e a área da figurinha).
4. Textos são editáveis, com quebra de linha manual. Painel, balões, botões, círculos e cartões são formas vetoriais.
5. Fotos, logo e ícones são camadas de pixel no tamanho final.

Exportação: Exportar como, sRGB. Stories em PNG; WhatsApp em JPG qualidade 90.

## Fotos (Adobe Stock, coleção gratuita, licenciadas na conta Adobe do Gabriel em 5/11/2026)

| Uso | ID |
|---|---|
| Story 1 · avó e neta | 436582561 |
| Story 2 e story único · paciente na infusão | 593175984 |
| Story 5 · enfermeira e paciente | 673613237 |
| WhatsApp principal · consulta | 671528341 |

As fotos são de modelos, por isso cada peça leva o selo "Imagem ilustrativa". Se o CPDDEM tiver foto real da sala de
infusão em boa resolução, ela pode entrar no lugar da foto do story 2.

## Textos para a direção técnica validar

- Passos: "O médico conversa com você e confirma se a infusão é indicada" / "Na veia, como um soro, numa poltrona
  confortável e com a equipe por perto" / "Você volta para tirar dúvidas e receber orientações".
- Benefício: "Uma alternativa ao tratamento em comprimidos, quando o médico indicar".
- Dúvida: "A aplicação dói? É feita na veia, parecida com tomar soro. A equipe acompanha você o tempo todo."

Mantido do brief: sem nome de medicamento, embalagem ou frequência de dose; sem promessa de resultado; sem imagem de queda
ou fratura; identificação do diretor técnico-médico em todas as peças.

## Pendências antes de publicar

- [ ] Nome, CRM-CE e RQE do diretor técnico-médico
- [ ] Número oficial de WhatsApp e link wa.me para a figurinha
- [ ] Endereço atual (o briefing de 4/11 registra mudança de sede)
- [ ] Os 12x valem para consulta e aplicação? Com ou sem juros? (as peças não dizem "sem juros")
- [ ] Aprovação da direção técnica para os textos acima
- [ ] O CPDDEM aplica com prescrição de médico externo? Define se sai uma versão para esse público
- [ ] Logo em vetor (AI, SVG ou EPS) com quem criou a marca

## Outros arquivos

`logo/` (PNG transparente recortado dos PDFs), `CPDDEM_cores.ase` (paleta para a Biblioteca CC "CPDDEM") e `_fonte/`
(código que gera as peças e os PSDs; para rodar, baixe as fotos pelos IDs acima e use `_fonte/recortes_fotos.py`).
