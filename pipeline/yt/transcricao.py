"""Lê transcrição em .srt, .vtt ou .json e devolve cues (início, fim, texto).

Formatos aceitos no .json: lista de palavras {text,start,end} (o transcript.json do pipeline),
segmentos do Whisper {"segments":[{start,end,text}]} ou lista de segmentos.
"""
import json
import re


def _ts(s):
    s = s.strip().replace(",", ".")
    p = s.split(":")
    return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2]) if len(p) == 3 else int(p[0]) * 60 + float(p[1])


def carregar(path, palavras_por_cue=8):
    raw = open(path, encoding="utf-8", errors="replace").read()
    if path.endswith(".json"):
        d = json.loads(raw)
        itens = d.get("segments", d.get("words", d)) if isinstance(d, dict) else d
        cues, buf = [], []
        for w in itens:
            t = (w.get("text") or w.get("word") or "").strip()
            if not t:
                continue
            if "segments" in (d if isinstance(d, dict) else {}) or len(t.split()) > 2:
                cues.append((float(w["start"]), float(w["end"]), t))
                continue
            buf.append((float(w["start"]), float(w["end"]), t))
            if len(buf) >= palavras_por_cue or re.search(r"[.?!]$", t):
                cues.append((buf[0][0], buf[-1][1], " ".join(b[2] for b in buf)))
                buf = []
        if buf:
            cues.append((buf[0][0], buf[-1][1], " ".join(b[2] for b in buf)))
        return cues
    cues, cur = [], None
    for line in raw.splitlines():
        m = re.match(r"\s*(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", line)
        if m:
            cur = [_ts(m.group(1)), _ts(m.group(2)), []]
            cues.append(cur)
        elif cur is not None and line.strip() and not line.strip().isdigit():
            cur[2].append(line.strip())
    return [(a, b, " ".join(t)) for a, b, t in cues if t]
