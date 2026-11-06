"""capitulos.py: capítulos do YouTube a partir de uma transcrição, validados pelas regras do próprio YouTube.

  python3 pipeline/yt/capitulos.py producao/<id>/transcript.json --target 6
  python3 pipeline/yt/capitulos.py legenda.srt --target 8 --json

As regras que o YouTube exige (bloco que quebra qualquer uma delas não vira capítulo, fica só como texto):
a lista começa em 00:00, tem pelo menos três itens e cada capítulo tem pelo menos 10 segundos.
Os limites vêm das pausas e da troca de vocabulário entre trechos. O resultado é rascunho: REESCREVA
cada título como a promessa daquela parte (3 a 5 palavras). Se uma parte não cabe em 5 palavras, são
duas partes ou é enchimento. Adaptado (português) do youtube-agent-skill, MIT.
"""
import json
import os
import re
import sys

from transcricao import carregar

PARAR = set("de do da dos das em no na nos nas um uma uns umas o a os as e ou que com por para pra como mas se então "
            "também mais muito muita isso esse essa esses essas aqui ali já não sim você vocês eu nós ele ela eles elas "
            "seu sua seus suas meu minha foi era são ser tem têm ter está estão vai vamos pode podem fazer faz feito "
            "quando onde porque pois depois antes ainda só até sobre entre cada tudo todo toda todos todas coisa coisas".split())


def chaves(texto):
    return {w for w in re.findall(r"[a-zà-ÿ]{4,}", texto.lower()) if w not in PARAR}


def mmss(t):
    t = int(t)
    h, m, s = t // 3600, (t % 3600) // 60, t % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main():
    a = sys.argv[1:]
    como_json = "--json" in a
    a = [x for x in a if x != "--json"]
    alvo = int(a[a.index("--target") + 1]) if "--target" in a else 7
    a = [x for x in a if not x.startswith("--") and not x.isdigit()]
    if not a or not os.path.exists(a[0]):
        print(__doc__)
        sys.exit(1)
    cues = carregar(a[0])
    if len(cues) < 6:
        print("poucas falas para dividir em capítulos")
        sys.exit(1)
    dur = cues[-1][1]
    cand = []
    for i in range(1, len(cues)):
        pausa = cues[i][0] - cues[i - 1][1]
        antes = " ".join(c[2] for c in cues[max(0, i - 12):i])
        depois = " ".join(c[2] for c in cues[i:i + 12])
        kb, ka = chaves(antes), chaves(depois)
        troca = 1 - (len(kb & ka) / len(kb | ka)) if (kb | ka) else 0
        cand.append((pausa * 1.6 + troca * 3.2, cues[i][0], i))
    cand.sort(reverse=True)
    escolhidos, MIN = [0.0], 10.0
    for _, t, i in cand:
        if len(escolhidos) >= alvo:
            break
        if all(abs(t - p) >= MIN for p in escolhidos) and dur - t >= MIN:
            escolhidos.append(t)
    escolhidos.sort()
    caps = []
    for n, t in enumerate(escolhidos):
        fim = escolhidos[n + 1] if n + 1 < len(escolhidos) else dur
        texto = " ".join(c[2] for c in cues if c[0] >= t and c[1] <= fim)
        kw = sorted(chaves(texto), key=lambda w: -texto.lower().count(w))
        caps.append({"inicio": round(t, 2), "rotulo": mmss(t), "titulo_rascunho": " ".join(w.capitalize() for w in kw[:3]) or "Parte",
                     "segundos": round(fim - t, 2)})
    ok = len(caps) >= 3 and caps[0]["inicio"] == 0 and all(c["segundos"] >= MIN for c in caps)
    if como_json:
        print(json.dumps({"valido": ok, "capitulos": caps}, indent=1, ensure_ascii=False))
        return
    print()
    for c in caps:
        print(f"  {c['rotulo']} {c['titulo_rascunho']}")
    print(f"\n  {len(caps)} capítulos" + ("" if ok else "  -- INVÁLIDO: o YouTube exige 3+, primeiro em 00:00 e 10s no mínimo cada"))
    print("  Reescreva cada linha antes de colar. São palavras do assunto, não as suas.\n")


if __name__ == "__main__":
    main()
