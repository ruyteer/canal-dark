# Formato do `plan.json`

Fica em `producao/<id>/plan.json`. Todos os tempos são em segundos da narração do vídeo longo. Caminhos são relativos a `producao/<id>/`.

```json
{
  "accent": "#FFD43B",
  "font": "Inter",
  "caption_words": 3,
  "fixes": { "Equal": "E qual", "acordar": "a cor" },
  "longo": {
    "bg": [
      { "start": 0.0, "end": 5.0, "file": "assets/bg/celular-noite.mp4", "media_start": 2 }
    ],
    "memes": [
      { "start": 16.7, "end": 19.0, "file": "assets/memes/rock.webm", "kind": "side" }
    ],
    "sfx": [
      { "start": 17.75, "file": "assets/sfx/ihhh.mp3", "volume": 0.5 }
    ],
    "music": { "file": "assets/music/lofi.mp3", "volume": 0.14, "media_start": 0 },
    "offer": { "start": 95.0, "end": 115.0, "text": "Link na descrição" }
  },
  "shorts": [
    { "name": "short-1", "start": 44.0, "end": 72.0, "hook": "O filtro de luz azul não resolve nada" }
  ]
}
```

- **`bg`**: cobre a narração inteira, sem buracos. `media_start` é de onde o clipe começa. Clipes mais curtos que o trecho congelam no último quadro: divida o trecho ou use outro clipe.
- **`memes`**: `kind` é `side` (lado direito; centralizado no vertical), `center` (grande no meio) ou `full` (tela cheia, para cartelas como "Much later…"). Arquivos `.webm` com transparência vêm de `assets.py meme-get`.
- **`sfx`**: sons curtos; o volume fica entre 0.35 e 0.6.
- **`music`**: obrigatória, lo-fi instrumental. Toca do começo ao fim (repete a faixa se ela for mais curta que o vídeo). Volume 0.12 a 0.16 (padrão 0.14).
- **`offer`**: o cartão aparece nesse intervalo, que deve coincidir com o bloco da oferta na narração.
- **`fixes`**: troca palavras que a transcrição errou. O valor pode ter mais de uma palavra; o tempo é dividido entre elas.
- **`shorts`**: cada um usa o trecho `[start, end]` do vídeo longo, com os mesmos fundos, memes e sons. `hook` é o texto fixo no topo do Short (opcional).
- **`accent`** e **`font`**: varie entre vídeos. Fontes disponíveis: Inter, Montserrat, Outfit, Nunito, Oswald, League Gothic, Archivo Black, Poppins, Roboto, Lato, Open Sans.
