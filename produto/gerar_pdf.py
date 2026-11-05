"""Transforma produto/<slug>/livro.md em PDF diagramado + capa e mockup para a página de vendas.

Uso:
  python3 produto/gerar_pdf.py <slug>
Gera em produto/<slug>/dist/: livro.pdf, capa.png (1600x2400) e mockup.png (capa com sombra, para o hero).

livro.md:
  primeira linha "# Título", segunda (opcional) "> subtítulo"; depois capítulos com "## ", seções "### ",
  parágrafos, listas (- ou 1.), **negrito**, *itálico*, > citação, ![legenda](img/arquivo.jpg), "---" (quebra de página).
produto/<slug>/tema.json (opcional): {"fundo_capa": "#111", "texto_capa": "#fff", "destaque": "#e63946",
  "fonte_titulo": "Playfair Display", "fonte_texto": "Source Serif 4", "autor": "Nome do canal"}
"""
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RENDER = os.path.join(ROOT, "pipeline", "render_html.js")
DEF = {"fundo_capa": "#111318", "texto_capa": "#f5f5f5", "destaque": "#e63946", "fonte_titulo": "Playfair Display",
       "fonte_texto": "Source Serif 4", "autor": ""}


def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\s)(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md(text, base):
    out, para, lst, toc, n = [], [], None, [], 0
    def flush():
        nonlocal para, lst
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>"); para = []
        if lst:
            out.append(f"<{lst[0]}>" + "".join(f"<li>{inline(i)}</li>" for i in lst[1]) + f"</{lst[0]}>"); lst = None
    for line in text.splitlines():
        s = line.strip()
        if not s:
            flush(); continue
        if s.startswith("## "):
            flush(); n += 1; toc.append(s[3:])
            out.append(f'<section class="cap" id="c{n}"><p class="capn">Capítulo {n}</p><h2>{inline(s[3:])}</h2></section>')
        elif s.startswith("### "):
            flush(); out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s == "---":
            flush(); out.append('<div class="pb"></div>')
        elif s.startswith("> "):
            flush(); out.append(f"<blockquote>{inline(s[2:])}</blockquote>")
        elif m := re.match(r"!\[(.*?)\]\((.+?)\)", s):
            flush(); src = m.group(2) if m.group(2).startswith("http") else "file://" + os.path.join(base, m.group(2))
            out.append(f'<figure><img src="{html.escape(src)}"><figcaption>{inline(m.group(1))}</figcaption></figure>')
        elif m := re.match(r"(-|\d+\.)\s+(.*)", s):
            kind = "ul" if m.group(1) == "-" else "ol"
            if para: flush()
            if not lst or lst[0] != kind:
                flush(); lst = (kind, [])
            lst[1].append(m.group(2))
        else:
            if lst: flush()
            para.append(s)
    flush()
    return "\n".join(out), toc


def fonts(t):
    fams = sorted({t["fonte_titulo"], t["fonte_texto"]})
    return '<link href="https://fonts.googleapis.com/css2?' + "&".join(
        "family=" + f.replace(" ", "+") + ":ital,wght@0,400;0,700;1,400" for f in fams) + '&display=swap" rel="stylesheet">'


def cover_html(title, sub, t, w, h):
    return f"""<!doctype html><html><head><meta charset="utf-8">{fonts(t)}<style>
*{{margin:0;box-sizing:border-box}}body{{width:{w}px;height:{h}px;background:{t["fundo_capa"]};color:{t["texto_capa"]};
font-family:'{t["fonte_titulo"]}',serif;display:flex;flex-direction:column;justify-content:space-between;padding:{w * .09}px;position:relative;overflow:hidden}}
.bar{{width:{w * .16}px;height:{w * .012}px;background:{t["destaque"]}}}
h1{{font-size:{w * .095}px;line-height:1.02;letter-spacing:-.01em}}p{{font-family:'{t["fonte_texto"]}',serif;font-size:{w * .034}px;opacity:.8;margin-top:{w * .04}px;max-width:85%}}
.a{{font-family:'{t["fonte_texto"]}',serif;font-size:{w * .028}px;letter-spacing:.2em;text-transform:uppercase;opacity:.7}}
.o{{position:absolute;right:-{w * .25}px;bottom:-{w * .25}px;width:{w * .8}px;height:{w * .8}px;border-radius:50%;border:{w * .01}px solid {t["destaque"]};opacity:.35}}
</style></head><body><div class="o"></div><div class="bar"></div><div><h1>{html.escape(title)}</h1><p>{html.escape(sub)}</p></div>
<div class="a">{html.escape(t.get("autor", ""))}</div></body></html>"""


def book_html(title, sub, body, toc, t):
    items = "".join(f'<li><a href="#c{i + 1}"><span>{i + 1:02d}</span>{html.escape(x)}</a></li>' for i, x in enumerate(toc))
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">{fonts(t)}<style>
@page{{size:A5;margin:18mm 16mm 20mm}}@page:first{{margin:0}}
*{{box-sizing:border-box}}body{{font-family:'{t["fonte_texto"]}',Georgia,serif;font-size:10.5pt;line-height:1.6;color:#1c1c1c;margin:0}}
.cover{{height:210mm;width:148mm;page-break-after:always}}.cover img{{width:100%;height:100%;object-fit:cover;display:block}}
h2,h3,.toc h2{{font-family:'{t["fonte_titulo"]}',serif;line-height:1.15}}
.toc{{page-break-after:always}}.toc ol{{list-style:none;padding:0}}.toc li{{border-bottom:1px solid #ddd;padding:7px 0}}
.toc a{{color:inherit;text-decoration:none}}.toc span{{color:{t["destaque"]};font-weight:700;margin-right:10px}}
.cap{{page-break-before:always;padding-top:28mm;margin-bottom:8mm}}.capn{{color:{t["destaque"]};text-transform:uppercase;letter-spacing:.18em;font-size:8pt;font-weight:700;margin:0}}
.cap h2{{font-size:24pt;margin:6px 0 0}}h3{{font-size:13pt;margin:18px 0 4px}}p{{margin:0 0 9px;text-align:justify;hyphens:auto}}
blockquote{{border-left:3px solid {t["destaque"]};margin:14px 0;padding:4px 0 4px 14px;font-style:italic;font-size:11.5pt}}
figure{{margin:14px 0;page-break-inside:avoid}}figure img{{width:100%;border-radius:4px}}figcaption{{font-size:8.5pt;color:#666;margin-top:4px}}
ul,ol{{padding-left:18px;margin:0 0 10px}}li{{margin-bottom:3px}}.pb{{page-break-after:always}}a{{color:{t["destaque"]}}}
</style></head><body><div class="cover"><img src="capa.png"></div>
<div class="toc"><h2>Sumário</h2><ol>{items}</ol></div>{body}</body></html>"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = os.path.join(HERE, sys.argv[1])
    t = dict(DEF)
    if os.path.exists(os.path.join(base, "tema.json")):
        t.update(json.load(open(os.path.join(base, "tema.json"), encoding="utf-8")))
    text = open(os.path.join(base, "livro.md"), encoding="utf-8").read()
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip()
    sub = lines[1][2:].strip() if len(lines) > 1 and lines[1].startswith("> ") else ""
    rest = "\n".join(lines[2 if sub else 1:])
    body, toc = md(rest, base)
    dist = os.path.join(base, "dist")
    os.makedirs(dist, exist_ok=True)
    w = lambda name, s: open(os.path.join(dist, name), "w", encoding="utf-8").write(s)
    w("_capa.html", cover_html(title, sub, t, 1600, 2400))
    subprocess.run(["node", RENDER, os.path.join(dist, "_capa.html"), os.path.join(dist, "capa.png"), "1600", "2400"], check=True)
    w("_mock.html", f'<body style="margin:0;width:1400px;height:1100px;display:grid;place-items:center;background:transparent">'
                    f'<img src="capa.png" style="height:950px;border-radius:6px 14px 14px 6px;box-shadow:-8px 0 0 rgba(0,0,0,.25) inset,'
                    f'0 40px 80px -20px rgba(0,0,0,.6);transform:perspective(1600px) rotateY(-14deg)"></body>')
    subprocess.run(["node", RENDER, os.path.join(dist, "_mock.html"), os.path.join(dist, "mockup.png"), "1400", "1100"], check=True)
    w("_livro.html", book_html(title, sub, body, toc, t))
    subprocess.run(["node", RENDER, os.path.join(dist, "_livro.html"), os.path.join(dist, "livro.pdf")], check=True)
    for f in ("_capa.html", "_mock.html", "_livro.html"):
        os.remove(os.path.join(dist, f))
    pages = subprocess.run(["bash", "-c", f"strings '{dist}/livro.pdf' | grep -c '/Type /Page$' || true"], capture_output=True, text=True).stdout.strip()
    print(f"{dist}/livro.pdf ({len(toc)} capítulos, ~{pages or '?'} páginas)\n{dist}/capa.png\n{dist}/mockup.png")


if __name__ == "__main__":
    main()
