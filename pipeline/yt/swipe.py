"""swipe.py: ranqueia vídeos coletados pelo quanto cada um superou a MEDIANA DO PRÓPRIO CANAL e nomeia a fórmula.

  python3 pipeline/yt/swipe.py coletados.json --min 2.0
  python3 pipeline/yt/swipe.py coletados.json --json

Entrada: lista de vídeos (pelo menos 4 por canal, senão a mediana não significa nada e o canal é pulado):
  [{"channel":"...","title":"...","views":412000,"url":"...","duration":613}]
Views brutas ranqueiam o tamanho do canal, não a ideia. 400 mil num canal de 2 milhões é terça-feira normal;
400 mil num canal de mediana 30 mil é o que vale estudar. A fórmula vem de hooks.json, casada com o TÍTULO:
é um julgamento sobre as palavras na tela, não uma afirmação sobre por que o vídeo deu certo.
Use junto de research.py (que ranqueia por views/inscritos) para confirmar os candidatos. Adaptado do youtube-agent-skill, MIT.
"""
import json
import os
import re
import statistics
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FORMULAS = json.load(open(os.path.join(AQUI, "hooks.json"), encoding="utf-8"))["hooks"]


def classificar(titulo):
    pts = sorted(((sum(1 for p in f["match"] if re.search(p, titulo, re.I)), f["nome"]) for f in FORMULAS), reverse=True)
    return pts[0][1] if pts and pts[0][0] else "Sem fórmula"


def main():
    a = sys.argv[1:]
    como_json = "--json" in a
    a = [x for x in a if x != "--json"]
    minimo = float(a[a.index("--min") + 1]) if "--min" in a else 1.5
    arqs = [x for x in a if not x.startswith("--") and not re.match(r"^[\d.]+$", x)]
    if not arqs or not os.path.exists(arqs[0]):
        print(__doc__)
        sys.exit(1)
    rows = json.load(open(arqs[0], encoding="utf-8"))
    if isinstance(rows, dict):
        rows = rows.get("videos", [])
    por = {}
    for r in rows:
        por.setdefault(r.get("channel", "?"), []).append(r)
    out, poucos = [], []
    for ch, vids in por.items():
        views = [float(v.get("views", 0) or 0) for v in vids]
        med = statistics.median(views) if views else 0
        if len(vids) < 4:
            poucos.append((ch, len(vids)))
            continue
        for v in vids:
            m = (float(v.get("views", 0) or 0) / med) if med else 0
            out.append({"canal": ch, "titulo": v.get("title", ""), "views": int(v.get("views", 0) or 0), "mediana": int(med),
                        "multiplo": round(m, 2), "formula": classificar(v.get("title", "")), "url": v.get("url", "")})
    out = sorted((r for r in out if r["multiplo"] >= minimo), key=lambda r: -r["multiplo"])
    if como_json:
        print(json.dumps({"destaques": out, "canais_pulados": poucos}, indent=1, ensure_ascii=False))
        return
    print(f"\n  {len(rows)} vídeos em {len(por)} canais, destaques a partir de {minimo}x\n")
    for r in out[:25]:
        print(f"    {r['multiplo']:5.2f}x  {r['views']:>9,}  vs mediana {r['mediana']:>9,}   {r['canal'][:22]:<22} {r['titulo'][:52]}")
        print(f"            {r['formula']}")
    if not out:
        print("    nada passou do limite: colete mais vídeos por canal ou baixe --min")
    if poucos:
        print(f"\n  pulei {len(poucos)} canal(is) com menos de 4 vídeos coletados: " + ", ".join(f"{c} ({n})" for c, n in poucos[:6]))
    cont = {}
    for r in out:
        cont[r["formula"]] = cont.get(r["formula"], 0) + 1
    if cont:
        print("\n  fórmulas entre os destaques")
        for f, n in sorted(cont.items(), key=lambda x: -x[1]):
            print(f"    {n:2d}x  {f}")
    print()


if __name__ == "__main__":
    main()
