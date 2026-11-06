# Canal dark com o Claude

Modelo de canal no YouTube em que você não aparece: o Claude pesquisa o que está viralizando no seu nicho, escreve o roteiro, narra com a sua voz clonada (ElevenLabs), edita com fundos, memes, sons, música e legenda dinâmica (HyperFrames), faz a miniatura, sobe **privado e agendado para o dia seguinte** (você revisa antes) e analisa os resultados. Também cria o seu produto digital e a página de vendas com checkout.

## Como usar

1. No GitHub, clique em **Use this template** (ou **Fork**) e crie a sua cópia, de preferência **privada**.
2. Abra o Claude Code (claude.ai/code) com a sua cópia como repositório.
3. Diga: **"vamos configurar o meu canal"**. O Claude segue o [`ONBOARDING.md`](ONBOARDING.md): nicho, público, voz, chaves, oferta, agenda e painel.
4. Depois, é só pedir **"rode a rotina de produção"** (ou agendar como tarefa recorrente).

## O que tem aqui

| Parte | O que faz |
|---|---|
| Produção | Pesquisa (últimos 14 dias) → roteiro com checagem de fatos e oferta → narração → mídias → edição → vídeo longo + 3 Shorts → miniatura → upload privado agendado → registro |
| Análise | Números do canal → `aprendizados.md` → ajusta as próximas ideias |
| Qualidade de YouTube | Ganchos pontuados (21 fórmulas), título e miniatura como par, Shorts que sobrevivem sozinhos, retenção lida por momento ([`docs/CONHECIMENTO-YOUTUBE.md`](docs/CONHECIMENTO-YOUTUBE.md), ferramentas em `pipeline/yt/`) |
| Painel | Página compartilhada com todos os vídeos, links e status ([`pipeline/painel/`](pipeline/painel/README.md)) |
| Produto | E-book em PDF criado pelo Claude ([`produto/`](produto/README.md)) |
| Vendas | Página de vendas com checkout Kiwify, Kirvano, Cakto, Hotmart… ([`vendas/`](vendas/README.md)) |

## Configuração

Passo a passo em [`docs/CONFIGURAR.md`](docs/CONFIGURAR.md): Google Cloud (YouTube Data + Analytics), ElevenLabs, Unsplash (miniaturas) e as chaves no ambiente. **Nenhuma chave vai no chat nem no repositório.**

## Estrutura

```
CLAUDE.md            regras para o Claude
ONBOARDING.md        primeira sessão: configura o canal com você
CANAL.md             nicho, oferta, formato, tom (preenchido no onboarding)
aprendizados.md      o que funciona (atualizado pela análise)
ROTINA.md            passo a passo das rotinas
pipeline/            scripts (pesquisa, narração, mídias, edição, miniatura, upload, análise, registro, painel)
pipeline/yt/         ganchos, título+miniatura, capítulos, retenção, virais (adaptado do youtube-agent-skill, MIT)
pipeline/edit/       modelo de edição no HyperFrames
produto/             criação do produto digital
vendas/              página de vendas com checkout
producao/<id>/       roteiro, plano e pesquisa de cada vídeo (mídias e renders ficam fora do Git)
registro/            tudo que foi editado e enviado, com links
```

## Regras que o Claude segue

- Upload sempre privado e agendado; nunca publica na hora.
- Nada de dado inventado: todo fato é conferido na fonte.
- Não repete tema, fundo, meme ou música dos últimos vídeos.
- Não contorna sites que bloqueiam acesso automático e não usa conteúdo pago sem conta.
