# Identidade do canal

> Este arquivo é o modelo. Na primeira sessão, o Claude conduz o `ONBOARDING.md` e preenche os campos **[DEFINIR]** junto com o dono do canal. Enquanto um campo essencial estiver em aberto, a rotina avisa e não inventa.

## Nicho e público

- **Nicho:** [DEFINIR]
- **Linha editorial:** [DEFINIR: o que cada vídeo entrega e o fio condutor do canal]
- **Palavras-chave de pesquisa** (usadas por `research.py`): [DEFINIR, 5 a 10 termos, separados por vírgula]
- **Canais de referência do nicho:** a primeira produção preenche com os 5 a 10 canais que mais aparecem com multiplicador alto em `research.py`.
- **Público:** [DEFINIR: quem é, idade, o que quer, o que teme]
- **Tom:** [DEFINIR]
- **Idioma:** [DEFINIR, ex.: português do Brasil]
- **Voz (ElevenLabs):** [DEFINIR: nome da voz], voice_id `[DEFINIR]` (não é segredo; a chave da API é). É a única fonte da voz para o `tts.py`.

### Voz de escrita (todo roteiro respeita)

- **Para quem eu falo:** [DEFINIR: UMA pessoa, descrita com precisão, não "o público"]
- **Como eu falo de verdade:** [DEFINIR: cole trechos reais de áudios ou vídeos do dono; se não houver, a rotina pede três e escreve esta seção]
- **Palavras que eu nunca uso:** [DEFINIR, ex.: "game-changer", "bora mergulhar"]
- **Palavras e cacoetes que eu uso:** [DEFINIR]
- **O que eu nunca afirmo:** [DEFINIR: números sem fonte, resultados que não são meus, ferramentas que não usei]

### Limites (obrigatórios em qualquer nicho)

- **Nada de dado inventado.** Números, casos e citações só com fonte pública aberta e confirmada (veja a checagem de fatos em `ROTINA.md`).
- **Nada que ensine a causar dano** (golpes, invasões, fraudes, riscos à saúde): fale pelo lado de quem se protege ou aprende.
- **Sem expor pessoas comuns.** Vítimas e anônimos não são nomeados.
- [DEFINIR: limites próprios do nicho]

## Oferta (monetização além do AdSense)

- **Oferta principal:** [DEFINIR: produto próprio em `produto/` ou afiliado]
- **Ofertas secundárias:** [DEFINIR ou "nenhuma"]
- **Link da oferta principal:** [DEFINIR: página de vendas de `vendas/` ou checkout]
- **Onde entra no vídeo:** entre 40% e 60% da duração, logo depois de um pico de valor. Nunca no gancho.
- **Como entra:** 15 a 25 segundos de narração ligando o problema do vídeo ao produto, sem quebrar o tom. Na tela, um cartão discreto "Link na descrição".
- **Enquanto o link não existir:** o roteiro cita a oferta normalmente e a descrição leva o marcador `[LINK DA OFERTA]`, para o dono trocar antes de publicar.

## Formato dos vídeos

- **Vídeo longo:** 3 a 8 minutos, 1920×1080, 30 fps.
- **Shorts:** no mínimo 3 por vídeo longo, de 20 a 55 segundos, 1080×1920, com gancho próprio nos primeiros 2 segundos.
- **Narração:** voz clonada no ElevenLabs, modelo `eleven_v4` (padrões do `tts.py`), com marcações de emoção entre colchetes no texto.
- **Fundo:** a fala manda na imagem. Fala neutra = gameplay ou fundo animado. Fala concreta = cena do Coverr mostrando exatamente aquilo. Troca de cena a cada 3 a 8 segundos, com zoom lento.
- **Memes:** do MemeScreens, recortados do fundo verde, no máximo 1 a cada 20 segundos, só em picos.
- **Sons:** de meme, do Myinstants, no máximo 6 por vídeo longo, sempre abaixo da voz.
- **Música:** lo-fi instrumental (Mixkit) do começo ao fim, volume 0.12 a 0.16; trocar de faixa a cada vídeo.
- **Legenda:** minimalista, 1 a 3 palavras por vez, branca com a palavra falada destacada.
- **Gameplay:** [DEFINIR: gravações próprias, se houver]. Sem elas, fundos animados do Mixkit.
- **Miniatura:** foto de banco de imagens + frase curta que gera expectativa (veja `pipeline/thumbnail.py`).

## Títulos e roteiro

Formatos que comprovadamente funcionam (veja `aprendizados.md`). Alterne: nunca o mesmo formato duas vezes seguidas.

- **Provocação na 2ª pessoa:** "Talvez você não queira tanto assim…"
- **Pergunta-dilema:** "Você quer X ou só gosta de Y?"
- **"Por que X vai te SALVAR"**
- **Escolha com números:** "Qual desses você aceitaria?"
- **Mistério com lacuna:** "O caso que ninguém entendeu… até descobrirem isso"
- **Desafio público em série:** "Vou fazer X por 30 dias"

Regras: gancho nos primeiros 10 s, sem agradecimento e sem falar do cenário; um loop aberto fechado mais à frente; uma frase crua e recortável; fecho com micro-ação e pergunta específica para os comentários.

## Agenda

- **Produção:** [DEFINIR: dias e horário das produções]
- **Horários de publicação agendada** (o upload sai privado e agendado): vídeo longo no dia seguinte às [DEFINIR, ex.: 18:00]; Shorts às [DEFINIR, ex.: 12:00 e 20:00].

## Painel

- **Link do painel (artefato):** [DEFINIR: criado no onboarding com `pipeline/painel/`]
