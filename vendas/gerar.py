"""Gera a página de vendas de um produto a partir de vendas/produtos/<slug>/pagina.json.

Uso:
  python3 vendas/gerar.py <slug>            # → vendas/produtos/<slug>/site/index.html (+ imagens copiadas)
  python3 vendas/gerar.py <slug> --shot     # também tira prints (desktop e celular) para conferir

Estrutura (a mesma para todo produto; o que muda é a identidade visual em "tema"):
  topo com marca e botão → hero (gancho, promessa com número, botão, preço, parcelas, mockup)
  → faixa corrida com os itens → amostra interativa (abas + pontos clicáveis na imagem)
  → "por dentro" (o mesmo caminho em N passos) → lista completa numerada → dúvidas
  → chamada final (números, preço, botão, garantia) → rodapé.

O link de checkout recebe automaticamente os parâmetros da URL da página (utm_*, src, sck, xcod…),
para a plataforma (Kiwify, Kirvano, Cakto, Hotmart, Eduzz…) atribuir a venda ao vídeo de origem.
"""
import argparse
import html
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
E = lambda s: html.escape(str(s or ""))


def font_link(t):
    fams = {t["fonte_titulo"], t["fonte_texto"]}
    q = "&".join("family=" + f.replace(" ", "+") + ":ital,wght@0,400;0,600;0,700;0,800;1,400" for f in sorted(fams))
    return f'<link href="https://fonts.googleapis.com/css2?{q}&display=swap" rel="stylesheet">'


def img(src, alt, cls=""):
    return f'<img src="{E(src)}" alt="{E(alt)}" class="{cls}" loading="lazy">' if src else ""


def build(p):
    t = p["tema"]
    c = p["checkout"]
    preco = p["preco"]
    cta = E(p.get("cta", "Quero agora"))
    btn = lambda extra="": f'<a class="btn {extra}" href="{E(c["url"])}" data-checkout>{cta}</a>'
    preco_html = (f'<div class="price"><span class="de">{E(preco.get("de"))}</span> <b>{E(preco["por"])}</b>'
                  f'<small>{E(preco.get("parcelas"))}</small></div>') if preco.get("de") else \
                 f'<div class="price"><b>{E(preco["por"])}</b><small>{E(preco.get("parcelas"))}</small></div>'
    itens = p.get("itens", [])
    marquee = " · ".join(E(i["nome"]) for i in itens) or E(p["nome"])

    # amostra interativa
    am = p.get("amostra", {})
    tabs, panes = [], []
    for k, a in enumerate(am.get("abas", [])):
        pts = "".join(f'<button class="dot" style="left:{x["x"]}%;top:{x["y"]}%" data-i="{j}" aria-label="{E(x["titulo"])}">{j + 1}</button>'
                      for j, x in enumerate(a.get("pontos", [])))
        notes = "".join(f'<li data-i="{j}"><b>{j + 1}. {E(x["titulo"])}</b><span>{E(x["texto"])}</span></li>'
                        for j, x in enumerate(a.get("pontos", [])))
        tabs.append(f'<button role="tab" data-t="{k}">{E(a["nome"])}</button>')
        panes.append(f'<div class="pane" data-t="{k}"><div class="stage">{img(a.get("imagem"), a["nome"])}{pts}</div>'
                     f'<ol class="notes">{notes}</ol></div>')
    amostra = "" if not tabs else f"""
<section id="amostra" class="sec"><div class="wrap">
  <p class="kick">{E(am.get("rotulo", "Experimente"))}</p><h2>{E(am.get("titulo", "Chegue mais perto."))}</h2>
  <p class="lead">{E(am.get("texto"))}</p>
  <div class="tabs" role="tablist">{''.join(tabs)}</div>{''.join(panes)}
</div></section>"""

    pd = p.get("por_dentro", {})
    passos = "".join(f'<div class="step"><span class="n">{k + 1:02d}</span>{img(s.get("imagem"), s["titulo"])}<h3>{E(s["titulo"])}</h3><p>{E(s["texto"])}</p></div>'
                     for k, s in enumerate(pd.get("passos", [])))
    lista = "".join(f'<li><span class="n">{k + 1:02d}</span><div><b>{E(i["nome"])}</b><small>{E(i.get("detalhe"))}</small></div></li>'
                    for k, i in enumerate(itens))
    faq = "".join(f'<details><summary>{E(f["p"])}</summary><p>{E(f["r"])}</p></details>' for f in p.get("faq", []))
    nums = "".join(f'<div><b>{E(n["valor"])}</b><span>{E(n["rotulo"])}</span></div>' for n in p.get("numeros", []))
    h = p["hero"]
    fim = p.get("final", {})
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(p["nome"])}</title><meta name="description" content="{E(h.get("subtitulo"))}">
<meta property="og:title" content="{E(p["nome"])}"><meta property="og:description" content="{E(h.get("subtitulo"))}">
{f'<meta property="og:image" content="{E(h["mockup"])}">' if h.get("mockup") else ""}
<link rel="preconnect" href="https://fonts.googleapis.com">{font_link(t)}
<style>
:root{{--bg:{t["fundo"]};--fg:{t["texto"]};--muted:{t.get("texto_suave", t["texto"] + "aa")};--accent:{t["destaque"]};--accent-fg:{t.get("texto_botao", "#fff")};
--card:{t.get("cartao", "rgba(127,127,127,.08)")};--line:{t.get("linha", "rgba(127,127,127,.22)")};--r:{t.get("raio", "14px")};
--ft:'{t["fonte_titulo"]}',Georgia,serif;--fb:'{t["fonte_texto"]}',system-ui,sans-serif}}
*{{box-sizing:border-box;margin:0;padding:0}}html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--fg);font:17px/1.6 var(--fb);-webkit-font-smoothing:antialiased}}
img{{max-width:100%;display:block}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 20px}}
h1,h2,h3{{font-family:var(--ft);line-height:1.08;letter-spacing:-.01em;font-weight:{t.get("peso_titulo", 700)}}}
h1{{font-size:clamp(38px,6vw,72px)}}h2{{font-size:clamp(30px,4.4vw,50px);margin-bottom:14px}}h3{{font-size:22px;margin:12px 0 6px}}
.kick{{text-transform:uppercase;letter-spacing:.16em;font-size:12px;font-weight:700;color:var(--accent);margin-bottom:10px}}
.lead{{color:var(--muted);max-width:640px;margin-bottom:28px}}
.btn{{display:inline-block;background:var(--accent);color:var(--accent-fg);text-decoration:none;font-weight:700;padding:16px 30px;border-radius:var(--r);
  box-shadow:0 10px 30px -10px var(--accent);transition:transform .15s}}.btn:hover{{transform:translateY(-2px)}}.btn.sm{{padding:9px 16px;font-size:14px;box-shadow:none}}
header.top{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
header.top .wrap{{display:flex;justify-content:space-between;align-items:center;height:62px}}.brand{{font-family:var(--ft);font-size:20px;font-weight:700}}
.hero{{padding:64px 0 56px}}.hero .wrap{{display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:center}}
.hero p.sub{{font-size:20px;color:var(--muted);margin:18px 0 26px;max-width:560px}}
.fmt{{font-size:13px;color:var(--muted);margin-top:12px}}
.price{{margin-top:18px;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}}.price b{{font-size:30px;font-family:var(--ft)}}.price .de{{text-decoration:line-through;color:var(--muted)}}
.price small{{color:var(--muted);font-size:14px;width:100%}}
.mock img{{border-radius:var(--r);box-shadow:0 30px 60px -20px rgba(0,0,0,.55);transform:rotate(-2deg)}}
.marq{{border-block:1px solid var(--line);overflow:hidden;white-space:nowrap;padding:14px 0;font-family:var(--ft);font-size:20px}}
.marq div{{display:inline-block;animation:m 60s linear infinite;padding-left:100%}}@keyframes m{{to{{transform:translateX(-100%)}}}}
@media (prefers-reduced-motion:reduce){{.marq div{{animation:none;padding-left:20px}}}}
.sec{{padding:84px 0}}.sec+.sec{{border-top:1px solid var(--line)}}
.tabs{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}}
.tabs button{{border:1px solid var(--line);background:transparent;color:var(--fg);padding:8px 14px;border-radius:999px;font:600 14px var(--fb);cursor:pointer}}
.tabs button[aria-selected=true]{{background:var(--fg);color:var(--bg)}}
.pane{{display:none;grid-template-columns:1.3fr 1fr;gap:28px;align-items:start}}.pane.on{{display:grid}}
.stage{{position:relative;max-width:480px;width:100%;border-radius:var(--r);overflow:hidden;background:var(--card)}}
.dot{{position:absolute;transform:translate(-50%,-50%);width:34px;height:34px;border-radius:50%;border:2px solid #fff;background:var(--accent);color:var(--accent-fg);font-weight:800;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.4)}}
.dot.on{{outline:4px solid color-mix(in srgb,var(--accent) 45%,transparent)}}
.notes{{list-style:none;display:grid;gap:10px}}.notes li{{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;cursor:pointer}}
.notes li span{{display:block;color:var(--muted);font-size:15px;margin-top:4px}}.notes li.on{{border-color:var(--accent)}}
.steps{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}}.step{{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:18px}}
.step .n,.list .n{{font-family:var(--ft);color:var(--accent);font-weight:700}}.step img{{border-radius:calc(var(--r) - 4px);margin-top:10px;aspect-ratio:4/3;object-fit:cover}}
.step p{{color:var(--muted);font-size:15px}}
.list{{list-style:none;columns:2;column-gap:36px}}.list li{{break-inside:avoid;display:flex;gap:14px;padding:12px 0;border-bottom:1px solid var(--line)}}
.list small{{display:block;color:var(--muted);font-size:14px}}
details{{border-bottom:1px solid var(--line);padding:18px 0}}summary{{cursor:pointer;font-weight:700;font-size:18px;list-style:none}}summary::after{{content:"+";float:right;color:var(--accent)}}
details[open] summary::after{{content:"–"}}details p{{color:var(--muted);margin-top:8px}}
.final{{text-align:center}}.final .lead{{margin:0 auto 28px}}.nums{{display:flex;justify-content:center;gap:36px;flex-wrap:wrap;margin:26px 0}}
.nums b{{display:block;font-family:var(--ft);font-size:38px;color:var(--accent)}}.nums span{{color:var(--muted);font-size:14px}}
.final .price{{justify-content:center}}.gar{{margin-top:16px;color:var(--muted);font-size:14px}}
footer{{border-top:1px solid var(--line);padding:30px 0;color:var(--muted);font-size:13px}}
@media (max-width:860px){{.hero .wrap,.pane.on{{grid-template-columns:1fr}}.steps{{grid-template-columns:1fr 1fr}}.list{{columns:1}}.sec{{padding:60px 0}}.hero{{padding:36px 0}}}}
@media (max-width:520px){{.steps{{grid-template-columns:1fr}}.btn{{display:block;text-align:center}}}}
{t.get("css_extra", "")}
</style></head><body>
<header class="top"><div class="wrap"><span class="brand">{E(p.get("marca", p["nome"]))}</span>{btn("sm")}</div></header>
<section class="hero"><div class="wrap"><div>
  <p class="kick">{E(h.get("rotulo"))}</p><h1>{E(h["titulo"])}</h1><p class="sub">{E(h.get("subtitulo"))}</p>
  {btn()}<p class="fmt">{E(p.get("formato", "E-book em PDF · acesso imediato"))}</p>{preco_html}
</div><div class="mock">{img(h.get("mockup"), p["nome"])}</div></div></section>
<div class="marq" aria-hidden="true"><div>{marquee} · {marquee}</div></div>
{amostra}
<section class="sec"><div class="wrap"><p class="kick">{E(pd.get("rotulo", "Por dentro"))}</p><h2>{E(pd.get("titulo"))}</h2>
<p class="lead">{E(pd.get("texto"))}</p><div class="steps">{passos}</div></div></section>
<section class="sec"><div class="wrap"><p class="kick">{E(p.get("lista_rotulo", "O conteúdo"))}</p><h2>{E(p.get("lista_titulo"))}</h2>
<ol class="list">{lista}</ol></div></section>
<section class="sec"><div class="wrap" style="max-width:820px"><p class="kick">Dúvidas</p><h2>Antes de comprar.</h2>{faq}</div></section>
<section class="sec final"><div class="wrap"><h2>{E(fim.get("titulo"))}</h2><p class="lead">{E(fim.get("texto"))}</p>
<div class="nums">{nums}</div>{preco_html}<div style="margin-top:22px">{btn()}</div><p class="gar">{E(p.get("garantia", "Garantia de 7 dias: não gostou, devolvemos 100%."))}</p></div></section>
<footer><div class="wrap">© {E(p.get("marca", p["nome"]))} · {E(p.get("rodape"))}</div></footer>
<script>
// repassa utm_*, src, sck, xcod… para o checkout (atribuição de venda por vídeo)
(function(){{var q=new URLSearchParams(location.search),keep=new URLSearchParams();
q.forEach(function(v,k){{if(/^(utm_|src$|sck$|xcod$|ref$|afid$)/.test(k))keep.set(k,v)}});
if([...keep].length)document.querySelectorAll('[data-checkout]').forEach(function(a){{var u=new URL(a.href);keep.forEach(function(v,k){{u.searchParams.set(k,v)}});a.href=u}});}})();
// amostra: abas e pontos
document.querySelectorAll('#amostra').forEach(function(s){{
  var tabs=s.querySelectorAll('[role=tab]'),panes=s.querySelectorAll('.pane');
  function show(k){{tabs.forEach(function(b){{b.setAttribute('aria-selected',b.dataset.t==k)}});panes.forEach(function(p){{p.classList.toggle('on',p.dataset.t==k)}})}}
  tabs.forEach(function(b){{b.onclick=function(){{show(b.dataset.t)}}}});show(0);
  panes.forEach(function(p){{function pick(i){{p.querySelectorAll('[data-i]').forEach(function(e){{e.classList.toggle('on',e.dataset.i==i)}})}}
    p.querySelectorAll('[data-i]').forEach(function(e){{e.onclick=function(){{pick(e.dataset.i)}}}});pick(0)}});
}});
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--shot", action="store_true")
    a = ap.parse_args()
    base = os.path.join(HERE, "produtos", a.slug)
    p = json.load(open(os.path.join(base, "pagina.json"), encoding="utf-8"))
    if not p.get("checkout", {}).get("url") or "[" in p["checkout"]["url"]:
        print("ATENÇÃO: checkout.url ainda não definido; o botão aponta para #.")
        p.setdefault("checkout", {})["url"] = "#"
    site = os.path.join(base, "site")
    os.makedirs(site, exist_ok=True)
    if os.path.isdir(os.path.join(base, "img")):
        shutil.copytree(os.path.join(base, "img"), os.path.join(site, "img"), dirs_exist_ok=True)
    out = os.path.join(site, "index.html")
    open(out, "w", encoding="utf-8").write(build(p))
    print(out)
    if a.shot:
        r = os.path.join(ROOT, "pipeline", "render_html.js")
        subprocess.run(["node", r, out, os.path.join(base, "print-desktop.jpg"), "1366", "900", "full"], check=True)
        subprocess.run(["node", r, out, os.path.join(base, "print-celular.jpg"), "390", "844", "full"], check=True)


if __name__ == "__main__":
    sys.exit(main())
