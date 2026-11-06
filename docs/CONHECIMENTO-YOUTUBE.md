# Conhecimento de YouTube que a rotina aplica

Aprendizados do projeto [youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) (MIT, ver `pipeline/yt/LICENSE-youtube-agent-skill`), adaptados ao português e ao nosso pipeline. A skill original escreve e não publica; aqui as ferramentas viraram scripts em `pipeline/yt/` e as regras viraram etapas do `ROTINA.md`. Todo número que o Claude usar precisa de fonte: **nada inventa dado**.

## 1. Gancho (os primeiros 15 segundos são o trabalho inteiro)

O gancho faz três coisas ou o vídeo vaza: **confirma o clique que o título prometeu**, **abre uma pergunta que o espectador não consegue fechar** e **prova que a recompensa existe**. Gancho que só faz a terceira é resumo.

1. **Escreva CINCO ganchos**, cada um baseado numa das 21 fórmulas de `pipeline/yt/hooks.json` (estatística, resultado alheio, o erro, virada contrária, revelação, relógio, "eu testei", pergunta, antes e depois, desmonte, alerta, lista, recibo, insider, afirmação impossível, comparação, origem, prazo, endereço direto…).
2. Rode `python3 pipeline/yt/hookscore.py ganchos.txt`, fique com os **dois melhores** e mostre as notas. Nunca entregue um gancho só. Nota baixa é motivo para olhar de novo; nota alta não é promessa (é heurística).
3. **A virada (0:15 a 0:45):** diga em uma frase o que o vídeo vai fazer e comece a fazer. Sem apresentação do canal, sem "antes de começar", sem pedido de inscrição: é a causa mais comum do penhasco aos 30 segundos.
4. **Corpo:** uma ideia por trecho. Marque o que aparece NA TELA em cada trecho (no mapa de edição), não só o que é dito. Narração com nada para olhar é podcast.
5. **Recompensa:** entregue o que o gancho prometeu e diga que está entregando.
6. **Fecho:** um pedido só (a pergunta para os comentários). Não três.

Regras das fórmulas: confirme o título na 1ª frase; uma ideia só; específico vence grande (número, nome, data); mostre o objeto prometido em até 20 segundos; nunca abra com quem você é.

## 2. Título + miniatura são UMA unidade

Escreva **dez títulos**, rode `python3 pipeline/yt/titulo.py titulos.txt` (ou `--title "..." --thumb "..."`) e mantenha os dois melhores. Regras:

- **60 caracteres** é onde a busca do computador corta; **40** é o feed do celular. O assunto tem que sobreviver aos 40.
- **A miniatura não repete o título**: mesma promessa, palavras diferentes.
- **No máximo 4 palavras na miniatura** (ideal 3). Com a 5ª, no tamanho do feed vira mancha.
- **Número, nome ou data** vence qualquer adjetivo.
- **No máximo 2 palavras em maiúsculas** no título.
- Para o vencedor, escreva o roteiro da miniatura: expressão/objeto, enquadramento, as palavras e o que o fundo precisa fazer para manter contraste no tamanho do feed (veja `pipeline/thumbnail.py`).

## 3. Shorts que já estão dentro do vídeo longo

Um Short cortado do longo não é "o melhor momento": é um momento que **sobrevive sem o vídeo em volta**. Procure trechos de 20 a 55 segundos em que (1) abre numa ideia completa, (2) tem uma virada (afirmação e depois algo que prova ou complica) e (3) termina numa frase, não num trecho solto. Mostre os 5 melhores com tempo e primeira frase e escolha 3. Para cada Short:

- **Primeira frase NOVA**, escrita para quem não viu o longo, pontuada no `hookscore.py`.
- **Texto na tela nos primeiros 2 segundos**, com palavras diferentes das faladas.
- **Ponto de loop:** a última frase prepara a primeira.
- Nota de enquadramento vertical: o que o corte 9:16 perde.

## 4. Descrição, tags e busca

- **As duas primeiras linhas** são tudo o que quase ninguém passa: aparecem acima do "mais" e viram o trecho da busca. Diga o que o vídeo entrega, nas palavras que a pessoa digitaria.
- Depois, o link da oferta (acima da dobra), depois os **capítulos** (`python3 pipeline/yt/capitulos.py producao/<id>/transcript.json --target 6`: tem que começar em 00:00, ter 3+ itens e 10 s no mínimo cada; reescreva cada título como a promessa da parte, 3 a 5 palavras), depois as fontes e o texto longo.
- **Tags pesam pouco.** Use para desambiguar (grafias, nomes de ferramentas, siglas) e pare. Quinze bastam; encher de tags não relacionadas viola os termos.
- **Teste da busca:** escreva as três buscas que o vídeo deveria ganhar e confira se o título e as duas primeiras linhas têm essas palavras. Se não têm, o problema é o título.

## 5. Retenção: o único feedback honesto

`python3 pipeline/analytics.py --retencao <VIDEO_ID> --out retencao.csv` e depois `python3 pipeline/yt/retencao.py retencao.csv --duration <segundos> --transcript producao/<id>/transcript.json`. São três problemas diferentes, com três consertos:

- **Vazamento do gancho** (perda nos primeiros 30 s; abaixo de 25% é saudável): sempre o primeiro a consertar, e é sempre a primeira frase do roteiro, nunca a edição.
- **Penhascos** (queda brusca num momento): troca de assunto sem aviso, leitura de oferta, setup longo. Com a transcrição, o relatório diz o que estava sendo dito.
- **Descida** (perda constante no meio): ritmo. O conserto é cortar, não reescrever.

Entregue **o maior vazamento e uma mudança** para ele, não uma lista de cinco. Se o gancho está saudável e a descida é plana, o vídeo está bom e o problema é a embalagem (título e miniatura).

## 6. Pesquisa: o que está funcionando de verdade

Views brutas ranqueiam o tamanho do canal, não a ideia. `research.py` já ordena por views ÷ inscritos; para confirmar candidatos, colete **pelo menos 4 vídeos por canal** e rode `python3 pipeline/yt/swipe.py coletados.json --min 2.0`: ele ranqueia pelo múltiplo sobre a **mediana do próprio canal** e nomeia a fórmula do título (é julgamento sobre as palavras do título, não prova do motivo do sucesso). Entregue os 5 melhores, a fórmula de cada, **a única coisa estrutural que têm em comum** e quais deles dá para fazer esta semana com o que temos. Só listas públicas, nunca sessão logada. **Piso de qualidade:** não modele vídeo com menos de 1.000 views, com quase nenhum like ou sem comentários; o múltiplo sozinho engana em canal pequeno (83 views pode dar 80×). Olhe views, likes ÷ views e comentários juntos.

## 7. Comentários (rotina de análise)

Triagem em quatro pilhas antes de responder: **perguntas** (respondem e viram tema do próximo vídeo; anote as repetidas), **correções** (se a pessoa tem razão, diga e agradeça; nunca discuta fato que não dá para checar), **elogios** (responda a alguns, com algo específico do comentário) e **provocação** (não responda, nunca escreva resposta atravessada). Respostas com menos de 30 palavras, a resposta na primeira frase, sem emoji. **Indique UM comentário para fixar**: a pergunta que mais gente também tem, não o mais simpático. A resposta é redigida e o dono posta (a rotina não comenta pelo canal).

## 8. Semana e auditoria

- **Semana que cabe nas horas reais:** uma âncora (o vídeo da semana), um barato (feito de algo que já existe: resposta ao comentário mais respondido) e os Shorts da âncora. Três envios, não sete. Pergunte ao dono quantas horas tem.
- **Auditoria do canal termina em UM conserto**, na ordem: (1) os 10 últimos títulos lidos como lista (prometem coisas diferentes? se todos têm a mesma forma, é problema de formato), (2) as miniaturas encolhidas ao tamanho do feed (o que sobrevive?), (3) os 15 primeiros segundos dos 3 vídeos mais recentes, pontuados, (4) a regularidade (consistência vence frequência), (5) a curva de retenção. Entregue: o maior conserto (com o que fazer esta semana), três coisas que já funcionam (específicas) e o que NÃO fazer ainda. Nunca abra auditoria com elogio que você não sente nem termine com lista de vinte itens.

## 9. Voz do dono

`CANAL.md` → "Voz de escrita" guarda: para quem se fala (uma pessoa, descrita com precisão), como o dono fala de verdade (trechos reais, não o que ele gostaria de soar), palavras que nunca usa, palavras que usa, o que nunca afirma e o formato. Todo roteiro respeita isso: roteiro na voz errada é pior que nenhum. Se estiver vazio, peça três vídeos ou áudios do dono e escreva a seção a partir deles.

## O que NÃO fazer (do projeto original)

Nada publica sozinho além do agendamento privado das nossas regras; nenhuma ferramenta inventa número; nenhum gerador de tags; nenhuma promessa de que nota alta no gancho garante resultado.
