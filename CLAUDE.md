# Canal dark: instruções para o Claude

Este repositório é um modelo de canal dark: um canal no YouTube em que o dono não aparece. O Claude pesquisa, escreve, narra (voz clonada no ElevenLabs), edita (HyperFrames), sobe como **privado agendado para o dia seguinte** e acompanha os resultados.

## Primeira sessão

Se `CANAL.md` ainda tiver **[DEFINIR]** no nicho, nas palavras-chave ou na voz, conduza o `ONBOARDING.md` com o usuário antes de qualquer outra coisa.

## Antes de qualquer tarefa, leia nesta ordem

1. `CANAL.md`: nicho, público, tom, formatos, oferta e regras fixas. É a identidade do canal.
2. `aprendizados.md`: o que funcionou e o que não funcionou até agora. Pese isso em toda decisão.
3. `ROTINA.md`: o passo a passo de cada rotina (produção e análise).
4. `registro/videos.json`: o que já foi feito, para não repetir tema, título, fundo ou meme.

## Regras que nunca mudam

- **Todo upload é privado e agendado para o dia seguinte** (`upload.py --days 1 --at HH:MM`). Nunca publique na hora e nunca mude a visibilidade ou o agendamento de um vídeo já enviado: o dono do canal revisa, muda o horário ou publica antes, pelo Studio.
- **Nada de repetir.** Antes de escolher tema, título, gancho, fundos, memes, sons e música, compare com os últimos 10 vídeos em `registro/videos.json`. Varie formato, estrutura, cenário e ritmo. O YouTube pune conteúdo repetitivo.
- **Pesquisa sempre fresca.** Ideias novas saem de vídeos publicados nos últimos 14 dias (`pipeline/research.py`), nunca de memória ou de pesquisas antigas.
- **Registre tudo.** Cada vídeo e cada Short editado ou enviado entra em `registro/videos.json` (e na tabela de `registro/README.md`) com tema, roteiro, arquivos usados, link do YouTube e data. Faça commit e push no fim de cada rotina.
- **Chaves só por variável de ambiente** (`ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `YOUTUBE_API_KEY`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`, `UNSPLASH_ACCESS_KEY`, `PEXELS_API_KEY`). Nunca escreva uma chave em arquivo, commit, log ou mensagem. Se faltar uma, pare a etapa que depende dela e avise.
- **Oferta no meio de todo vídeo longo**, como descrito em `CANAL.md`. Se a oferta ainda não estiver definida lá, deixe o bloco marcado no roteiro e avise.
- **Sites que bloqueiam acesso automático** (403, captcha, "confirme que não é um robô"): não tente contornar. Use outra fonte ou avise.
- Não use conteúdo pago (clipes premium) sem a conta paga.
- **Trabalhe com subagentes em paralelo** na produção, como descrito em `ROTINA.md` → "Trabalho em paralelo". A sessão principal orquestra e é a única que faz commit, push, upload e registro.

## Ferramentas

- `pipeline/setup.sh`: instala o que a sessão precisa (rode primeiro em toda sessão nova).
- `pipeline/research.py`: virais recentes do nicho pela API oficial do YouTube.
- `pipeline/tts.py`: narração no ElevenLabs.
- `pipeline/assets.py`: busca e baixa fundos (Coverr, Mixkit), memes (MemeScreens), sons (Myinstants) e música (Mixkit).
- `pipeline/edit/`: modelo de edição no HyperFrames. `make_video.py` monta e renderiza a partir de um `plan.json`.
- `pipeline/upload.py`: sobe como privado, agendado para o dia seguinte.
- `pipeline/analytics.py`: puxa os números do canal.
- `pipeline/registry.py`: lê e grava o registro.
- `pipeline/thumbnail.py`: miniatura com foto de banco de imagens e frase de expectativa.
- `pipeline/painel/`: painel compartilhado (artefato) com vídeos, links e status. Atualize ao fim de cada rotina.
- `produto/`: criação do produto digital (e-book em PDF).
- `vendas/`: página de vendas com checkout (Kiwify, Kirvano, Cakto, Hotmart…).

Os arquivos de trabalho de cada vídeo ficam em `producao/<id>/` (o roteiro e o plano entram no Git; os vídeos e mídias brutas não, por tamanho).
