# Rotinas

Cada rotina roda numa sessão nova do Claude, sozinha. Comece sempre por:

1. **Acesso de escrita ao repositório, antes de qualquer outra coisa.** O repositório do canal precisa ser fonte da sessão em que a rotina roda (veja "Rotinas automáticas" no `ONBOARDING.md`). Clone (ou atualize) em `/home/user/canal-dark` e confirme com `git push --dry-run origin main`. Se der 403 e existir a ferramenta `add_repo`, chame-a com o dono e o nome do repositório e `access: push` e teste de novo. Se continuar 403, pare e avise que o repositório precisa ser adicionado às fontes da tarefa: não produza um vídeo que não vai poder ser registrado.
2. Rode o setup:

```bash
bash pipeline/setup.sh
```

e leia `CLAUDE.md`, `CANAL.md`, `aprendizados.md` e `registro/videos.json`.

Se `CANAL.md` ainda tiver **[DEFINIR]** no nicho ou nas palavras-chave, pare e avise o dono do canal no resumo final. Se só a oferta estiver em aberto, produza normalmente usando o CTA de inscrição no lugar dela e avise no resumo.

Se faltar alguma chave (o `setup.sh` mostra), faça tudo o que não depende dela e diga qual faltou. Sem `YOUTUBE_API_KEY`, não invente pesquisa: pare antes da etapa 2.

---

## Trabalho em paralelo (obrigatório na produção)

A sessão da rotina é a **orquestradora**: ela decide, integra e é a única que faz commit, push e upload. O que puder ser feito ao mesmo tempo vai para **subagentes em paralelo** (ferramenta `Agent`, tipo `general-purpose`, com `run_in_background: true`, várias chamadas na mesma mensagem). Os subagentes trabalham na mesma máquina e no mesmo repositório.

**Como delegar:**
- Cada subagente começa do zero: o prompt dele tem que trazer tudo. Caminho do vídeo (`/home/user/canal-dark/producao/<id>/`), o trecho do roteiro ou do mapa de edição que ele precisa, as regras de `CANAL.md` que valem para a tarefa (limites do nicho, nada de repetir, sites que bloqueiam não se contornam) e o que entregar.
- Cada um grava **só na própria pasta ou arquivo** e devolve um relatório curto (o que fez, arquivos, problemas). Subagente nunca faz commit, push, upload, nem mexe no `registro/`.
- Enquanto eles trabalham, a orquestradora segue com o que não depende deles. Ela só espera quando precisa do resultado.
- Se um subagente falhar, a orquestradora refaz aquela parte ou segue sem ela e avisa no resumo.

**A máquina tem 4 núcleos.** Cada render já usa os 4, então renders rodam **um de cada vez**. O ganho está em paralelizar todo o resto e em subir um arquivo enquanto o próximo renderiza.

**Divisão padrão:**

| Fase | Orquestradora | Em paralelo |
|---|---|---|
| A, depois da pesquisa e da ideia | Escreve o rascunho do roteiro | **Fontes:** abre cada fonte e confirma fatos → `fatos.md`. **Referências:** estuda os 3 a 5 vídeos virais do tema (título, duração, descrição, como abrem) → `referencias.md` |
| B, depois do roteiro final | Gera a narração (`tts.py`) e transcreve (`make_video.py --transcribe`) | **Fundos:** cenas do mapa de edição → `assets/bg/` + folha `bg.png` conferida. **Memes e sons:** → `assets/memes/`, `assets/sfx/` + folha conferida. **Música:** 1 lo-fi que não esteja nos últimos 5 vídeos → `assets/music/`. **Metadados:** títulos, descrições (oferta, fontes, hashtags) e tags → `upload-*.json`. **Miniatura:** busca de fotos e `thumb.jpg` (etapa 6) |
| C | Escreve o `plan.json` com os tempos da transcrição e roda as capturas do longo | **Revisão:** um subagente por Short roda `--snap --only short-N`, olha as folhas e aponta problemas |
| D | Renderiza em sequência: longo, short-1, short-2… | **Upload em segundo plano:** assim que um arquivo fica pronto, sobe com `upload.py` (Bash em segundo plano) enquanto o próximo renderiza |
| E | Registro, `aprendizados` se houver, commit e push | — |

## Rotina 1: produção de um vídeo

O `<id>` do vídeo é `AAAA-MM-DD-slug-curto` (ex.: `2026-11-12-salarios-dev`). Tudo do vídeo fica em `producao/<id>/`.

### 1. Pesquisa (sempre nova)

```bash
python3 pipeline/research.py --days 14 --out producao/<id>/pesquisa.json
```

- Usa as palavras-chave e os canais de `CANAL.md`. Só vídeos dos últimos 14 dias.
- Ordene por **multiplicador** (views ÷ inscritos do canal) e por **views por dia**, não por views brutas. Um canal pequeno com muitas views achou algo copiável.
- Para confirmar os candidatos, colete pelo menos 4 vídeos por canal e use `python3 pipeline/yt/swipe.py coletados.json --min 2.0` (múltiplo sobre a mediana do próprio canal; veja `docs/CONHECIMENTO-YOUTUBE.md` §6).
- Escolha 3 candidatos, nomeie o formato de cada um (os formatos estão em `CANAL.md`) e descarte os que repetem tema ou formato dos últimos 10 vídeos do registro.
- Escolha 1 e escreva o porquê em `producao/<id>/ideia.md` (referências com link, formato, ângulo próprio).
- Copie o **formato**, nunca o roteiro de ninguém.

### 2. Roteiro

Escreva `producao/<id>/roteiro.md` com:

- **Título:** escreva 10 e rode `python3 pipeline/yt/titulo.py titulos.txt` (use `--thumb` com a frase da miniatura); fique com o principal + 5 alternativas. **Descrição:** as duas primeiras linhas dizem o que o vídeo entrega nas palavras da busca, depois o link da oferta, os capítulos (`pipeline/yt/capitulos.py`, títulos reescritos) e as fontes; 3 a 5 hashtags. **Tags:** até 15, só para desambiguar.
- **Narração para o ElevenLabs:** texto corrido, com marcações de emoção entre colchetes (`[em tom provocador]`, `[rindo baixinho]`, `[pausa]`). Nada de colchetes com dados pessoais. 450 a 1.100 palavras (3 a 8 min).
- **Bloco da oferta** entre 40% e 60% do texto, como manda `CANAL.md`.
- **Mapa de edição:** para cada trecho, o fundo (cena concreta ou gameplay), se entra meme (qual emoção) e se entra som.
- **3 a 5 cortes para Shorts:** trechos de 20 a 55 s que funcionam sozinhos (abrem numa ideia completa, têm uma virada e terminam numa frase), cada um com título próprio, **primeira frase NOVA** pontuada no `hookscore.py`, texto de 2 segundos na tela diferente da fala e ponto de loop.

**Gancho:** escreva CINCO, cada um numa fórmula de `pipeline/yt/hooks.json`, pontue com `python3 pipeline/yt/hookscore.py ganchos.txt` e fique com os dois melhores (mostre as notas no `ideia.md`). Depois do gancho, a virada em 15 a 45 s sem apresentação, sem agradecimento e sem pedido de inscrição. Marque no mapa de edição o que aparece NA TELA em cada trecho. Fecho com um pedido só.

Regras: gancho confirma o título na primeira frase; um loop aberto; uma frase crua; fecho com pergunta específica; formato diferente do vídeo anterior; respeite a "Voz de escrita" de `CANAL.md`. Detalhes e porquês em `docs/CONHECIMENTO-YOUTUBE.md`.

**Checagem de fatos (obrigatória antes da narração):** abra cada fonte que o roteiro usa (WebFetch na página da notícia, do órgão ou do estudo) e confirme cada número, data, nome e caso no texto original. Resumo de busca não conta como fonte. O que não puder ser confirmado sai do roteiro. Liste em `roteiro.md` cada fato com o link onde foi confirmado.

### 3. Narração

```bash
python3 pipeline/tts.py producao/<id>/narracao.txt producao/<id>/narracao.mp3
```

`narracao.txt` é só o texto da narração (com as marcações). Confira a duração com `ffprobe`.

### 4. Mídias

```bash
python3 pipeline/assets.py coverr-search "phone at night"          # lista clipes gratuitos
python3 pipeline/assets.py coverr-get <slug> producao/<id>/assets/bg/<nome>.mp4
python3 pipeline/assets.py mixkit-video <tag>                       # ex.: video-game, abstract, neon
python3 pipeline/assets.py mixkit-get <id> producao/<id>/assets/bg/<nome>.mp4
python3 pipeline/assets.py meme-list [reactions|funny|effects|gaming|animals|dance]
python3 pipeline/assets.py meme-get <slug> producao/<id>/assets/memes/<nome>.webm --start 0 --dur 2.5
python3 pipeline/assets.py sfx-search "ihhh"
python3 pipeline/assets.py sfx-get <arquivo.mp3> producao/<id>/assets/sfx/<nome>.mp3 --dur 1.8
python3 pipeline/assets.py music-list ambient                       # ou hip-hop, chill, lo-fi-beats, corporate
python3 pipeline/assets.py music-get <id> producao/<id>/assets/music/fundo.mp3
python3 pipeline/assets.py sheet producao/<id>/assets/bg producao/<id>/bg.png   # folha de quadros para conferir
```

- **Olhe a folha de quadros** (`sheet`) de fundos e memes antes de usar. Clipe errado ou meme pequeno demais se corrige aqui (`meme-get --crop w:h:x:y`).
- Não repita fundo, meme ou música dos últimos 5 vídeos (veja o registro).
- **Música lo-fi é obrigatória** em todo vídeo longo e em todos os Shorts (o editor recusa plano sem música). Use `music-list lo-fi-beats`, `music-list chill` ou `music-list hip-hop` e escolha uma faixa instrumental calma; o editor repete a faixa até o fim do vídeo.
- Gameplay: use a indicada em `CANAL.md`; sem ela, fundos animados do Mixkit.

### 5. Edição e render

Escreva `producao/<id>/plan.json` (formato em `pipeline/edit/PLAN.md`) com os tempos tirados da transcrição, e rode:

```bash
python3 pipeline/edit/make_video.py producao/<id> --transcribe      # transcreve, monta, confere e tira capturas
python3 pipeline/edit/make_video.py producao/<id> --render          # renderiza o longo e os Shorts
```

- Depois do `--transcribe`, olhe as capturas (`producao/<id>/hf-longo/snaps/contact-sheet*.jpg`): meme visível e no lugar, legenda legível, cena certa.
- Faça o mesmo com **cada** Short antes do render (`make_video.py producao/<id> --snap --only short-N`) e olhe todas as folhas, não só a primeira.
- Corrija no `plan.json` as palavras que a transcrição errou (campo `fixes`), usando o roteiro como verdade.

### 6. Miniatura

Uma para o vídeo longo (os Shorts usam um quadro do próprio vídeo). Modelo: foto real do assunto + frase curta de expectativa, com a palavra-chave em amarelo, sublinhado e seta curva apontando para o detalhe da foto que gera a curiosidade (ex.: "IMAGINA CODAR *AQUI?*" sobre um escritório no alto de uma montanha).

```bash
python3 pipeline/thumbnail.py search "mountain cabin desk view"                  # termos em inglês funcionam melhor
python3 pipeline/thumbnail.py make producao/<id>/thumb.jpg --photo <id-da-foto> --text "IMAGINA CODAR *AQUI?*" --arrow 70,58
```

- **A frase** tem de 2 a 4 palavras (ideal 3), não repete o título (completa ele) e abre uma pergunta; confira com `python3 pipeline/yt/titulo.py --title "<título>" --thumb "<frase>"`: "ELE NÃO SABIA *DISSO*", "QUANTO CUSTOU *ISSO?*", "NUNCA FAÇA *ISSO*". Marque a palavra de destaque com `*asteriscos*`; sem marcação, a última palavra fica em destaque.
- **A foto** mostra o assunto concreto, com espaço livre do lado do texto (`--side left|right`). Escolha entre os resultados olhando as prévias. `--arrow x,y` (em % da imagem) aponta para o detalhe.
- Olhe o `thumb.jpg` antes de usar: texto legível no celular, seta no lugar certo, nada cobrindo o rosto ou o objeto.
- Ponha `"thumbnail": "producao/<id>/thumb.jpg"` no `upload-longo.json` e o crédito de `thumb-credito.txt` no fim da descrição.
- Não repita foto nem frase dos últimos 10 vídeos. Sem chave do Unsplash/Pexels, use um quadro do próprio vídeo com `--image`.

### 7. Upload (privado, agendado para o dia seguinte)

Horários de Brasília. O vídeo longo vai para amanhã às 18h; os Shorts se espalham por amanhã e depois de amanhã:

```bash
python3 pipeline/upload.py producao/<id>/render/longo.mp4   --meta producao/<id>/upload-longo.json   --days 1 --at 18:00 --registry <id>:longo
python3 pipeline/upload.py producao/<id>/render/short-1.mp4 --meta producao/<id>/upload-short-1.json --days 1 --at 12:00 --registry <id>:short-1
python3 pipeline/upload.py producao/<id>/render/short-2.mp4 --meta producao/<id>/upload-short-2.json --days 1 --at 20:00 --registry <id>:short-2
python3 pipeline/upload.py producao/<id>/render/short-3.mp4 --meta producao/<id>/upload-short-3.json --days 2 --at 12:00 --registry <id>:short-3
```

Shorts extras: `--days 2 --at 20:00`, `--days 3 --at 12:00`… Antes de agendar, veja no registro se já há algo marcado no mesmo dia e horário (produções seguidas podem colidir) e empurre para o próximo horário livre.

`upload-*.json` tem `title`, `description`, `tags` e, se houver, `thumbnail`. O script força `private` + `publishAt` e não aceita publicar na hora. Se ele avisar que o YouTube recusou o agendamento, diga isso no resumo.

### 8. Registro, painel e push

```bash
python3 pipeline/registry.py render-table
python3 pipeline/painel/build.py      # depois publique no link do painel (pipeline/painel/README.md)
git add -A && git commit -m "Vídeo <id>: <título>" && git push
```

Atualize o painel (`pipeline/painel/README.md`). No resumo final, liste: título, links privados do YouTube com o horário agendado, o que foi usado e o que o dono do canal precisa revisar.

---

## Rotina 2: análise

```bash
python3 pipeline/analytics.py --days 28 --out registro/metricas/$(date +%F).json
```

1. Para cada vídeo publicado, compare com a mediana do canal: views, retenção média (%), duração média assistida, inscritos ganhos, cliques na oferta (se houver link rastreável).
2. Separe **vídeo sem views** (problema de título/miniatura/gancho) de **vídeo com views e sem retenção** (problema de roteiro/ritmo).
2b. Para os 2 vídeos mais recentes com views suficientes, baixe a retenção (`python3 pipeline/analytics.py --retencao <ID> --out retencao.csv`) e leia com `python3 pipeline/yt/retencao.py retencao.csv --duration <s> --transcript producao/<id>/transcript.json`. Registre o maior vazamento e UMA mudança.
2c. **Comentários:** se a API/export trouxer comentários, faça a triagem em quatro pilhas (perguntas, correções, elogios, provocação), redija respostas e indique UM comentário para fixar (`docs/CONHECIMENTO-YOUTUBE.md` §7). O dono posta; a rotina não comenta.
3. Atualize `aprendizados.md` → "Do próprio canal", sempre com a evidência e o tamanho da amostra. Com menos de 5 vídeos, escreva "sinal fraco".
4. Se um formato ou tema ficar abaixo da mediana 3 vezes seguidas, marque como "evitar". Se ficar acima 2 vezes, "repetir com variação".
5. Atualize o painel (`pipeline/painel/README.md`), faça commit e push. No resumo, diga em 3 linhas o que mudou na estratégia.
