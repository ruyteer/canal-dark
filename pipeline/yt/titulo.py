"""titulo.py: confere título e miniatura como UM par antes de publicar.

  python3 pipeline/yt/titulo.py --title "..." --thumb "IMAGINA CODAR AQUI?"
  python3 pipeline/yt/titulo.py titulos.txt         # um por linha, em ranking
  python3 pipeline/yt/titulo.py --title "..." --json

O par é a unidade, não o título. Título que repete o texto da miniatura desperdiça metade da
superfície de clique, e esse é o erro mais comum que isto confere.
Limites: o YouTube corta perto de 60 caracteres na busca do computador e perto de 40 no feed do
celular. Os dois são avisados porque falham diferente: o corte do computador perde o fim; o do celular
pode perder o assunto. Adaptado (português) do youtube-agent-skill, MIT.
"""
import json
import os
import re
import sys

DESKTOP, CELULAR, MAXIMO = 60, 40, 100
VAGAS = {"incrível", "absurdo", "louco", "enorme", "gigante", "definitivo", "poderoso", "melhor", "segredo",
         "revolucionário", "épico", "perfeito", "completo", "tudo", "inacreditável", "insano"}
LIGACAO = {"o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "para", "pra",
           "por", "com", "e", "ou", "que", "como", "por que", "seu", "sua", "você", "eu", "meu", "minha", "isso", "esse", "essa"}


def palavras(t):
    return re.findall(r"[\wÀ-ÿ']+", t.lower())


def conferir(titulo, thumb=None):
    t = titulo.strip()
    n = len(t)
    problemas, bom = [], []
    if n > MAXIMO:
        problemas.append(("tamanho", f"{n} caracteres: o limite do YouTube é {MAXIMO}"))
    elif n > DESKTOP:
        problemas.append(("tamanho", f"{n} caracteres: a busca no computador corta perto de {DESKTOP}"))
    else:
        bom.append(f"{n} caracteres, dentro do corte de {DESKTOP} do computador")
    if n > CELULAR:
        cabeca = t[:CELULAR].rsplit(" ", 1)[0]
        problemas.append(("celular", f'o feed do celular mostra algo como "{cabeca}...": confira se o assunto sobrevive'))
    gritos = [w for w in t.split() if len(w) > 2 and w.isupper()]
    if len(gritos) > 2:
        problemas.append(("grito", f"{len(gritos)} palavras em maiúsculas: duas é o teto antes de parecer spam"))
    elif gritos:
        bom.append(f"{len(gritos)} palavra em maiúsculas para ênfase")
    v = [w for w in palavras(t) if w in VAGAS]
    if v:
        problemas.append(("vago", f"{', '.join(sorted(set(v)))}: troque por número, nome ou data"))
    nums = re.findall(r"\d[\d.,]*%?", t)
    if nums:
        bom.append(f"traz um dado concreto ({', '.join(nums[:3])})")
    else:
        problemas.append(("sem-numero", "sem número, data ou nome: é o conserto mais confiável"))
    if t.endswith("?"):
        bom.append("pergunta aberta no título")
    frente = [w for w in palavras(t)[:3] if w not in LIGACAO]
    if not frente:
        problemas.append(("frente", "as três primeiras palavras são só ligação: ponha o assunto na frente"))
    if thumb:
        tw, hw = set(palavras(t)) - LIGACAO, set(palavras(thumb)) - LIGACAO
        iguais = tw & hw
        if iguais:
            problemas.append(("repetido", f"a miniatura repete o título em {', '.join(sorted(iguais))}: ela deve dizer o que o título não diz"))
        else:
            bom.append("miniatura e título trazem palavras diferentes")
        nt = len(palavras(thumb))
        if nt > 4:
            problemas.append(("miniatura-longa", f"{nt} palavras na miniatura: o teto no tamanho do feed é 4 (o ideal é 3)"))
        elif nt <= 3:
            bom.append(f"miniatura com {nt} palavras, legível no feed")
    score = max(0, min(100, 100 - 14 * len(problemas) + 4 * len(bom)))
    return {"titulo": t, "caracteres": n, "nota": score, "problemas": problemas, "bom": bom}


def mostrar(r):
    print(f'\n  "{r["titulo"]}"')
    print(f"  {r['caracteres']} caracteres   nota {r['nota']}/100")
    for k, m in r["problemas"]:
        print(f"    x  {k:<16} {m}")
    for m in r["bom"]:
        print(f"    ok               {m}")


def main():
    a = sys.argv[1:]
    como_json = "--json" in a
    a = [x for x in a if x != "--json"]
    thumb = a[a.index("--thumb") + 1] if "--thumb" in a else None
    if "--title" in a:
        linhas = [conferir(a[a.index("--title") + 1], thumb)]
    elif a and os.path.exists(a[0]):
        linhas = [conferir(l, thumb) for l in open(a[0], encoding="utf-8").read().splitlines() if l.strip()]
    else:
        print(__doc__)
        sys.exit(1)
    linhas.sort(key=lambda r: -r["nota"])
    if como_json:
        print(json.dumps(linhas, indent=1, ensure_ascii=False))
        return
    for r in linhas:
        mostrar(r)
    print()


if __name__ == "__main__":
    main()
