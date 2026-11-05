# Produto digital

O produto padrão é um **e-book em PDF** escrito pelo Claude a partir do que o canal já pesquisou e do que o público pergunta nos comentários.

## Passo a passo

1. **Tema e promessa** (com o dono do canal): o problema que o produto resolve, para quem, e um número concreto (ex.: "30 casos", "12 passos"). Confira os comentários e os vídeos de melhor desempenho em `registro/`.
2. **Sumário** com capítulos que seguem o mesmo caminho (ex.: problema → exemplo real → método → ação). Aprovação do dono antes de escrever.
3. **Escrita** em `produto/<slug>/livro.md` (formato no topo de `gerar_pdf.py`). Pode usar subagentes em paralelo, um por capítulo, com o mesmo guia de estilo. Todo fato com fonte pública conferida, como nos roteiros.
4. **Imagens** (opcional): fotos do Unsplash/Pexels via `pipeline/thumbnail.py search`, com crédito no fim do livro; ou ilustrações feitas em HTML.
5. **Identidade:** `produto/<slug>/tema.json` (cores e fontes). A mesma identidade vai para a página de vendas.
6. **Gerar:** `python3 produto/gerar_pdf.py <slug>` → `dist/livro.pdf`, `dist/capa.png`, `dist/mockup.png`. Abra o PDF (páginas em imagem com `pdftoppm -r 50 -png`) e confira capa, sumário e quebras.
7. **Vender:** siga `vendas/README.md`.

`livro.md` e `tema.json` entram no Git; `dist/` não. O PDF é o que você sobe na plataforma de checkout.
