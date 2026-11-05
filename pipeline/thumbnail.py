"""Miniatura 1280x720: foto de banco de imagens + frase curta de expectativa.

Estilo: foto real do assunto ocupando tudo, frase GRANDE em branco com a última palavra (ou a palavra
marcada com *asteriscos*) em amarelo, sublinhado amarelo e uma seta curva apontando para o ponto da foto
que gera a curiosidade. Ex.: "IMAGINA CODAR *AQUI?*" sobre a foto de um escritório no meio da montanha.

Uso:
  python3 pipeline/thumbnail.py search "home office mountain view" [--source unsplash|pexels]
  python3 pipeline/thumbnail.py make producao/<id>/thumb.jpg --text "IMAGINA CODAR *AQUI?*" \\
      --photo <id-da-busca> [--source unsplash|pexels] | --image foto.jpg
      [--arrow 70,55] [--side left|right] [--y top|bottom] [--accent "#FFD400"]

--arrow x,y: ponto (em % da imagem) para onde a seta aponta. Sem --arrow, não há seta.
Chaves: UNSPLASH_ACCESS_KEY (unsplash.com/developers) ou PEXELS_API_KEY (pexels.com/api). Gratuitas.
O crédito do fotógrafo vai para producao/<id>/thumb-credito.txt (cole na descrição do vídeo).
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys

from common import ROOT, env, http, download


def search(query, source, n=12):
    if source == "unsplash":
        r = http("GET", "https://api.unsplash.com/search/photos",
                 params={"query": query, "per_page": n, "orientation": "landscape", "content_filter": "high"},
                 headers={"Authorization": f"Client-ID {env('UNSPLASH_ACCESS_KEY')}", "Accept-Version": "v1"})
        return [{"id": p["id"], "desc": p.get("alt_description") or p.get("description") or "",
                 "by": p["user"]["name"], "page": p["links"]["html"], "preview": p["urls"]["small"]} for p in r["results"]]
    r = http("GET", "https://api.pexels.com/v1/search", params={"query": query, "per_page": n, "orientation": "landscape"},
             headers={"Authorization": env("PEXELS_API_KEY")})
    return [{"id": str(p["id"]), "desc": p.get("alt", ""), "by": p["photographer"], "page": p["url"],
             "preview": p["src"]["medium"]} for p in r["photos"]]


def fetch_photo(pid, source, out):
    if source == "unsplash":
        h = {"Authorization": f"Client-ID {env('UNSPLASH_ACCESS_KEY')}", "Accept-Version": "v1"}
        p = http("GET", f"https://api.unsplash.com/photos/{pid}", headers=h)
        http("GET", p["links"]["download_location"], headers=h)  # exigido pelas regras da API do Unsplash
        download(p["urls"]["raw"] + "&w=1920&q=85&fm=jpg", out)
        return f'Foto: {p["user"]["name"]} no Unsplash ({p["links"]["html"]})'
    p = http("GET", f"https://api.pexels.com/v1/photos/{pid}", headers={"Authorization": env("PEXELS_API_KEY")})
    download(p["src"]["large2x"], out)
    return f'Foto: {p["photographer"]} no Pexels ({p["url"]})'


def text_html(text):
    words = text.split()
    marked = [i for i, w in enumerate(words) if w.startswith("*") and w.endswith("*") and len(w) > 2]
    hi = set(marked) if marked else {len(words) - 1}
    out = []
    for i, w in enumerate(words):
        w = html.escape(w.strip("*"))
        out.append(f'<span class="hi">{w}</span>' if i in hi else w)
    return " ".join(out)


TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">
<style>
*{margin:0;box-sizing:border-box}
html,body{width:1280px;height:720px;overflow:hidden;background:#000}
.bg{position:absolute;inset:0;background:url('__IMG__') center/cover no-repeat;filter:saturate(1.15) contrast(1.08)}
.shade{position:absolute;inset:0;background:linear-gradient(__DIR__,rgba(0,0,0,.72) 0%,rgba(0,0,0,.35) 45%,rgba(0,0,0,0) 70%)}
.t{position:absolute;__SIDE__:56px;__Y__:52px;max-width:760px;font-family:Anton,Impact,'Arial Black',sans-serif;
   font-size:__SIZE__px;line-height:1.02;color:#fff;text-transform:uppercase;letter-spacing:.5px;
   text-shadow:0 6px 24px rgba(0,0,0,.65),0 2px 0 rgba(0,0,0,.5);text-align:__SIDE__}
.hi{color:__ACCENT__;position:relative;display:inline-block}
.hi::after{content:"";position:absolute;left:-4px;right:-4px;bottom:-10px;height:12px;border-radius:8px;background:__ACCENT__;
   box-shadow:0 4px 14px rgba(0,0,0,.5)}
svg{position:absolute;inset:0;overflow:visible}
</style></head><body>
<div class="bg"></div><div class="shade"></div>
<div class="t" id="t">__TEXT__</div>
<svg width="1280" height="720" id="s"></svg>
<script>
const target = __ARROW__;
window.__draw = () => { if (!target) return;
  const hi = document.querySelector('.hi').getBoundingClientRect();
  const tx = target[0] * 12.8, ty = target[1] * 7.2;
  const sx = tx >= hi.left + hi.width / 2 ? hi.right + 18 : hi.left - 18, sy = hi.top + hi.height * .55;
  const dx = tx - sx, dy = ty - sy, len = Math.hypot(dx, dy);
  const ex = tx - dx / len * 34, ey = ty - dy / len * 34;          // para antes do ponto
  const bend = (dx >= 0 ? 1 : -1) * Math.min(160, len * .35);
  const cx = (sx + ex) / 2 + bend * (dy / len) * -1 + bend * .2, cy = (sy + ey) / 2 + Math.abs(bend) * .5;
  const ang = Math.atan2(ey - cy, ex - cx), a = 30, sp = .5;
  const p1 = [ex - a * Math.cos(ang - sp), ey - a * Math.sin(ang - sp)], p2 = [ex - a * Math.cos(ang + sp), ey - a * Math.sin(ang + sp)];
  const st = 'fill="none" stroke="__ACCENT__" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"';
  document.getElementById('s').innerHTML =
    `<g filter="drop-shadow(0 4px 10px rgba(0,0,0,.6))"><path d="M${sx},${sy} Q${cx},${cy} ${ex},${ey}" ${st}/>` +
    `<path d="M${p1} L${ex},${ey} L${p2}" ${st}/></g>`;
};
</script></body></html>"""


def make(out, text, img, arrow=None, side="left", y="top", accent="#FFD400"):
    n = len(re.sub(r"\*", "", text))
    size = 132 if n <= 14 else 116 if n <= 22 else 98 if n <= 32 else 84
    work = os.path.splitext(out)[0] + "-thumb.html"
    page = (TEMPLATE.replace("__IMG__", os.path.abspath(img)).replace("__TEXT__", text_html(text))
            .replace("__SIDE__", side).replace("__Y__", y).replace("__SIZE__", str(size)).replace("__ACCENT__", accent)
            .replace("__DIR__", "to right" if side == "left" else "to left")
            .replace("__ARROW__", json.dumps(arrow) if arrow else "null"))
    open(work, "w", encoding="utf-8").write(page)
    subprocess.run(["node", os.path.join(ROOT, "pipeline", "render_html.js"), work, out, "1280", "720"], check=True)
    os.remove(work)
    if os.path.getsize(out) > 2_000_000:  # limite do YouTube
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-q:v", "4", out + ".jpg"], check=True)
        os.replace(out + ".jpg", out)
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--source", default="unsplash", choices=["unsplash", "pexels"])
    m = sub.add_parser("make"); m.add_argument("out"); m.add_argument("--text", required=True)
    m.add_argument("--photo"); m.add_argument("--image"); m.add_argument("--source", default="unsplash", choices=["unsplash", "pexels"])
    m.add_argument("--arrow"); m.add_argument("--side", default="left", choices=["left", "right"])
    m.add_argument("--y", default="top", choices=["top", "bottom"]); m.add_argument("--accent", default="#FFD400")
    a = ap.parse_args()
    if a.cmd == "search":
        for p in search(a.query, a.source):
            print(f'{p["id"]:<14} {p["desc"][:70]:<70} | {p["by"]} | {p["preview"]}')
        return
    img = a.image
    if not img:
        if not a.photo:
            sys.exit("use --photo <id> (de 'search') ou --image <arquivo>")
        img = os.path.splitext(a.out)[0] + "-foto.jpg"
        credit = fetch_photo(a.photo, a.source, img)
        open(os.path.join(os.path.dirname(os.path.abspath(a.out)), "thumb-credito.txt"), "w").write(credit + "\n")
        print(credit)
    arrow = [float(v) for v in a.arrow.split(",")] if a.arrow else None
    print(make(a.out, a.text, img, arrow, a.side, a.y, a.accent))


if __name__ == "__main__":
    main()
