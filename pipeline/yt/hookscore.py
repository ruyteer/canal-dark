"""hookscore.py: pontua um gancho (os primeiros 15 segundos) antes de você gastar uma narração nele.

Cinco propriedades de 0 a 100. O veredito é 60% da média e 40% da pior, de propósito: gancho com
quatro pontos fortes e um morto vaza no morto, e a média esconde isso.

  python3 pipeline/yt/hookscore.py ganchos.txt          # um gancho por linha, em ranking
  python3 pipeline/yt/hookscore.py --hook "uma linha"   # um gancho só
  python3 pipeline/yt/hookscore.py --json ganchos.txt

O QUE ISSO DIZ E NÃO DIZ. É uma heurística, não um previsor. O projeto de origem mediu 74 ganchos
reais: ela separa ganchos deliberadamente ruins de ganchos reais, e quase não separa os acertos de
um criador dos erros dele mesmo. Nota baixa é motivo para olhar de novo; nota alta não é promessa.
Adaptado (português) do youtube-agent-skill, MIT.
"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FORMULAS = json.load(open(os.path.join(AQUI, "hooks.json"), encoding="utf-8"))["hooks"]

ENCHIMENTO = {"então", "tipo", "galera", "gente", "pessoal", "fala", "bem-vindo", "bem-vindos", "hoje",
              "vídeo", "video", "inscreva-se", "inscrevam-se", "canal", "basicamente", "realmente", "meio",
              "assim", "né", "olá", "oi", "bom"}
VAGAS = {"incrível", "absurdo", "louco", "doido", "enorme", "gigante", "segredo", "poderoso", "melhor",
         "definitivo", "revolucionário", "inacreditável", "espetacular", "surreal", "insano", "perfeito"}
CONCRETO = re.compile(r"(\d[\d.,]*\s?(%|mil|milhões|milhão|x|segundos?|minutos?|horas?|dias?|semanas?|meses|anos?|reais)?|R\$\s?\d)", re.I)
VOCE = re.compile(r"\b(você|voce|vc|seu|sua|seus|suas|te|teu|tua|sua família)\b", re.I)
RISCO = re.compile(r"\b(perder|perdeu|perde|prejuízo|golpe|golpista|risco|nunca|antes de|pare|erro|errado|custa|custou|cair|caiu|roubar|roubaram|vazar|vazou|multa|processo|morrer|falir|quebrar)\b", re.I)
CURIOSIDADE = re.compile(r"\b(por que|porque|como|qual|quais|quando|até|mas|ninguém|quase|exceto|motivo|segredo|será|só que|na verdade)\b", re.I)
FECHA_SOZINHO = re.compile(r"\b(porque (ele|ela|isso)|ou seja|o que significa)\b", re.I)


def palavras(t):
    return re.findall(r"[\wÀ-ÿ'%$.,-]+", t.lower())


def especificidade(t):
    w = palavras(t)
    if not w:
        return 0
    nums = len(CONCRETO.findall(t))
    vagas = sum(1 for x in w if x.strip(".,") in VAGAS)
    ench = sum(1 for x in w if x.strip(".,") in ENCHIMENTO)
    s = 34 + nums * 22 - vagas * 16 - ench * 5
    s += min(18, 6 * sum(1 for x in t.split()[1:] if x[:1].isupper()))  # nomes próprios no meio da frase
    return max(0, min(100, s))


def endereco(t):
    n = len(VOCE.findall(t))
    primeiras = 30 if VOCE.search(" ".join(t.split()[:6])) else 0
    return max(0, min(100, 26 + n * 20 + primeiras))


def aposta(t):
    n = len(RISCO.findall(t))
    return max(0, min(100, 22 + n * 26 + (14 if CONCRETO.search(t) else 0)))


def curiosidade(t):
    n = len(CURIOSIDADE.findall(t))
    q = 18 if t.strip().endswith("?") else 0
    fecha = -18 if FECHA_SOZINHO.search(t) else 0  # gancho que se resolve sozinho não deixa lacuna
    return max(0, min(100, 24 + n * 17 + q + fecha))


def brevidade(t):
    n = len(palavras(t))
    if n == 0:
        return 0
    if 9 <= n <= 26:  # faixa que cabe em ~10 segundos de fala
        return 100
    if n < 9:
        return max(30, 100 - (9 - n) * 11)
    return max(10, 100 - (n - 26) * 7)


PROPS = [("ESPECIFICIDADE", especificidade), ("ENDEREÇO", endereco), ("APOSTA", aposta),
         ("CURIOSIDADE", curiosidade), ("BREVIDADE", brevidade)]
CONSERTO = {
    "ESPECIFICIDADE": "troque um adjetivo por um número, um nome ou uma data",
    "ENDEREÇO": "diga 'você' nas primeiras seis palavras",
    "APOSTA": "diga o que custa continuar fazendo do jeito atual",
    "CURIOSIDADE": "corte a metade da frase que responde a si mesma",
    "BREVIDADE": "de 9 a 26 palavras. Leia em voz alta e pare onde faltar o fôlego",
}


def classificar(t):
    melhor, hits = None, 0
    for f in FORMULAS:
        n = sum(1 for p in f["match"] if re.search(p, t, re.I))
        if n > hits:
            melhor, hits = f, n
    return (melhor["nome"] if melhor else "Sem fórmula"), hits


def pontuar(t):
    partes = {n: fn(t) for n, fn in PROPS}
    vals = list(partes.values())
    veredito = round(0.6 * (sum(vals) / len(vals)) + 0.4 * min(vals))
    nome, hits = classificar(t)
    return partes, veredito, nome, hits


def faixa(v):
    return "FORTE" if v >= 72 else "RAZOÁVEL" if v >= 55 else "FRACO"


def relatorio(t, partes, veredito, nome, hits):
    print(f"\n  {t.strip()}")
    print(f"  {'-' * min(72, max(20, len(t.strip())))}")
    for k, v in partes.items():
        print(f"    {k:<15} {v:3d}  {'#' * (v // 5)}")
    print(f"    {'VEREDITO':<15} {veredito:3d}  {faixa(veredito)}")
    print(f"    fórmula         {nome}" + (f"  ({hits} padrão(ões))" if hits else "  (nenhuma casou: costuma ser resumo, não gancho)"))
    pior = min(partes, key=partes.get)
    print(f"    mais fraco      {pior}: {CONSERTO[pior]}")


def main():
    a = sys.argv[1:]
    como_json = "--json" in a
    a = [x for x in a if x != "--json"]
    if "--hook" in a:
        linhas = [a[a.index("--hook") + 1]]
    elif a and os.path.exists(a[0]):
        linhas = [l for l in open(a[0], encoding="utf-8").read().splitlines() if l.strip()]
    else:
        print(__doc__)
        sys.exit(1 if not a else 0)
    out = []
    for t in linhas:
        partes, ver, nome, hits = pontuar(t)
        out.append({"gancho": t.strip(), "propriedades": partes, "veredito": ver, "faixa": faixa(ver), "formula": nome, "padroes": hits})
    out.sort(key=lambda r: -r["veredito"])
    if como_json:
        print(json.dumps(out, indent=1, ensure_ascii=False))
        return
    for r in out:
        relatorio(r["gancho"], r["propriedades"], r["veredito"], r["formula"], r["padroes"])
    if len(out) > 1:
        print(f"\n  vencedor: {out[0]['gancho']}  ({out[0]['veredito']}, {out[0]['faixa']})\n")


if __name__ == "__main__":
    main()
