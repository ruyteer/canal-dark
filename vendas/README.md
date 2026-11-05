# Página de vendas

Cada produto tem uma página com a **mesma estrutura** (a que converte) e uma **identidade visual própria** (cores, fontes, raio, imagens). O Claude escreve o `pagina.json`, gera e confere.

## Estrutura (não mude a ordem)

1. **Topo:** marca + botão de compra sempre visível.
2. **Hero:** gancho em uma frase forte, subtítulo com um número e a promessa, botão ("Quero…"), formato ("E-book em PDF · acesso imediato"), preço e parcelas, mockup do produto.
3. **Faixa corrida** com o nome de todos os itens (capítulos, casos, aulas).
4. **Amostra interativa** ("Experimente — Chegue mais perto."): abas com imagens do conteúdo e pontos numerados clicáveis que explicam cada detalhe. É a prova de que o produto é bom.
5. **Por dentro** ("Cada capítulo, o mesmo caminho."): o método em 4 passos, com imagem.
6. **Lista completa** numerada de tudo que vem no produto.
7. **Dúvidas:** preciso saber algo antes? como recebo? lê no celular? as informações são confiáveis? e se eu não gostar?
8. **Chamada final:** frase de transformação, números do produto (capítulos, páginas, casos), preço, botão, garantia de 7 dias.
9. **Rodapé.**

## Passo a passo

1. Crie o produto em `produto/` (veja `produto/README.md`) e copie `dist/mockup.png`, `dist/capa.png` e páginas de amostra para `vendas/produtos/<slug>/img/`.
2. Copie `vendas/produtos/exemplo/pagina.json` para `vendas/produtos/<slug>/pagina.json` e reescreva **tudo**: textos, itens, amostra, FAQ, números e o **tema** (escolha uma identidade que combine com o assunto: cores, par de fontes do Google Fonts, raio dos cantos; nunca repita a de outro produto).
3. Gere e confira: `python3 vendas/gerar.py <slug> --shot` e olhe `print-desktop.jpg` e `print-celular.jpg`.
4. Cadastre o produto na plataforma de checkout e cole o link em `checkout.url`.
5. Publique a pasta `vendas/produtos/<slug>/site/` (abaixo) e grave o endereço em `url_publicada` e em `CANAL.md` → "Link da oferta principal".

## Checkout

| Plataforma | Onde pegar o link | Entrega |
|---|---|---|
| Kiwify | Produtos → seu produto → Links → link do checkout (`pay.kiwify.com.br/…`) | Área de membros ou arquivo enviado por e-mail |
| Kirvano | Produtos → Ofertas → link de pagamento | Arquivo ou área de membros |
| Cakto | Produtos → Ofertas → link do checkout | Arquivo ou área de membros |
| Hotmart | Produtos → Ferramentas → Links de divulgação → checkout (`pay.hotmart.com/…`) | Hotmart Club ou arquivo |
| Eduzz | Produtos → Links → checkout | Nutror ou arquivo |

Em todas, suba o `livro.pdf` como arquivo de entrega. A página repassa automaticamente `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `src`, `sck` e `xcod` para o checkout. Use isso na descrição de cada vídeo para saber qual vídeo vendeu:

```
https://sua-pagina.com/?utm_source=youtube&utm_medium=video&utm_campaign=<id-do-video>
```

## Publicar

Qualquer hospedagem de site estático serve (é um `index.html` + `img/`):

- **Vercel:** importe o repositório e defina *Root Directory* = `vendas/produtos/<slug>/site` (gere o site e faça commit da pasta, ou rode o gerador no build). Ou arraste a pasta em vercel.com/new.
- **Netlify:** arraste a pasta `site/` em app.netlify.com/drop.
- **GitHub Pages:** copie o conteúdo de `site/` para um repositório público e ative Pages.

Domínio próprio é opcional e configurado na hospedagem.

## Regras

- Nada de promessa que o produto não cumpre, depoimento inventado, contador falso de "últimas unidades" ou números que não estão no produto.
- Preço, parcelas e garantia têm que bater com o que está na plataforma.
