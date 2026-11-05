# Painel do canal

Uma página (artefato do Claude, privada até você compartilhar) com todos os vídeos e Shorts, links do YouTube, status do agendamento e os links de venda. Todas as sessões e rotinas automáticas atualizam o **mesmo** link.

## Criar (uma vez, no onboarding)

1. `python3 pipeline/painel/build.py`
2. Publique `pipeline/painel/dist/index.html` com a ferramenta **Artifact** (ícone `chart`).
3. Grave o link retornado em `CANAL.md` → "Painel" → **Link do painel (artefato):** e faça commit.

## Atualizar (fim de toda rotina)

1. `python3 pipeline/painel/build.py`
2. Publique `pipeline/painel/dist/index.html` com a ferramenta **Artifact**, passando `url` = o link de `CANAL.md`. Na primeira vez em cada sessão, leia o artefato antes (`action: "read"`), como a ferramenta pede.
3. Se a sessão não tiver a ferramenta Artifact, pule e avise no resumo: o `registro/README.md` continua sendo a fonte de verdade.

`dist/` fica fora do Git. Nunca coloque chave, e-mail ou dado pessoal no painel.
