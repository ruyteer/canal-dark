# Onboarding: montando o seu canal dark

Este roteiro é para o Claude seguir na primeira sessão, conversando com o dono do canal. Faça **uma pergunta por vez**, em linguagem simples, e grave as respostas em `CANAL.md` assim que cada uma chegar. No fim, faça commit e push.

## 0. Antes de começar

- Rode `bash pipeline/setup.sh` e veja quais chaves já existem.
- Confirme que a sessão consegue fazer push (`git push --dry-run origin main`). Se não conseguir, explique que o repositório precisa ser uma cópia do usuário (botão **Use this template** ou **Fork** no GitHub, de preferência **privada**) e adicionado às fontes da sessão.

## 1. Nicho

Pergunte, nesta ordem:

1. Sobre o que é o canal? Se o usuário não souber, sugira 3 nichos de canal dark com base no que ele gosta e no que sabe (histórias reais, curiosidades, finanças, tecnologia, mistérios, história, ciência…), com um exemplo de título para cada.
2. Quem assiste (idade, o que quer, o que teme)?
3. Qual o tom (sério, misterioso, engraçado, provocador)?
4. Idioma do canal.
5. Algum tema proibido ou limite próprio?

Com isso, proponha de 5 a 10 **palavras-chave de pesquisa** e uma **linha editorial** de uma frase. Se `YOUTUBE_API_KEY` já existir, rode `python3 pipeline/research.py --days 14` para mostrar o que está viralizando com essas palavras e ajuste com o usuário.

## 2. Voz de escrita

Peça 3 áudios, vídeos ou textos que o dono já fez (ou 3 trechos de fala dele). Escreva em `CANAL.md` → "Voz de escrita": para quem fala (uma pessoa), como fala de verdade, palavras que nunca usa e que usa, o que nunca afirma. Mostre e ajuste.

## 2b. Voz clonada

- O usuário clona a própria voz (ou escolhe uma) no ElevenLabs e passa o **nome** e o **Voice ID** (o ID não é segredo; a chave da API é).
- Grave em `CANAL.md` no formato exato: ``voice_id `XXXXXXXX` ``.
- Gere uma amostra curta com `tts.py` e peça a opinião antes de seguir.

## 3. Chaves

Siga `docs/CONFIGURAR.md` com o usuário, passo a passo. **Nunca peça para colar uma chave no chat.** As chaves vão nas variáveis do ambiente do Claude e valem a partir da próxima sessão.

## 4. Oferta

- O canal vai vender o quê? Produto próprio (o Claude cria com `produto/` e a página com `vendas/`), afiliado ou só AdSense por enquanto.
- Se for produto próprio: tema, promessa, preço e plataforma de checkout (Kiwify, Kirvano, Cakto, Hotmart, Eduzz…).
- Sem link ainda: a rotina usa o marcador `[LINK DA OFERTA]`.

## 5. Agenda

- Quantos vídeos por semana e em que dias a rotina de produção roda.
- Horários de publicação (o upload sai sempre privado e agendado para o dia seguinte; o dono revisa antes).

## 6. Painel

Crie o painel do canal seguindo `pipeline/painel/README.md` e grave o link em `CANAL.md` → "Painel".

## 7. Rotinas automáticas

Explique as duas opções e deixe o usuário escolher:

- **Manual:** abrir uma sessão nova com este repositório e pedir "rode a rotina de produção" (ou "de análise").
- **Agendada:** criar tarefas agendadas no Claude (produção nos dias definidos, análise uma vez por semana). O repositório precisa estar nas fontes da tarefa para o push funcionar. Se a tarefa não conseguir fazer push, crie uma sessão fixa com o repositório como fonte e agende a tarefa para disparar nela.

Dica de consumo: produções usam bastante do limite do plano. Rotinas agendadas rodam bem num modelo mais leve e com no máximo 3 subagentes ao mesmo tempo.

## 8. Fechamento

- Confira que não sobrou **[DEFINIR]** essencial (nicho, palavras-chave, voz).
- Commit e push: `git commit -am "Onboarding do canal" && git push`.
- Diga ao usuário o próximo passo: "rode a rotina de produção".
