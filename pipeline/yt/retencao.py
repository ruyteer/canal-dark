"""retencao.py: lê o CSV de retenção da audiência e acha onde as pessoas saem.

  python3 pipeline/yt/retencao.py retencao.csv --duration 600
  python3 pipeline/yt/retencao.py retencao.csv --transcript producao/<id>/transcript.json
  python3 pipeline/analytics.py --retencao <VIDEO_ID> --out retencao.csv     # baixa o CSV pela API

O CSV tem duas colunas: posição (porcentagem ou segundos) e % ainda assistindo.
Reporta três coisas, porque são três problemas com três consertos diferentes:
  VAZAMENTO DO GANCHO  o que se perdeu nos primeiros 30 segundos
  PENHASCOS            quedas bruscas: um momento específico em que as pessoas saíram
  DESCIDA              a perda constante no meio do vídeo
Com --transcript, mostra o que estava sendo dito em cada penhasco: é o que torna o relatório
acionável sem rever o vídeo inteiro. Adaptado (português) do youtube-agent-skill, MIT.
"""
import csv
import json
import os
import sys

from transcricao import carregar


def ler_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        for r in csv.reader(fh):
            nums = []
            for c in r:
                c = c.strip().replace("%", "").replace(",", ".")
                try:
                    nums.append(float(c))
                except ValueError:
                    nums.append(None)
            vals = [n for n in nums if n is not None]
            if len(vals) >= 2:
                rows.append((vals[0], vals[1]))
    return rows


def main():
    a = sys.argv[1:]
    como_json = "--json" in a
    a = [x for x in a if x != "--json"]
    tr = a[a.index("--transcript") + 1] if "--transcript" in a else None
    dur = float(a[a.index("--duration") + 1]) if "--duration" in a else None
    arqs = [x for x in a if not x.startswith("--") and x != tr and not (dur and x == str(a[a.index("--duration") + 1]))]
    if not arqs or not os.path.exists(arqs[0]):
        print(__doc__)
        sys.exit(1)
    rows = ler_csv(arqs[0])
    if len(rows) < 8:
        print("não consegui ler 8 pontos de dados desse CSV")
        sys.exit(1)
    xs = [r[0] for r in rows]
    ys = [r[1] for r in rows]
    pct = max(xs) <= 100.5
    seg = lambda x: (x / 100.0 * dur) if (pct and dur) else x
    inicio = ys[0] or 100.0
    corte = 30.0 if not pct else (30.0 / dur * 100 if dur else 10.0)
    fim_gancho = min((y for x, y in rows if x <= corte), default=inicio)
    vazamento = inicio - fim_gancho
    quedas = []
    for i in range(1, len(rows)):
        d = ys[i - 1] - ys[i]
        span = xs[i] - xs[i - 1] or 1
        quedas.append((d / span, xs[i - 1], xs[i], d))
    quedas.sort(reverse=True)
    penhascos = [{"de": round(a1, 2), "ate": round(b1, 2), "perdeu": round(d, 2),
                  "segundo": round(seg(a1), 1) if (not pct or dur) else None}
                 for _, a1, b1, d in quedas[:5] if d > 0.8]
    meio = [q[0] for q in quedas if q[1] > corte]
    descida = sum(meio) / len(meio) if meio else 0
    dito = {}
    if tr and os.path.exists(tr):
        cues = carregar(tr)
        for c in penhascos:
            if c["segundo"] is None:
                continue
            t = c["segundo"]
            perto = [q[2] for q in cues if q[0] <= t + 4 and q[1] >= t - 4]
            dito[str(c["de"])] = " ".join(perto)[:140]
    if como_json:
        print(json.dumps({"pontos": len(rows), "inicio": inicio, "vazamento_gancho": round(vazamento, 2), "fim": ys[-1],
                          "penhascos": penhascos, "descida_por_unidade": round(descida, 3), "dito": dito}, indent=1, ensure_ascii=False))
        return
    print(f"\n  {arqs[0]}   {len(rows)} pontos   {ys[0]:.1f}% -> {ys[-1]:.1f}%\n")
    veredito = "saudável" if vazamento < 25 else "vazando" if vazamento < 40 else "grave"
    print(f"  VAZAMENTO DO GANCHO   {vazamento:.1f}% perdidos na abertura   [{veredito}]")
    print("                        abaixo de 25 é saudável. Conserte a primeira frase antes de qualquer outra coisa.\n")
    print("  PENHASCOS             os momentos em que as pessoas realmente saíram")
    for c in penhascos:
        onde = f"{c['segundo']:.0f}s" if c["segundo"] is not None else f"{c['de']}"
        print(f"    -{c['perdeu']:5.1f}%  em {onde:>8}" + (f'   "{dito.get(str(c["de"]), "")}"' if dito else ""))
    if not penhascos:
        print("    nada mais íngreme que 0,8%: a perda é toda descida, não momento")
    print(f"\n  DESCIDA               {descida:.3f}% por unidade no meio")
    print("                        descida plana é ritmo, não conteúdo. Corte o meio, não reescreva.\n")


if __name__ == "__main__":
    main()
